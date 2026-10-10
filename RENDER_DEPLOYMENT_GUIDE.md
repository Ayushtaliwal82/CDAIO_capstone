# Deploy EngageAI on Render (public web service)

This package is prepared for Render's **native Python** Web Service. It runs the Streamlit UI with the Render-provided `$PORT`, binds to `0.0.0.0`, pins Python 3.11.11, and pins scikit-learn to the version used by the bundled model.

## Before deployment

- Keep the entire project directory together: `app.py`, `requirements.txt`, `.python-version`, `render.yaml`, `data/`, and `model/`.
- Do not upload only `app.py`; the dataset and `model/engageai_model.joblib` are required.
- Use synthetic/demo data only. Do not upload confidential student records.
- Azure ML and Dialogflow are optional for the first public demo. Without environment variables, the local model and local chatbot fallback run.

## Recommended deployment: GitHub + Render

1. Extract the ZIP.
2. Open the extracted `EngageAI` folder. Confirm that `app.py` and `requirements.txt` are directly inside it.
3. Create a GitHub repository, for example `engageai-smart-classroom`.
4. Upload the *contents* of the `EngageAI` folder to the repository root. The repository root must contain `app.py`, `requirements.txt`, `.python-version`, `render.yaml`, `data/`, and `model/`.
5. In Render, choose **New + → Blueprint** if you want Render to read `render.yaml`, or choose **New + → Web Service** and connect the repository.
6. For a normal Web Service, set:
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
7. Deploy and watch the build/runtime logs.
8. When deployment succeeds, open the public `https://<service-name>.onrender.com` URL.

## If using Render Blueprint

The included `render.yaml` configures:
- Python 3.11.11
- `pip install -r requirements.txt`
- Streamlit bound to `0.0.0.0` on Render's `$PORT`
- Free plan (subject to Render's current limits)

## Optional integrations

Only add these environment variables after the local-mode deployment works:
- `AZURE_ML_ENDPOINT`
- `AZURE_ML_API_KEY`
- `DIALOGFLOW_WEBHOOK_URL`

Set them under Render Dashboard → your service → Environment. Do not hard-code API keys in Python or commit them to GitHub. Save changes and redeploy.

## Compatibility notes

- The serialized model was created with scikit-learn 1.8.0, so the package pins `scikit-learn==1.8.0` to reduce model-version mismatch risk.
- The app's Azure response parser now accepts the list-of-results response emitted by the included Azure `score.py`.
- The current Dialogflow webhook is a separate service. The Streamlit app can call it only when `DIALOGFLOW_WEBHOOK_URL` points to a publicly reachable HTTPS webhook.
- This app has no login/authentication. Anyone who has the public URL can access the demo and its synthetic dataset. Do not use real student data until access control and privacy protections are implemented.
- Render free web services can spin down after inactivity and may take time to wake up. Check Render's current plan limitations before presenting.

## Test after deployment

1. Dashboard opens and shows synthetic/demo data.
2. Students page filters and search work.
3. Predict Engagement returns a risk class and recommendations.
4. Analytics charts load.
5. Chatbot answers using local fallback.
6. Governance page loads.
7. Check Render logs for errors.
