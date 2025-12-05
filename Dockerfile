FROM python:3.12.9-slim

WORKDIR /model-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ ./src/
COPY smsspamcollection/ ./smsspamcollection/


# F10: model directory and volume for models
ENV MODEL_DIR=/models
RUN mkdir -p ${MODEL_DIR}
VOLUME ["/models"]


ENV MODEL_SERVICE_PORT=8081
EXPOSE 8081

CMD ["python", "src/serve_model.py"]
