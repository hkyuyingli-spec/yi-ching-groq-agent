import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, List

def init_firebase():
    """Initializes Firebase Admin SDK"""
    if not firebase_admin._apps:
        # In a real app, you'd use a service account JSON or environment variables
        # For this prototype, we'll try to load from environment or a placeholder path
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for local development if creds are not provided
            # This might fail if not in a GCP environment with default credentials
            try:
                firebase_admin.initialize_app()
            except Exception:
                print("⚠️ Firebase credentials not found. Firestore will be unavailable.")

def get_db():
    """Returns Firestore client"""
    try:
        return firestore.client()
    except Exception:
        return None

def save_reading(reading_data: Dict[str, Any]):
    """Saves a reading to the 'readings' collection"""
    db = get_db()
    if db:
        db.collection("readings").add(reading_data)

def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Retrieves user profile from 'user_profiles' collection"""
    db = get_db()
    if db:
        doc = db.collection("user_profiles").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
    return {"hexagram_weights": {}}

def update_user_profile_weights(user_id: str, weights: Dict[str, float]):
    """Updates hexagram weights in user profile"""
    db = get_db()
    if db:
        db.collection("user_profiles").document(user_id).set(
            {"hexagram_weights": weights}, merge=True
        )

def save_feedback(reading_id: str, feedback_data: Dict[str, Any]):
    """Saves feedback linked to a reading_id"""
    db = get_db()
    if db:
        db.collection("feedback").document(reading_id).set(feedback_data)

def get_reading_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves the latest readings for a user"""
    db = get_db()
    if db:
        docs = db.collection("readings")\
                 .where("user_id", "==", user_id)\
                 .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                 .limit(limit)\
                 .stream()
        return [doc.to_dict() for doc in docs]
    return []
