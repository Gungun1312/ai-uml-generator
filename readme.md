# AI-Based UML Generator (Human-in-the-loop)

An interactive tool that generates UML class diagrams using AI-extracted data and allows users to refine the diagram before exporting.

## Live Demo
[Open the App](https://your-streamlit-link.streamlit.app)

---

## Features

- Upload extracted UML data in JSON format
- Human-in-the-loop editing of classes and relationships
- Rename classes or remove incorrect ones
- Interactive Streamlit interface
- Automatic PlantUML generation
- Live UML diagram preview
- Download `.puml` UML files

---

## Tech Stack

- Python
- Streamlit
- Pydantic
- PlantUML
- Requests

---

## Project Structure

```
ai-uml-generator
│
├── app.py
├── extracted.json
├── requirements.txt
├── README.md
│
├── src
│   ├── uml_models.py
│   ├── plantuml.py
│   ├── render.py
│   ├── extract.py
│   ├── ingest.py
│   ├── preprocess.py
│   └── nlp.py
```

---

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ai-uml-generator.git
cd ai-uml-generator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

---

## Example Workflow

1. Upload `extracted.json`
2. Review detected classes
3. Rename or remove incorrect classes
4. Review relationships
5. Generate UML diagram
6. Download `.puml` file

---

## Future Improvements

- Generate UML directly from text requirements using AI
- Support sequence diagrams
- Add attribute/method editing
- Export PNG/SVG diagrams

---

## Author

**Gungun Srivastava**
