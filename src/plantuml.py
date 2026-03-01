from .uml_models import UMLModel


def to_plantuml(model: UMLModel) -> str:

    lines = [
        "@startuml",
        "skinparam classAttributeIconSize 0",
        "",
    ]

    # Generate classes
    for c in model.classes:

        lines.append(f"class {c.name} {{")

        for a in c.attributes:
            lines.append(f"  +{a}")

        for m in c.methods:
            # Avoid double parentheses
            if m.endswith("()"):
                lines.append(f"  +{m}")
            else:
                lines.append(f"  +{m}()")

        lines.append("}")

        lines.append(f"note right of {c.name}")
        lines.append(f"  confidence: {c.confidence:.2f}")
        lines.append("end note")
        lines.append("")

    # Generate relations
    for r in model.relations:

        if r.type == "association":
            arrow = "-->"
        elif r.type == "aggregation":
            arrow = "o--"
        else:  # inheritance
            arrow = "<|--"

        label = f" : {r.label}" if r.label else ""

        lines.append(f"{r.source} {arrow} {r.target}{label}")

        lines.append("note on link")
        lines.append(f"  confidence: {r.confidence:.2f}")
        lines.append("end note")
        lines.append("")

    lines.append("@enduml")

    return "\n".join(lines)