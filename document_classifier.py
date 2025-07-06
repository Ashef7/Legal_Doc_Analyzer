import pickle
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

MODEL_PATH = 'models/classifier_model.pkl'

def create_and_save_model():
    os.makedirs('models', exist_ok=True)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 3))),
        ('classifier', RandomForestClassifier(n_estimators=200, random_state=42, max_depth=15))
    ])
    X_train = [
        "IN THE SUPREME COURT OF INDIA", "INCOME TAX ACT", "LEASE DEED", "GOVERNMENT OF TAMIL NADU",
        "FAKE DOCUMENT", "UNREGISTERED PROPERTY", "ILLEGAL AGREEMENT", "FORGED CERTIFICATE"
    ]
    y_train = ["legal", "legal", "legal", "legal", "illegal", "illegal", "illegal", "illegal"]
    pipeline.fit(X_train, y_train)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)
    return pipeline

def load_model():
    if not os.path.exists(MODEL_PATH):
        return create_and_save_model()
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except:
        return create_and_save_model()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def check_for_aadhar_format(text):
    return bool(re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text))

def check_for_pan_format(text):
    return bool(re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text, re.IGNORECASE))

def check_for_official_header(text):
    headers = [
        'government of india', 'govt. of india', 'ministry of', 'department of',
        'supreme court', 'high court', 'government of tamil nadu',
        'directorate of government examinations', 'tamil nadu state board'
    ]
    return any(h in text.lower() for h in headers)

def rule_based_classification(text):
    text = text.lower()
    legal_keywords = {
        'supreme court': 3, 'high court': 3, 'civil court': 3, 'judiciary': 2,
        'income tax act': 3, 'contract act': 3, 'companies act': 3,
        'tamil nadu state board': 3, 'government of tamil nadu': 3,
        'hall ticket': 2, 'marksheet': 2, 'subject code': 1, 'pass': 1, 'fail': 1,
        'section': 2, 'notarized': 3, 'registered': 3, 'seal': 2
    }
    illegal_keywords = {
        'fake': 3, 'forged': 3, 'illegal': 3, 'unregistered': 2, 'counterfeit': 3,
        'smuggle': 2, 'black money': 2, 'bribe': 2, 'not valid': 2, 'fabricated': 3
    }
    legal_score = sum(w for k, w in legal_keywords.items() if k in text)
    illegal_score = sum(w for k, w in illegal_keywords.items() if k in text)
    total_score = legal_score + illegal_score

    if legal_score > 0 and illegal_score == 0:
        return "legal", min(legal_score * 10, 95)
    elif illegal_score > 0 and legal_score == 0:
        return "illegal", min(illegal_score * 10, 95)
    elif legal_score >= illegal_score:
        return "legal", 70
    else:
        return "illegal", 70

def classify_document(text):
    if not text or len(text.strip()) < 10:
        return "unknown", 0.0
    text = preprocess_text(text)
    if check_for_aadhar_format(text) or check_for_pan_format(text) or check_for_official_header(text):
        label, confidence = rule_based_classification(text)
    else:
        try:
            model = load_model()
            label = model.predict([text])[0]
            proba = model.predict_proba([text])[0]
            confidence = proba[list(model.classes_).index(label)] * 100
        except:
            label, confidence = rule_based_classification(text)
    return label, confidence
