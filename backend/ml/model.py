import xgboost as xgb
import pandas as pd
import numpy as np
import os
import joblib

MODEL_PATH = os.path.join("backend", "ml", "xgb_model.pkl")

# ----------------------------
# TRAINING
# ----------------------------
def train_model(X_train, y_train):
    model = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=42
    )
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")

# ----------------------------
# PREDICTION
# ----------------------------
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model file not found. Please train it first.")
    return joblib.load(MODEL_PATH)

def predict_urgency(features):
    """
    Accepts a single feature dictionary or DataFrame row and returns prediction
    """
    model = load_model()
    df = pd.DataFrame([features])
    prob = model.predict_proba(df)[0][1]
    label = model.predict(df)[0]
    return {"urgency_score": float(prob), "predicted_label": int(label)}
