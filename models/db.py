import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

firebase_type = os.getenv("API_FIREBASE_TYPE")
project_id = os.getenv("API_FIREBASE_PROJECT_ID")
private_key_id = os.getenv("API_FIREBASE_PRIVATE_KEY_ID")
private_key = os.getenv("API_FIREBASE_PRIVATE_KEY")
if isinstance(private_key, str):
  private_key = private_key.replace('\\n', '\n')
else:
  print("API_FIREBASE_PRIVATE_KEY is empty!")
client_email = os.getenv("API_FIREBASE_CLIENT_EMAIL")
client_id = os.getenv("API_FIREBASE_CLIENT_ID")
auth_uri = os.getenv("API_FIREBASE_AUTH_URI")
token_uri = os.getenv("API_FIREBASE_TOKEN_URI")
auth_provider_x509_cert_url = os.getenv("API_FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
client_x509_cert_url = os.getenv("API_FIREBASE_CLIENT_X509_CERT_URL")

certs = {
  'type': firebase_type,
  'project_id': project_id,
  'private_key_id': private_key_id,
  'private_key': private_key,
  'client_email': client_email,
  'client_id': client_id,
  'auth_uri': auth_uri,
  'token_uri': token_uri,
  'auth_provider_x509_cert_url': auth_provider_x509_cert_url,
  'client_x509_cert_url': client_x509_cert_url
}

print(f"Current Certs: {certs}")
cred = credentials.Certificate(certs)
firebase_admin.initialize_app(cred)
db = firestore.client()
