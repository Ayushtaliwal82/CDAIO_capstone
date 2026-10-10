# Dialogflow ES deployment — EngageAI

Dialogflow ES fulfillment sends an HTTPS POST request to a webhook when an intent
with fulfillment enabled is matched.

## Deploy webhook to Google Cloud Run

From `dialogflow/cloud_run`:

```bash
gcloud auth login
gcloud config set project <GOOGLE_CLOUD_PROJECT_ID>
gcloud run deploy engageai-dialogflow-webhook   --source .   --region asia-south1   --allow-unauthenticated
```

Copy the Cloud Run HTTPS URL and append `/dialogflow`.

## Configure Dialogflow ES

1. Open the Dialogflow ES agent.
2. Open **Fulfillment**.
3. Enable Webhook.
4. Enter the Cloud Run HTTPS URL + `/dialogflow`.
5. Save.
6. Open each EngageAI intent.
7. Under Fulfillment, enable webhook call for that intent.
8. Test in the Dialogflow simulator.

Use the intents in `intents.json`:
- High Risk Students
- Moderate Risk Count
- Attendance Below Threshold
- Class Engagement
- Intervention
- Capabilities

## Connect Streamlit

Set:

`DIALOGFLOW_WEBHOOK_URL=https://<cloud-run-url>/dialogflow`

For production, authenticate the webhook rather than allowing unauthenticated access.
