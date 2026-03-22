# Canberbyte DocFlow AI Platform

Production-style Streamlit platform for converting PDFs into structured workflows, SOPs, and exportable artifacts.

## Architecture
- `app.py`: Main entry and route controller.
- `workflow_pages/`: Workflow views (`login_page.py`, `simplified_flow.py`, plus advanced modules).
- `components/`: Reusable UI widgets and design system.
- `services/`: Auth, PDF parsing, AI workflow generation, export services.
- `utils/`: Config, logging, validators, session state, domain models.
- `tests/`: Basic unit tests for validators, auth, and AI pipeline.
- `docs/`: Product artifacts and deployment guidance.

## Workflow
1. Login / Landing
2. Upload PDF
3. Preview & Validate
4. AI Processing
5. Edit / Review Output
6. Export Results

## Run Locally
```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Test
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Product Artifacts
- `docs/PRODUCT_VISION.md`
- `docs/KPIS.md`
- `docs/PRD.md`
- `docs/BUSINESS_VALUE.md`
- `docs/DEPLOYMENT.md`
