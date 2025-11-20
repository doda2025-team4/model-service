FROM python:3.12.9-slim

WORKDIR /model-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ ./src/
COPY smsspamcollection/ ./smsspamcollection/

EXPOSE 8081

CMD ["python", "src/serve_model.py"]
