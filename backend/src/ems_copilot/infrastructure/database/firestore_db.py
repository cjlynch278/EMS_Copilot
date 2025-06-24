import os
import firebase_admin
from firebase_admin import credentials, firestore

# Global flag to track if Firebase has been initialized
_firebase_initialized = False

class FirestoreDB:
    def __init__(self, credentials_path):
        """
        Initialize FirestoreDB with the given credentials.
        """
        self.credentials_path = credentials_path
        self._initialize_firestore()

    def _initialize_firestore(self):
        """
        Initialize the Firestore client.
        """
        global _firebase_initialized
        
        if not _firebase_initialized:
            try:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                _firebase_initialized = True
                print("Firebase Admin SDK initialized successfully")
            except Exception as e:
                if "already initialized" in str(e).lower():
                    print("Firebase Admin SDK already initialized")
                    _firebase_initialized = True
                else:
                    raise e
        else:
            print("Firebase Admin SDK already initialized")
        
        self.db = firestore.client()

    def write_vitals(self, collection_name, vitals_data):
        """
        Write vitals data to Firestore.
        """
        try:
            print("writing to collection: ", collection_name)
            doc_ref = self.db.collection(collection_name).document()
            doc_ref.set(vitals_data)
            print(f"Vitals for patient {vitals_data['patient_name']} written successfully.")
        except Exception as e:
            raise Exception(f"Failed to write vitals to Firestore: {e}")

    def write_note(self, collection_name, note_data):
        """
        Write a patient note to Firestore.
        """
        try:
            print("writing note to collection: ", collection_name)
            doc_ref = self.db.collection(collection_name).document()
            doc_ref.set(note_data)
            print(f"Note for patient {note_data['patient_name']} written successfully.")
        except Exception as e:
            raise Exception(f"Failed to write note to Firestore: {e}")

    def get_vitals(self, collection_name, patient_id):
        """
        Retrieve vitals data for a specific patient from Firestore.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(patient_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            raise Exception(f"Failed to retrieve vitals from Firestore: {e}")

    def get_vitals_by_patient_name(self, collection_name, patient_name):
        """
        Retrieve vitals data for a specific patient from Firestore.
        """
        try:
            docs = self.db.collection(collection_name).where('patient_name', '==', patient_name).stream()
            vitals_data = []
            for doc in docs:
                vitals_data.append(doc.to_dict())
            return vitals_data
        except Exception as e:
            raise Exception(f"Failed to retrieve vitals from Firestore: {e}")

    def get_notes_by_patient_name(self, collection_name, patient_name):
        """
        Retrieve notes for a specific patient from Firestore.
        """
        try:
            docs = self.db.collection(collection_name).where('patient_name', '==', patient_name).stream()
            notes_data = []
            for doc in docs:
                notes_data.append(doc.to_dict())
            return notes_data
        except Exception as e:
            raise Exception(f"Failed to retrieve notes from Firestore: {e}")