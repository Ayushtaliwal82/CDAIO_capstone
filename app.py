import os, json, re
from pathlib import Path
import requests
import joblib
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data" / "engageai_students.csv"
MODEL_PATH = BASE / "model" / "engageai_model.joblib"
METRICS_PATH = BASE / "model" / "metrics.json"

st.set_page_config(
    page_title="EngageAI | Smart Classroom",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

def risk_icon(risk):
    return {"High":"🔴", "Moderate":"🟡", "Low":"🟢"}.get(risk, "⚪")

def local_prediction(payload):
    bundle = load_model()
    x = pd.DataFrame([payload])[bundle["features"]]
    pred = bundle["model"].predict(x)[0]
    probs = bundle["model"].predict_proba(x)[0]
    probability = float(max(probs))
    return pred, probability, dict(zip(bundle["classes"], probs))

def azure_prediction(payload):
    endpoint = os.getenv("AZURE_ML_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_ML_API_KEY", "").strip()
    if not endpoint or not api_key:
        return None
    body = {"input_data": {"columns": list(payload.keys()), "data": [[payload[k] for k in payload.keys()]]}}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(endpoint, headers=headers, json=body, timeout=20)
    r.raise_for_status()
    result = r.json()
    # The bundled Azure ML score.py returns a list with one result per input row.
    if isinstance(result, list) and result:
        result = result[0]
    # Support both the project's score.py and common custom endpoint responses.
    if isinstance(result, dict):
        if result.get("error"):
            raise ValueError(result["error"])
        pred = result.get("prediction") or result.get("label")
        probs = result.get("probabilities", {})
        prob = result.get("probability")
        if prob is None:
            prob = result.get("confidence")
        if prob is None and isinstance(probs, dict) and probs:
            prob = max(float(v) for v in probs.values())
        if not pred:
            raise ValueError(f"Azure ML response has no prediction: {result}")
        return pred, float(prob or 0.0), probs
    raise ValueError(f"Unexpected Azure ML response format: {type(result).__name__}")

def predict(payload):
    try:
        azure = azure_prediction(payload)
        if azure:
            return azure, "Azure ML endpoint"
    except Exception as e:
        st.warning(f"Azure ML endpoint unavailable; using local demo model. ({e})")
    return local_prediction(payload), "Local demo model"

def intervention(risk, payload):
    actions = []
    if payload["attendance"] < 70:
        actions.append("Review attendance barriers and arrange a brief faculty follow-up.")
    if payload["class_participation"] < 40:
        actions.append("Use interactive questioning, polls or small-group activities.")
    if payload["quiz_average"] < 60:
        actions.append("Offer targeted academic support or a short revision activity.")
    if payload["assignment_completion"] < 60:
        actions.append("Check assignment difficulties and provide a clear completion plan.")
    if payload["lms_activity"] < 40:
        actions.append("Encourage structured LMS engagement with a short weekly task.")
    if risk == "High":
        return actions[:3] or ["Schedule a faculty check-in and monitor engagement closely."]
    if risk == "Moderate":
        return actions[:2] or ["Monitor engagement over the next two weeks."]
    return ["Continue the current learning strategy and reinforce positive participation."]

def chatbot_answer(q, data):
    ql = q.lower().strip()
    if any(x in ql for x in ["high risk", "high engagement", "who needs attention", "need attention"]):
        n = int((data.engagement_risk=="High").sum())
        names = data.loc[data.engagement_risk=="High","student_name"].head(5).tolist()
        suffix = ", ".join(names) if names else "none in the demo dataset"
        return f"There are {n} students classified as high engagement risk. Examples: {suffix}."
    if "moderate" in ql and ("how many" in ql or "count" in ql):
        n = int((data.engagement_risk=="Moderate").sum())
        return f"There are {n} students classified as moderate engagement risk."
    if "low risk" in ql or "low engagement risk" in ql:
        n = int((data.engagement_risk=="Low").sum())
        return f"There are {n} students classified as low engagement risk."
    if "attendance" in ql and ("75" in ql or "below" in ql):
        n = int((data.attendance < 75).sum())
        return f"{n} students in the demo dataset have attendance below 75%."
    if "average engagement" in ql or "average participation" in ql:
        return f"The class average participation is {data.class_participation.mean():.1f}%, and average attendance is {data.attendance.mean():.1f}%."
    if "intervention" in ql or "what should" in ql or "improve engagement" in ql:
        return "For high-risk students, consider faculty follow-up, interactive classroom activities, targeted academic support and structured LMS tasks. AI output is advisory and requires faculty review."
    m = re.search(r"(?:why is|why does|about)\s+([a-zA-Z ]+?)(?:\s+at|\s+high|\?|$)", ql)
    if m:
        candidate = m.group(1).strip()
        hit = data[data.student_name.str.lower().str.contains(candidate, na=False)]
        if len(hit):
            r = hit.iloc[0]
            factors=[]
            if r.attendance < 70: factors.append("low attendance")
            if r.class_participation < 40: factors.append("low participation")
            if r.lms_activity < 40: factors.append("low LMS activity")
            if r.quiz_average < 60: factors.append("low quiz performance")
            return f"{r.student_name} is currently {r.engagement_risk} risk in the demo data. Key indicators include: {', '.join(factors) if factors else 'no single dominant low indicator'}."
    if "what can engageai" in ql or ql in ["help", "what can you do"]:
        return "I can summarize engagement risk, identify students needing attention, explain key indicators, report attendance/engagement statistics and suggest faculty interventions."
    return "I can answer questions about engagement risk, attendance, participation, student indicators and recommended interventions. Try: 'Who needs attention?'"

def call_dialogflow_webhook(q):
    url = os.getenv("DIALOGFLOW_WEBHOOK_URL","").strip()
    if not url:
        return None
    r = requests.post(url, json={"query": q}, timeout=20)
    r.raise_for_status()
    return r.json().get("fulfillmentText") or r.json().get("answer")

data = load_data()
metrics = json.loads(METRICS_PATH.read_text())

st.markdown("""
<style>
.main-title {font-size: 2.1rem; font-weight: 700; margin-bottom: 0;}
.subtitle {color: #64748b; margin-top: 0;}
.card {padding: 1rem; border-radius: 14px; border: 1px solid #e2e8f0; background: #ffffff;}
.risk-high {padding: 14px; border-radius: 12px; background:#fee2e2; border:1px solid #fecaca;}
.risk-med {padding: 14px; border-radius: 12px; background:#fef3c7; border:1px solid #fde68a;}
.risk-low {padding: 14px; border-radius: 12px; background:#dcfce7; border:1px solid #bbf7d0;}
.small {font-size:.85rem;color:#64748b;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# 🎓 EngageAI")
st.sidebar.caption("Smart Classroom Engagement Assistant")
page = st.sidebar.radio("Navigation", ["Dashboard","Students","Predict Engagement","Analytics","EngageAI Chatbot","Governance"])

st.sidebar.divider()
st.sidebar.caption("Data mode")
st.sidebar.info("Synthetic / demo data")
if os.getenv("AZURE_ML_ENDPOINT"):
    st.sidebar.success("Azure ML endpoint configured")
else:
    st.sidebar.warning("Azure ML: demo/local mode")

if page == "Dashboard":
    st.markdown('<p class="main-title">EngageAI Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Early identification of classroom engagement risk for faculty decision support</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Students", len(data))
    c2.metric("🔴 High Risk", int((data.engagement_risk=="High").sum()))
    c3.metric("🟡 Moderate Risk", int((data.engagement_risk=="Moderate").sum()))
    c4.metric("🟢 Low Risk", int((data.engagement_risk=="Low").sum()))
    st.divider()
    left,right=st.columns([1,1])
    with left:
        st.subheader("Engagement Risk Distribution")
        counts=data.engagement_risk.value_counts().reindex(["High","Moderate","Low"]).fillna(0)
        st.bar_chart(counts)
    with right:
        st.subheader("Classroom Snapshot")
        st.metric("Average Attendance", f"{data.attendance.mean():.1f}%")
        st.metric("Average Participation", f"{data.class_participation.mean():.1f}%")
        st.metric("Average Quiz Score", f"{data.quiz_average.mean():.1f}%")
    st.subheader("Students Requiring Attention")
    high=data[data.engagement_risk=="High"].sort_values("attendance").head(8)
    st.dataframe(high[["student_id","student_name","course","attendance","class_participation","quiz_average","engagement_risk"]], use_container_width=True, hide_index=True)
    st.caption("All results shown here are synthetic/demo results for the prototype.")

elif page == "Students":
    st.title("Student Engagement")
    col1,col2=st.columns(2)
    with col1:
        risk_filter=st.multiselect("Risk level", ["High","Moderate","Low"], default=["High","Moderate","Low"])
    with col2:
        search=st.text_input("Search student")
    view=data[data.engagement_risk.isin(risk_filter)].copy()
    if search:
        view=view[view.student_name.str.contains(search, case=False, na=False)]
    st.dataframe(view[["student_id","student_name","course","attendance","assignment_completion","quiz_average","lms_activity","class_participation","engagement_risk"]], use_container_width=True, hide_index=True)
    st.info("Use Predict Engagement to run an individual model prediction using the same feature set.")

elif page == "Predict Engagement":
    st.title("AI Engagement Prediction")
    st.caption("Prediction can use an Azure ML online endpoint when configured; otherwise the bundled local model is used for demonstration.")
    selected = st.selectbox("Select a demo student", data.student_name.tolist())
    row=data[data.student_name==selected].iloc[0]
    st.subheader(f"Student Profile — {row.student_name}")
    a,b,c,d=st.columns(4)
    a.metric("Attendance", f"{row.attendance:.1f}%")
    b.metric("Participation", f"{row.class_participation:.1f}%")
    c.metric("Quiz Average", f"{row.quiz_average:.1f}%")
    d.metric("LMS Activity", f"{row.lms_activity:.1f}%")
    payload={k:float(row[k]) for k in [
        "attendance","assignment_completion","quiz_average","lms_activity",
        "class_participation","poll_participation","discussion_participation",
        "previous_engagement","missed_classes","avg_response_time_sec"
    ]}
    if st.button("🔮 Predict Engagement", type="primary", use_container_width=True):
        (pred, prob, probs), source = predict(payload)
        st.session_state["last_prediction"]=(pred,prob,probs,payload,source,row.student_name)
    if "last_prediction" in st.session_state:
        pred,prob,probs,payload,source,name=st.session_state["last_prediction"]
        css={"High":"risk-high","Moderate":"risk-med","Low":"risk-low"}[pred]
        st.markdown(f'<div class="{css}"><h2>{risk_icon(pred)} {pred} Engagement Risk</h2><b>Model confidence: {prob:.0%}</b><br><span class="small">Prediction source: {source}</span></div>', unsafe_allow_html=True)
        st.subheader("Recommended Intervention")
        for action in intervention(pred,payload):
            st.write("• "+action)
        st.subheader("Key Indicators")
        indicators={
            "Attendance": payload["attendance"],
            "Assignment Completion": payload["assignment_completion"],
            "Quiz Average": payload["quiz_average"],
            "LMS Activity": payload["lms_activity"],
            "Class Participation": payload["class_participation"]
        }
        st.bar_chart(pd.Series(indicators))
        st.warning("AI output is decision support. Faculty review is required before any academic action.")

elif page == "Analytics":
    st.title("Engagement Analytics")
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Attendance vs Participation")
        st.scatter_chart(data, x="attendance", y="class_participation", color="engagement_risk")
    with c2:
        st.subheader("Quiz Score vs Participation")
        st.scatter_chart(data, x="quiz_average", y="class_participation", color="engagement_risk")
    st.subheader("Model Feature Importance")
    fi=pd.Series(metrics["feature_importance"]).sort_values(ascending=True)
    st.bar_chart(fi)
    st.caption(f"Bundled demo model test accuracy: {metrics['accuracy']:.1%}. For production use, the model must be independently validated on representative institutional data.")

elif page == "EngageAI Chatbot":
    st.title("💬 EngageAI Chatbot")
    st.caption("Conversational support for faculty. Configure DIALOGFLOW_WEBHOOK_URL to route messages to Google Dialogflow.")
    if "chat" not in st.session_state:
        st.session_state.chat=[("assistant","Hello! Ask me about engagement risk, attendance, participation or interventions.")]
    for role,msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)
    q=st.chat_input("Ask: Which students need attention?")
    if q:
        st.session_state.chat.append(("user",q))
        try:
            answer=call_dialogflow_webhook(q) or chatbot_answer(q,data)
        except Exception as e:
            answer=chatbot_answer(q,data)
            st.warning(f"Dialogflow connection failed; local demo assistant answered instead. ({e})")
        st.session_state.chat.append(("assistant",answer))
        st.rerun()

elif page == "Governance":
    st.title("Responsible AI & Enterprise Governance")
    st.subheader("Prototype controls")
    items=[
        ("Data source","Synthetic/demo data only; no confidential institutional records."),
        ("Purpose","Faculty decision support for classroom engagement."),
        ("Transparency","Prediction class and confidence are displayed."),
        ("Human oversight","Faculty review is required before academic action."),
        ("Model traceability","Model metrics and feature importance are shown."),
        ("Data minimization","Only engagement-related demo attributes are used."),
        ("Failure handling","If Azure ML is unavailable, the app clearly falls back to the local demo model."),
        ("Production requirement","Institutional validation, access control, privacy review and monitoring are required before deployment.")
    ]
    for title,desc in items:
        st.markdown(f"**{title}:** {desc}")
    st.divider()
    st.subheader("Production questions")
    st.write("• What institutional data would be required?")
    st.write("• How will false positives and false negatives be monitored?")
    st.write("• Who approves interventions?")
    st.write("• How will student privacy and access control be implemented?")
    st.write("• How will model drift and fairness be monitored?")
