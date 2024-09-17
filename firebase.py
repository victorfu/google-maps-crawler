import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
from util import log

load_dotenv()


class DataHelper:
    def __init__(self) -> None:
        credPath = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
        log(f"Credentials path: {credPath}")
        cred = credentials.Certificate(credPath)
        bucketName = os.getenv("FIREBASE_BUCKET")
        log(f"Bucket name: {bucketName}")
        firebase_admin.initialize_app(cred, {"storageBucket": bucketName})
        self.db = firestore.client()
        self.bucket = storage.bucket()

    def add_document(self, collection, doc):
        self.db.collection(collection).add(doc)

    def set_document(self, collection, docId, data):
        self.db.collection(collection).document(docId).set(data)

    def update_document(self, collection, docId, data):
        self.db.collection(collection).document(docId).update(data)

    def get_document(self, collection, id):
        ref = self.db.collection(collection).document(id)
        doc = ref.get()
        return doc.to_dict()

    def delete_document(self, collection, id):
        self.db.collection(collection).document(id).delete()

    def query_collection(self, collection):
        docs = self.db.collection(collection).stream()
        return docs
