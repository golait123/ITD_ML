import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle


def load_data(csv_path='event_data.csv'):
    """
    Load the event dataset from a CSV file.
    The CSV should have columns: 'description' and 'label'.
    """
    data = pd.read_csv(csv_path)
    return data['description'], data['label']


def train_model():
    # Load the data
    X, y = load_data()

    # Split data into training and testing sets (optional but recommended)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline that first transforms the text with TF-IDF then applies Logistic Regression.
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LogisticRegression(solver='liblinear'))
    ])

    # Train the classifier
    pipeline.fit(X_train, y_train)

    # Evaluate the model
    predictions = pipeline.predict(X_test)
    print("Model Evaluation:\n")
    print(classification_report(y_test, predictions))

    # Save the trained model to disk
    with open('threat_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)

    print("Training complete. Model saved as 'threat_model.pkl'.")


if __name__ == "__main__":
    train_model()
