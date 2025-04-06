import pandas as pd
import os
from sklearn.model_selection import train_test_split
from model import train_model
from feature_engineering import build_feature_vector

DATA_PATH = os.path.join("backend", "ml", "data", "training_data.csv")

def preprocess_and_train():
    df = pd.read_csv(DATA_PATH)

    X = df.apply(build_feature_vector, axis=1, result_type="expand")

    y = df["urgency_label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    train_model(X_train, y_train)

if __name__ == "__main__":
    preprocess_and_train()
