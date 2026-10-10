# Dialogflow integration

Create a Dialogflow ES agent and add intents based on `intents.json`.

Set the webhook URL to the deployed Flask endpoint:

POST /dialogflow

The webhook accepts both:
- Dialogflow ES requests using `queryResult.queryText`
- Simple requests using `{"query":"..."}`

Then configure the Streamlit application with:

DIALOGFLOW_WEBHOOK_URL=https://<your-host>/dialogflow

Without this variable, EngageAI uses a built-in local demo conversational assistant.
