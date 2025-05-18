import firebase_admin
from firebase_admin import credentials, firestore

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
        cred = credentials.Certificate(self.credentials_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def write_vitals(self, collection_name, vitals_data):
        """
        Write vitals data to Firestore.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(vitals_data["patient_id"])
            doc_ref.set(vitals_data)
            print(f"Vitals for patient {vitals_data['patient_id']} written successfully.")
        except Exception as e:
            raise Exception(f"Failed to write vitals to Firestore: {e}")

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