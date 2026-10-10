from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "engageai_students.csv"
MODEL_DIR = BASE / "model"
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "attendance","assignment_completion","quiz_average","lms_activity",
    "class_participation","poll_participation","discussion_participation",
    "previous_engagement","missed_classes","avg_response_time_sec"
]
TARGET = "engagement_risk"

df = pd.read_csv(DATA)
X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=250, max_depth=8, min_samples_leaf=3,
    random_state=42, class_weight="balanced"
)
model.fit(X_train, y_train)

pred = model.predict(X_test)
proba = model.predict_proba(X_test)
accuracy = accuracy_score(y_test, pred)

print(f"Accuracy: {accuracy:.3f}")
print(classification_report(y_test, pred))
print("Confusion matrix:")
print(confusion_matrix(y_test, pred, labels=model.classes_))

joblib.dump(
    {"model": model, "features": FEATURES, "classes": list(model.classes_)},
    MODEL_DIR / "engageai_model.joblib"
)
print(f"Saved model to {MODEL_DIR/'engageai_model.joblib'}")
