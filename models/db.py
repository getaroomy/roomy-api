import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name: str) -> str:
  env_var = os.getenv(name)
  if env_var == None:
    print(f"Environment variable '{name}' is empty")
    return ''
  return env_var

firebase_type = get_env("API_FIREBASE_TYPE")
project_id = get_env("API_FIREBASE_PROJECT_ID")
private_key_id = get_env("API_FIREBASE_PRIVATE_KEY_ID")
private_key = get_env("API_FIREBASE_PRIVATE_KEY").replace('\\n', '\n')
client_email = get_env("API_FIREBASE_CLIENT_EMAIL")
client_id = get_env("API_FIREBASE_CLIENT_ID")
auth_uri = get_env("API_FIREBASE_AUTH_URI")
token_uri = get_env("API_FIREBASE_TOKEN_URI")
auth_provider_x509_cert_url = get_env("API_FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
client_x509_cert_url = get_env("API_FIREBASE_CLIENT_X509_CERT_URL")

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
