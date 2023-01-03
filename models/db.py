import firebase_admin
from firebase_admin import credentials, firestore
import os

certs = {
  'type': os.getenv("API_FIREBASE_TYPE"),
  'project_id': os.getenv("API_FIREBASE_PROJECT_ID"),
  'private_key_id': os.getenv("API_FIREBASE_PRIVATE_KEY_ID"),
  'private_key': os.getenv("API_FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
  'client_email': os.getenv("API_FIREBASE_CLIENT_EMAIL"),
  'client_id': os.getenv("API_FIREBASE_CLIENT_ID"),
  'auth_uri': os.getenv("API_FIREBASE_AUTH_URI"),
  'token_uri': os.getenv("API_FIREBASE_TOKEN_URI"),
  'auth_provider_x509_cert_url': os.getenv("API_FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
  'client_x509_cert_url': os.getenv("API_FIREBASE_CLIENT_X509_CERT_URL")
}

cred = credentials.Certificate(certs)
firebase_admin.initialize_app(cred)
db = firestore.client()