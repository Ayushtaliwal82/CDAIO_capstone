import os
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
DATA = os.path.join(os.path.dirname(__file__), "..", "data", "engageai_students.csv")
df = pd.read_csv(os.path.abspath(DATA))

def answer(q):
    ql=q.lower()
    if "high risk" in ql or "who needs attention" in ql:
        n=int((df.engagement_risk=="High").sum())
        return f"There are {n} high engagement-risk students in the demo dataset."
    if "moderate" in ql and ("how many" in ql or "count" in ql):
        n=int((df.engagement_risk=="Moderate").sum())
        return f"There are {n} moderate engagement-risk students."
    if "attendance" in ql and ("75" in ql or "below" in ql):
        n=int((df.attendance<75).sum())
        return f"{n} students have attendance below 75%."
    if "average" in ql:
        return f"Average attendance is {df.attendance.mean():.1f}% and average participation is {df.class_participation.mean():.1f}%."
    if "intervention" in ql or "improve engagement" in ql:
        return "Recommended actions include faculty follow-up, interactive activities, targeted academic support and structured LMS tasks. Faculty review is required."
    return "Ask me about high-risk students, attendance, engagement averages or interventions."

@app.post("/dialogflow")
def dialogflow():
    body=request.get_json(silent=True) or {}
    # Supports Dialogflow ES webhook request format and a simple direct {"query": "..."} format.
    q=(body.get("query") or body.get("queryResult",{}).get("queryText") or "").strip()
    response=answer(q)
    # Dialogflow ES response format
    return jsonify({"fulfillmentText": response, "answer": response})

@app.get("/health")
def health():
    return jsonify({"status":"ok"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","8080")))
