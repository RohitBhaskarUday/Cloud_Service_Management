from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

#db
from database import get_db
from model import User, SubscriptionPlan, Permission, Token
#authenticate
from authentication import create_jwt_token, get_current_user, verify_token


app = FastAPI()


SECRET_KEY = "2000$"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.get("/", response_class=HTMLResponse)  #index start page if we run the application 
async def index(request: Request):
  return Jinja2Templates(directory="templates").TemplateResponse("index.html",{"request":request})

#APIS
@app.get("/storage")
async def storage_service(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    required_permission = "/storage"
    if current_user.get("usage", 0) <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")
    if required_permission not in current_user.get("subscription_plan", {}).get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    result = await db.User.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"usage": -1}}
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to update usage")
    return {"message": "Storage service is running"}

@app.get("/compute")
async def compute_service(current_user: User = Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    required_permission = "/compute"
    if current_user.get("usage", 0) <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")
    if required_permission not in current_user.get("subscription_plan", {}).get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    result = await db.User.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"usage": -1}}
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to update usage")
    return {"message": "Compute service is running"}
    

@app.get("/network")
async def network_service(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    required_permission = "/network"
    if current_user.get("usage", 0) <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")
    if required_permission not in current_user.get("subscription_plan", {}).get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    result = await db.User.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"usage": -1}}
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to update usage")
    return {"message": "Network service is running"}

@app.get("/database")
async def network_service(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    required_permission = "/database"
    if current_user.get("usage", 0) <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")
    if required_permission not in current_user.get("subscription_plan", {}).get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    result = await db.User.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"usage": -1}}
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to update usage")
    return {"message": "Database service is running"}

@app.get("/modeling")
async def network_service(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    required_permission = "/modeling"
    if current_user.get("usage", 0) <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")
    if required_permission not in current_user.get("subscription_plan", {}).get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    result = await db.User.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"usage": -1}}
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to update usage")
    return {"message": "Modeling service is running"}

