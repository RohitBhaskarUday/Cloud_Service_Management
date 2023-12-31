from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional

class SubscriptionPlan(BaseModel):
    _id: ObjectId
    plan_id: int
    plan: str
    description: str
    api_permissions: List[str]
    usagelimit: int


       

class Permission(BaseModel):
    _id: ObjectId
    permission_id:int
    name: str
    api_endpoint:str
    description: str
    
    
class User(BaseModel):
    _id: ObjectId
    username:str
    password:str
    isAdmin: bool = False  # Add default value
    subscription_plan: dict= {}  # Add default value
    permissions: List[Permission]=[]
    usage: int = 0  # Add default value 
    limit: int = 0
    permissions: List[str] = []
    

class Token(BaseModel):
    access_token: str
    token_type: str
    

   
   
        

    
  