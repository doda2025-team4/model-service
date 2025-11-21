"""
Flask API of the SMS Spam detection model model.
"""
import os
from pathlib import Path

import joblib
import requests
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd

from text_preprocessing import prepare, _extract_message_len, _text_process

MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models"))
MODEL_FILE = os.getenv("MODEL_FILE", "model.joblib")


def ensure_model_present(filename: str, url_env_var: str) -> Path:
    path = MODEL_DIR / filename

    if path.exists():
        print(f"[model-service] Using existing model file: {path}")
        return path

    url = os.getenv(url_env_var)
    if not url:
        raise RuntimeError(
            f"{url_env_var} is not set and model file {path} does not exist. "
            "Either mount a volume with the model or configure a download URL."
        )

    print(f"[model-service] Downloading model file from {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(response.content)

    print(f"[model-service] Download complete: {path}")
    return path


MODEL_PATH = ensure_model_present(MODEL_FILE, "MODEL_URL")
MODEL = joblib.load(MODEL_PATH)

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """
    input_data = request.get_json()
    sms = input_data.get('sms')
    processed_sms = prepare(sms)
    prediction = MODEL.predict(processed_sms)[0]

    res = {
        "result": prediction,
        "classifier": "decision tree",
        "sms": sms
    }
    print(res)
    return jsonify(res)


if __name__ == '__main__':
    port = os.environ.get("MODEL_SERVICE_PORT", "8080")
    app.run(host="0.0.0.0", port=int(port), debug=True)
