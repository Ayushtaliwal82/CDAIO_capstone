# EngageAI — Smart Classroom Engagement Prediction & Intervention Platform

## What this prototype does

EngageAI is a working faculty-facing web application for the Group 2 Smart Classroom
AI Challenge. It uses synthetic classroom data to predict engagement risk and turn
the prediction into an actionable faculty recommendation.

The prototype contains:
- Streamlit vibe-coded web application
- Synthetic 500-student dataset
- Random Forest engagement-risk model
- Azure ML-ready scoring endpoint
- Dialogflow-ready webhook and intent design
- Analytics dashboard
- Responsible AI / governance page
- Human-in-the-loop intervention language

## Run locally

Python 3.10/3.11 recommended.

```bash
pip install -r requirements.txt
streamlit run app.py
```

The bundled model is already included, so the application works immediately.

## Retrain model

```bash
python train_model.py
```

## Azure ML

See `azure_ml/README.md`.
Set:

```text
AZURE_ML_ENDPOINT=<your endpoint scoring URI>
AZURE_ML_API_KEY=<your endpoint key>
```

The application then sends prediction requests to Azure ML. If the endpoint fails,
the application explicitly falls back to the local demo model.

## Dialogflow

See `dialogflow/README.md`.

Deploy `dialogflow/webhook.py`, configure Dialogflow ES webhook integration, and set:

```text
DIALOGFLOW_WEBHOOK_URL=https://<host>/dialogflow
```

The Chatbot page will then attempt Dialogflow first and use the local assistant only
if the Dialogflow endpoint is not configured/available.

## Demo credentials

No login is required in this prototype. For the presentation, label the data as
synthetic/demo data. Production deployment should add institutional authentication,
authorization and audit logging.

## Suggested 10-minute live demo

1. Open Dashboard.
2. Show 500 synthetic students and the High/Moderate/Low distribution.
3. Open Predict Engagement.
4. Select a high-risk student.
5. Click Predict Engagement.
6. Show the prediction confidence and intervention recommendation.
7. Explain that Azure ML supplies the production prediction when configured.
8. Open EngageAI Chatbot and ask: "Who needs attention?"
9. Ask: "What intervention should I use?"
10. Open Governance and explain synthetic data, transparency and human review.

## Production questions to prepare for

- What data would the institution provide?
- How would false positives/negatives be handled?
- Who approves interventions?
- How is student privacy protected?
- How is model drift monitored?
- How is the model validated across courses and cohorts?
