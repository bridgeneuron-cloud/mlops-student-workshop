FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -U pip && pip install -r /app/requirements.txt

COPY src /app/src

# Artifacts must exist in the build context (built by the pipeline prior to docker build)
COPY artifacts /app/artifacts

EXPOSE 8000

CMD ["python", "-m", "src.app", "--artifacts", "/app/artifacts", "--port", "8000"]

