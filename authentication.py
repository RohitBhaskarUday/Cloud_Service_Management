from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from database import get_db
from motor.motor_asyncio import AsyncIOMotorClient
from model import User
from bson import ObjectId

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
  

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception
      
async def authenticate_user(username: str, password: str, db: AsyncIOMotorClient = Depends(get_db)):
    user = await db.User.find_one({"username": username, "password": password})
    if user:
        # Generate JWT token upon successful authentication
        token_data = {"sub": str(user["_id"]), "username": user["username"], "is_admin": user.get("isAdmin", False)}
        token = create_jwt_token(token_data)
        return token
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
      
      
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorClient = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.User.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    
    return User(**user)
  
  
async def get_subscription_plan_by_id(plan_id: int, db: AsyncIOMotorClient = Depends(get_db)):
    return await db.SubscriptionPlans.find_one({"plan_id": plan_id})

async def get_permission_by_id(permission_id: str, db: AsyncIOMotorClient = Depends(get_db)):
    return await db.Permissions.find_one({"permission_id": permission_id})