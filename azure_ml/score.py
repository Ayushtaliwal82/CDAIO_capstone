import json
import os
import joblib
import pandas as pd

def init():
    global model_bundle
    model_dir = os.getenv("AZUREML_MODEL_DIR", ".")
    # Azure ML model asset should contain engageai_model.joblib
    candidates = [
        os.path.join(model_dir, "engageai_model.joblib"),
        os.path.join(model_dir, "model", "engageai_model.joblib")
    ]
    path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    model_bundle = joblib.load(path)

def run(raw_data):
    try:
        data = raw_data
        if isinstance(data, str):
            data = json.loads(data)
        if "input_data" in data:
            data = data["input_data"]
        if isinstance(data, dict) and "data" in data:
            columns = data.get("columns", model_bundle["features"])
            values = data["data"]
            df = pd.DataFrame(values, columns=columns)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported input format")

        x = df[model_bundle["features"]]
        preds = model_bundle["model"].predict(x).tolist()
        probs = model_bundle["model"].predict_proba(x).tolist()
        classes = model_bundle["classes"]
        results=[]
        for p, pr in zip(preds, probs):
            results.append({
                "prediction": p,
                "probability": max(pr),
                "probabilities": dict(zip(classes, pr))
            })
        return results
    except Exception as e:
        return {"error": str(e)}
