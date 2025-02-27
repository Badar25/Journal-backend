import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
import base64
import json

security = HTTPBearer()

# Decode base64 credentials
creds_json = base64.b64decode(settings.firebase_credentials_base64).decode("utf-8")
creds_dict = json.loads(creds_json)
cred = credentials.Certificate(creds_dict)

# Initialize Firebase
firebase_admin.initialize_app(cred)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )