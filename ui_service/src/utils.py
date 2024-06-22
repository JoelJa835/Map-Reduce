import requests
import os
from typing import Optional

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

def validate_token(token: str) -> Optional[dict]:
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/user-role", params={"token": token})
        response.raise_for_status()
        user_role = response.json()
        return {"role": user_role}
    except requests.RequestException as e:
        print(f"Token validation failed: {e}")
        return None