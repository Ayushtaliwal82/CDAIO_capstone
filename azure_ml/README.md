# Azure ML deployment

The local application is already functional using the bundled Random Forest model.
For the required Azure ML component, deploy the same `engageai_model.joblib` as an
Azure Machine Learning managed online endpoint.

## Suggested Azure ML flow

1. Create an Azure ML workspace.
2. Create/upload the model asset containing `model/engageai_model.joblib`.
3. Create a managed online endpoint.
4. Attach `score.py` as the scoring script.
5. Use `requirements.txt` as the environment dependencies.
6. Test the endpoint with the sample JSON in `sample_request.json`.
7. Copy the endpoint scoring URI and key into the application environment:

AZURE_ML_ENDPOINT=<scoring URI>
AZURE_ML_API_KEY=<endpoint key>

The Streamlit application will automatically use Azure ML when both variables are configured.
If Azure ML is unavailable, the app clearly falls back to the local demo model.
