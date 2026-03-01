import re
from typing import List, Dict
from pathlib import Path
import docx
import spacy

# ---------- DOCX ingest ----------
def read_docx_blocks(path: str) -> List[Dict[str, str]]:
    d = docx.Document(path)
    blocks = []
    for p in d.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue
        style = (p.style.name or "").lower()

        if "heading" in style:
            blocks.append({"type": "heading", "text": text})
        elif p._p.pPr is not None and p._p.pPr.numPr is not None:
            blocks.append({"type": "list", "text": text})
        else:
            blocks.append({"type": "para", "text": text})
    return blocks

# ---------- Use case extraction ----------
ROLE_HINTS = {"user", "users", "admin", "customer", "manager", "operator", "student", "teacher", "staff"}

def normalize_actor(a: str) -> str:
    a = a.strip().lower()
    if a in ("users", "user"):
        return "User"
    return a.capitalize()

def extract_usecases(blocks, nlp):
    usecases = []
    current_uc = None

    for b in blocks:
        t = b["text"].strip()
        low = t.lower()

        # Start new UC from "shall" requirement
        if " shall " in f" {low} ":
            m = re.search(r"(?i)shall\s+(.*)", t)
            name = (m.group(1).strip() if m else t).rstrip(".")
            current_uc = {
                "name": name,
                "actors": set(),
                "steps": [],
                "confidence": 0.60
            }

            # Guess actors from keywords + noun chunks
            doc = nlp(t)
            for tok in doc:
                if tok.text.lower() in ROLE_HINTS:
                    current_uc["actors"].add(normalize_actor(tok.text))

            usecases.append(current_uc)
            continue

        # If we already have a current use case, treat following lines as steps
        if current_uc is not None:
            is_step = (b["type"] in ("list", "para")) and (
                low.startswith("the user") or low.startswith("user") or
                low.startswith("the system") or low.startswith("system")
            )
            if is_step:
                current_uc["steps"].append(t)
                current_uc["confidence"] = min(1.0, current_uc["confidence"] + 0.05)

                # actor enrichment from step text
                doc = nlp(t)
                for tok in doc:
                    if tok.text.lower() in ROLE_HINTS:
                        current_uc["actors"].add(normalize_actor(tok.text))

    # finalize (convert sets to lists)
    for uc in usecases:
        uc["actors"] = sorted(list(uc["actors"])) or ["User"]
    return usecases

# ---------- Sequence extraction ----------
def extract_sequences(usecases):
    seqs = []
    for uc in usecases:
        if not uc["steps"]:
            continue

        participants = set(["System"] + uc["actors"])
        messages = []

        default_actor = uc["actors"][0] if uc["actors"] else "User"

        for step in uc["steps"]:
            s = re.sub(r"^\s*\d+[\).\-\:]\s*", "", step).strip()
            slow = s.lower()

            if slow.startswith("the system") or slow.startswith("system"):
                messages.append({"from": "System", "to": "System", "text": s})
            elif slow.startswith("the user") or slow.startswith("user"):
                messages.append({"from": default_actor, "to": "System", "text": s})
            else:
                messages.append({"from": default_actor, "to": "System", "text": s})

        seqs.append({
            "name": uc["name"],
            "participants": sorted(participants),
            "messages": messages,
            "confidence": min(1.0, 0.55 + 0.02 * len(messages))
        })
    return seqs

# ---------- PlantUML ----------
def usecase_to_plantuml(usecases):
    lines = ["@startuml", "left to right direction", ""]
    lines.append("rectangle System {")
    for i, uc in enumerate(usecases, 1):
        lines.append(f'  usecase "UC{i}: {uc["name"]}" as UC{i}')
        lines.append(f"  ' confidence: {uc['confidence']:.2f}")
    lines.append("}")
    lines.append("")

    actor_ids = {}
    aid = 1
    for i, uc in enumerate(usecases, 1):
        for a in uc["actors"]:
            if a not in actor_ids:
                actor_ids[a] = f"A{aid}"
                lines.append(f'actor "{a}" as {actor_ids[a]}')
                aid += 1
            lines.append(f"{actor_ids[a]} --> UC{i}")

    lines.append("\n@enduml")
    return "\n".join(lines)

def sequences_to_plantuml(seqs):
    out = []
    for seq in seqs:
        lines = ["@startuml", f"title {seq['name']}", ""]
        for p in seq["participants"]:
            lines.append(f"participant {p}")
        lines.append("")
        for m in seq["messages"]:
            lines.append(f'{m["from"]} -> {m["to"]}: {m["text"]}')
        lines.append(f"\n' confidence: {seq['confidence']:.2f}")
        lines.append("@enduml\n")
        out.append("\n".join(lines))
    return "\n".join(out)

# ---------- main ----------
def main():
    nlp = spacy.load("en_core_web_sm")

    blocks = read_docx_blocks("data/srs.docx")
    usecases = extract_usecases(blocks, nlp)
    seqs = extract_sequences(usecases)

    Path("output").mkdir(exist_ok=True)
    Path("output/usecase.puml").write_text(usecase_to_plantuml(usecases), encoding="utf-8")
    Path("output/sequences.puml").write_text(sequences_to_plantuml(seqs), encoding="utf-8")

    print("Generated:")
    print(" - output/usecase.puml")
    print(" - output/sequences.puml")

if __name__ == "__main__":
    main()