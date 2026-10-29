# DeepLearning.AI — Agentic AI course labs

My working copies of the labs from the DeepLearning.AI **Agentic AI** course, organised by module / design pattern.

## Layout

```
labs/
├── module-2-reflection/
│   └── ugl-1-chart-generation/          M2_UGL_1  — reflect on a rendered chart and regenerate it
├── module-3-tool-use/
│   ├── ugl-1-functions-to-tools/        M3_UGL_1  — turning Python functions into LLM tools (aisuite)
│   ├── ugl-2-email-assistant/           M3_UGL_2  — email agent over a simulated FastAPI email service
│   └── graded-research-agent/           C1M3      — graded: tool use → reflection → HTML report
├── module-4-evaluations/
│   └── ugl-1-component-eval/            M4_UGL_1  — component-level eval of the research step
└── module-5-planning/
    └── ugl-1-customer-service-agent/    M5_UGL_1  — planning with code execution over TinyDB
```

Each lab folder is **self-contained**: the notebook imports its helpers (`utils`, `research_tools`, …) by
bare name and reads its images/data by relative path, so run every notebook with its own folder as the
working directory (the Jupyter default). Small helpers are deliberately duplicated across folders
(`display_functions.py`, `research_tools.py`, `utils.print_html`) — if you fix one, fix its copies too.

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in the API keys the lab needs
jupyter notebook
```

## Not included

The graded lab (`C1M3_Assignment.ipynb`) depends on the course's `unittests.py` and `images/` folder, which only
exist on the course platform; the test cells will fail locally.
