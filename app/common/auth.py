import jwt
import os
import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Secret Key & Algorithm
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Define OAuth2 Security Scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: int = 60):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to verify JWT token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Decoded token (user details)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
