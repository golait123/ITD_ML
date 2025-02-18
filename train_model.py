# train_model.py
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

EVENT_LOG = "event_data.csv"
MODEL_FILE = "threat_model.pkl"


def train_model():
    """Train a machine learning model for USB threat detection using the event log."""
    try:
        df = pd.read_csv(EVENT_LOG)
    except FileNotFoundError:
        print("Error: event_data.csv not found. Ensure USB events are being logged before training the model.")
        return

    # Label 'inserted' events as threat (1) and 'removed' events as safe (0)
    df['threat'] = df['event_type'].apply(lambda x: 1 if x == "inserted" else 0)

    # Use the 'device' field as the feature.
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['device'].astype(str))
    y = df['threat']

    # Optionally split data (here we use 80% training and 20% testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    with open(MODEL_FILE, 'wb') as f:
        pickle.dump((vectorizer, model), f)

    print("Threat detection model trained and saved successfully as", MODEL_FILE)


if __name__ == "__main__":
    train_model()
