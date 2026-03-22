# Deployment Instructions

## Local Setup
1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create env file:
   ```bash
   cp .env.example .env
   ```
4. Launch app:
   ```bash
   streamlit run app.py
   ```

## Docker Deployment
1. Build image:
   ```bash
   docker build -t canberbyte-docflow-ai .
   ```
2. Run container:
   ```bash
   docker run --rm -p 8501:8501 --env-file .env canberbyte-docflow-ai
   ```
3. Open:
   - http://localhost:8501

## Production Notes
- Replace local auth with enterprise SSO provider for production.
- Store secrets in a secure vault.
- Route logs to centralized observability (CloudWatch, ELK, Datadog).
- Add CI/CD checks for tests, linting, and security scanning.
