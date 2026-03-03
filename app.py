import streamlit as st
from src.uml_models import UMLModel, UMLClass, UMLRelation
from src.plantuml import to_plantuml
from src.render import plantuml_url

st.title("AI-Based UML Generator (Human-in-the-loop)")

import json

# ---------------- SAMPLE INPUT DOWNLOAD ----------------

sample_data = {
  "classes": [
    {
      "name": "Patient",
      "attributes": ["patientId", "name", "age", "medicalHistory"],
      "methods": ["bookAppointment()", "viewReport()"],
      "confidence": 0.96
    },
    {
      "name": "Doctor",
      "attributes": ["doctorId", "name", "specialization"],
      "methods": ["diagnose()", "prescribeMedicine()"],
      "confidence": 0.93
    },
    {
      "name": "Appointment",
      "attributes": ["appointmentId", "date", "time", "status"],
      "methods": ["schedule()", "cancel()"],
      "confidence": 0.90
    }
  ],
  "relations": [
    {
      "source": "Patient",
      "target": "Appointment",
      "type": "association",
      "label": "books",
      "confidence": 0.95
    },
    {
      "source": "Doctor",
      "target": "Appointment",
      "type": "association",
      "label": "attends",
      "confidence": 0.92
    }
  ]
}

sample_json = json.dumps(sample_data, indent=4)

st.download_button(
    label="📥 Download Sample extracted.json",
    data=sample_json,
    file_name="extracted.json",
    mime="application/json"
)

uploaded = st.file_uploader(
    "Upload extracted.json (from pipeline)", type=["json"]
)

if uploaded:

    # Read file safely
    raw = uploaded.getvalue().decode("utf-8")

    if not raw.strip():
        st.error("Uploaded JSON file is empty.")
        st.stop()

    # Validate JSON
    try:
        model = UMLModel.model_validate_json(raw)
    except Exception as e:
        st.error(f"Invalid JSON format: {e}")
        st.code(raw)
        st.stop()

    # ---------------- CLASSES ----------------
    st.subheader("Classes")

    updated_classes = []

    for c in model.classes:
        col1, col2, col3 = st.columns([3, 2, 2])

        keep = col1.checkbox(
            f"Keep {c.name}", value=True, key=f"keep_{c.name}"
        )

        new_name = col2.text_input(
            "Rename", value=c.name, key=f"rename_{c.name}"
        )

        col3.write(f"confidence: {c.confidence:.2f}")

        if keep:
            updated_classes.append(
                UMLClass(
                    name=new_name,
                    attributes=c.attributes,
                    methods=c.methods,
                    confidence=c.confidence,
                )
            )

    # ---------------- RELATIONS ----------------
    st.subheader("Relations")

    updated_rel = []

    for i, r in enumerate(model.relations):

        keep = st.checkbox(
            f"Keep {r.source} ({r.type}) {r.target}",
            value=True,
            key=f"rel_{i}",
        )

        if keep:
            updated_rel.append(r)

    # Remove relations pointing to removed classes
    class_names = {c.name for c in updated_classes}

    filtered_rel = [
        r for r in updated_rel
        if r.source in class_names and r.target in class_names
    ]

    # Create updated model
    new_model = UMLModel(
        classes=updated_classes,
        relations=filtered_rel,
    )

    # ---------------- PLANTUML ----------------
    st.subheader("Generated PlantUML")

    puml = to_plantuml(new_model)

    st.code(puml, language="text")

    # ---------------- DIAGRAM PREVIEW ----------------
    st.subheader("UML Diagram Preview")

    url = plantuml_url(puml)

    st.image(url)

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "Download diagram.puml",
        data=puml,
        file_name="diagram.puml",
    )