@app.get("/view-user-plan")
async def view_plan(current_user: dict = Depends(verify_token),db: AsyncIOMotorClient = Depends(get_db)):
    user_id = current_user.get("sub")
    username = current_user.get("username")
    is_admin = current_user.get("is_admin")
    user_details = await db.User.find_one({"_id": ObjectId(user_id)})
    if user_details:
        if "subscription_plan" in user_details:
            subscription_plan = user_details["subscription_plan"]
            usage = user_details.get("usage", 0)
            limit = user_details.get("limit", 0)
            return {
                "username": username,
                "isAdmin": is_admin,
                "subscription_plan": subscription_plan,
                "usage": usage,
                "limit": limit
            }
        else:
            return {
                "username": username,
                "isAdmin": is_admin,
                "message": "Not subscribed to any plan, Please subscribe to plans 1 or 2 or 3"
            }
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
@app.post("/subscription-plans/", response_model=SubscriptionPlan)
async def create_subscription_plan(
    plan_data: SubscriptionPlan,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.get("isAdmin", False):
        existing_plan = await db.Subscription_Plan.find_one({"plan_id": plan_data.plan_id})
        if existing_plan:
            raise HTTPException(status_code=400, detail="Plan with this name already exists")
        result = await db.Subscription_Plan.insert_one({
            "plan_id":plan_data.plan_id,
            "plan": plan_data.plan,
            "description": plan_data.description,
            "api_permissions": plan_data.api_permissions,
            "usagelimit": plan_data.usagelimit
        })
        inserted_plan = await db.Subscription_Plan.find_one({"_id": result.inserted_id})
        return inserted_plan
    else:
        raise HTTPException(status_code=403, detail="Permission denied")


@app.patch("/subscription-plans/{plan_id}", response_model=SubscriptionPlan)
async def modify_subscription_plan(
    plan_id: int,
    updated_plan_data: SubscriptionPlan,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    if not current_user.get("isAdmin", False):
        raise HTTPException(status_code=403, detail="Permission denied")
    print(f"Received plan_id: {plan_id}")
    existing_plan = await db.Subscription_Plan.find_one({"plan_id": plan_id})
    print(f"Existing plan: {existing_plan}")

    if existing_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    await db.Subscription_Plan.update_one(
        {"plan_id": plan_id},
        {"$set": updated_plan_data.dict(exclude_unset=True)},
    )
    return updated_plan_data


@app.delete("/subscription-plans/{plan_id}", response_model=SubscriptionPlan)
async def delete_subscription_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    if current_user.get("isAdmin", False):
        existing_plan = await db.Subscription_Plan.find_one({"plan_id": plan_id})
        if existing_plan is None:
            raise HTTPException(status_code=404, detail="Plan not found")
        await db.Subscription_Plan.delete_one({"plan_id": plan_id})
        return existing_plan
    else:
        raise HTTPException(status_code=403, detail="Permission denied")

#endpoint for user to subscribe after login.
@app.post("/subscribe/{plan_id}", response_model=dict)
async def subscribe_to_plan(
    plan_id: int,
    current_user: dict = Depends(verify_token),
    db: AsyncIOMotorClient = Depends(get_db)
):
    subscription_plan = await db.Subscription_Plan.find_one({"plan_id":plan_id})
    if not subscription_plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    usagelimit = subscription_plan.get("usagelimit", 0)
    result = await db.User.update_one(
        {"_id": ObjectId(current_user["sub"])},
        {
            "$set": {
                "subscription_plan": {
                    "plan_id": subscription_plan["plan_id"],
                    "plan": subscription_plan["plan"],
                    "api_permissions": subscription_plan["api_permissions"],
                    "usagelimit": subscription_plan["usagelimit"],
                },
                "usage": usagelimit,
                "limit": usagelimit,
            }
        }
    )
    if result.modified_count == 1:
        return {"message": "Successfully subscribed"}
    else:
        raise HTTPException(status_code=500, detail="Failed to subscribe")

#Admin permissions..
@app.post("/permissions", response_model=Permission)
async def add_permission(
    permission_request: Permission,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if current_user.isAdmin:
        existing_permission = await db.Permissions.find_one({"name": permission_request.name})
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission with this name already exists")
        result = await db.Permissions.insert_one(permission_request.dict())
        inserted_permission = await db.Permissions.find_one({"_id": result.inserted_id})

        return inserted_permission
    else:
        raise HTTPException(status_code=403, detail="Permission denied")
    

#Endpoint to modify user subscription plan
@app.put("/subscriptions/{username}")
async def modify_user_plan(
    username: str,
    new_plan: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user.get("isAdmin"):
        raise HTTPException(status_code=403, detail="Permission denied. Admin access required.")
    user = await db.User.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_plan =user.get("subscription_plan", {}).get("plan_id")
    
    if not existing_plan:
        raise HTTPException(status_code=400, detail="User is not subscribed to any plan")
    print("Existing plan.." ,existing_plan)
    result = await db.User.update_one(
        {"username": username},
    {
        "$set": {
            "subscription_plan": new_plan,
            "usage": new_plan.get("usagelimit", 0),
            "limit": new_plan.get("usagelimit", 0),
        }
    }
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to modify user plan")

    return {"message": "User plan modified successfully"}

#check usage and limit
@app.get("/usage/{user_name}")
async def get_usage_status(
    user_name: str, current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user.get("isAdmin"):
        raise HTTPException(status_code=403, detail="Permission denied. Admin access required.")
    user = await db.User.find_one({"username": user_name})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"usage": user.get("usage", 0)}

@app.get("/usage/{user_name}/limit")
async def check_limit_status(
    user_name: str, current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    if not current_user.get("isAdmin"):
        raise HTTPException(status_code=403, detail="Permission denied. Admin access required.")
    user = await db.User.find_one({"username": user_name})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"usage": user.get("usage", 0), "limit": user.get("limit", 0)}

@app.post("/login", response_model=Token)
async def login(form_data: User, db: AsyncIOMotorClient = Depends(get_db)):
    # Verify user credentials against MongoDB
    user = await db.User.find_one({"username": form_data.username, "password": form_data.password})

    if user:
        # Generate JWT token
        token_data = {"sub": str(user["_id"]), "username": user["username"], "is_admin": user["isAdmin"]}
        token = create_jwt_token(token_data)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")



@app.post("/register", response_model=Token)
async def register(form_data: User, db: AsyncIOMotorClient = Depends(get_db)):

        # Check if the username is already taken
        existing_user = await db.User.find_one({"username": form_data.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        result = await db.User.insert_one({
            "username": form_data.username,
            "password": form_data.password,
            "isAdmin": form_data.isAdmin,
        })
        
        inserted_user = await db.User.find_one({"_id": result.inserted_id})


        print(f"Inserted user: {inserted_user}")#Adding this line for debugging
        if inserted_user:
            token_data = {"sub": str(inserted_user["_id"]), "username": inserted_user["username"], "is_admin": inserted_user["isAdmin"]}
            token = create_jwt_token(token_data)

            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve inserted user")