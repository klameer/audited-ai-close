FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY datasets/ datasets/

# Cloud Run injects PORT; DEMO_API_KEY (or DEMO_API_KEY_<DATASET>) set as service env vars
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
