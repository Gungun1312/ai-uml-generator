import json
from pathlib import Path
from src.ingest import load_srs
from src.preprocess import preprocess_text
from src.nlp import load_nlp
from src.extract import build_model
from src.plantuml import to_plantuml

def run(input_path: str):
    text = load_srs(input_path)
    text = preprocess_text(text)

    nlp = load_nlp()
    doc = nlp(text)

    model = build_model(doc)

    Path("output").mkdir(exist_ok=True)
    Path("output/extracted.json").write_text(model.model_dump_json(indent=2), encoding="utf-8")
    Path("output/diagram.puml").write_text(to_plantuml(model), encoding="utf-8")

    print("Saved:")
    print(" - output/extracted.json")
    print(" - output/diagram.puml")

if __name__ == "__main__":
    run("data/sample_srs.txt")