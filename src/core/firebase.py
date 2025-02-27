import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
from ..models.response import APIResponse
from .logger import logger
import base64
import json

security = HTTPBearer()

try:
    # Decode base64 credentials
    creds_json = base64.b64decode(settings.firebase_credentials_base64).decode("utf-8")
    creds_dict = json.loads(creds_json)
    cred = credentials.Certificate(creds_dict)

    # Initialize Firebase
    firebase_admin.initialize_app(cred)
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    raise RuntimeError(f"Firebase initialization failed: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except auth.ExpiredIdTokenError:
        logger.warning("Expired authentication token")
        return APIResponse.error_response(
            error="TOKEN_EXPIRED",
            message="Authentication token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except auth.RevokedIdTokenError:
        logger.warning("Revoked authentication token")
        return APIResponse.error_response(
            error="TOKEN_REVOKED",
            message="Authentication token has been revoked",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except auth.InvalidIdTokenError:
        logger.warning("Invalid authentication token")
        return APIResponse.error_response(
            error="TOKEN_INVALID",
            message="Invalid authentication token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return APIResponse.error_response(
            error="AUTH_ERROR",
            message="Authentication failed",
            status_code=status.HTTP_401_UNAUTHORIZED
        )