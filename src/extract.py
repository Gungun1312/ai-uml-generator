from collections import Counter
from typing import Tuple
from .uml_models import UMLModel, UMLClass, UMLRelation

INHERIT_PATTERNS = ["is a", "is an", "inherits", "extends"]
AGG_PATTERNS = ["has a", "has an", "contains", "consists of", "includes", "composed of"]
ASSOC_PATTERNS = ["uses", "accesses", "updates", "reads", "writes", "interacts with", "communicates with"]

def normalize_class_name(s: str) -> str:
    # Convert to TitleCase-ish class name
    s = s.strip()
    s = " ".join(w.capitalize() for w in s.split())
    return s.replace(" ", "")

def extract_candidates(doc, min_freq=2):
    noun_chunks = []
    for nc in doc.noun_chunks:
        phrase = nc.text.lower().strip()
        # Filter weak chunks
        if len(phrase) < 3:
            continue
        if any(ch.isdigit() for ch in phrase):
            continue
        noun_chunks.append(phrase)

    freq = Counter(noun_chunks)
    candidates = [k for k, v in freq.items() if v >= min_freq]
    return candidates, freq

def extract_relations_from_sentence(sent_text: str, class_names: list) -> list:
    s = sent_text.lower()
    rels = []

    # Try to find two class mentions in the sentence
    mentions = [cn for cn in class_names if cn.lower() in s]
    mentions = list(dict.fromkeys(mentions))  # unique preserving order
    if len(mentions) < 2:
        return rels

    # naive pair selection: first two mentions
    a, b = mentions[0], mentions[1]

    # Inheritance
    if any(p in s for p in INHERIT_PATTERNS):
        rels.append(("inheritance", a, b))
        return rels

    # Aggregation
    if any(p in s for p in AGG_PATTERNS):
        rels.append(("aggregation", a, b))
        return rels

    # Association
    if any(p in s for p in ASSOC_PATTERNS):
        rels.append(("association", a, b))
        return rels

    return rels

def build_model(doc) -> UMLModel:
    candidates, freq = extract_candidates(doc, min_freq=2)
    class_names = [normalize_class_name(c) for c in candidates]

    # Classes with confidence based on frequency (simple heuristic)
    maxf = max(freq.values()) if freq else 1
    classes = []
    for c in candidates:
        name = normalize_class_name(c)
        conf = min(1.0, freq[c] / maxf)
        classes.append(UMLClass(name=name, confidence=conf))

    relations = []
    for sent in doc.sents:
        rels = extract_relations_from_sentence(sent.text, class_names)
        for rtype, src, tgt in rels:
            # simple confidence: higher if sentence contains strong keywords
            base = 0.65 if rtype in ("inheritance", "aggregation") else 0.55
            relations.append(UMLRelation(
                source=src,
                target=tgt,
                type=rtype,
                label=None,
                confidence=base
            ))

    # Deduplicate relations
    uniq = {}
    for r in relations:
        key = (r.source, r.target, r.type)
        if key not in uniq or uniq[key].confidence < r.confidence:
            uniq[key] = r

    return UMLModel(classes=classes, relations=list(uniq.values()))