from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

#db
from database import get_db
from model import User, SubscriptionPlan, Permission, Token
#authenticate
from authentication import create_jwt_token, authenticate_user, get_current_user, verify_token, get_permission_by_id,get_subscription_plan_by_id


app = FastAPI()


SECRET_KEY = "2000$"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.get("/", response_class=HTMLResponse)  #index start page if we run the application 
async def index(request: Request):
  return Jinja2Templates(directory="templates").TemplateResponse("index.html",{"request":request})

#APIS
@app.get("/storage")
def storage_service():
    id = 101
    return {"Storage service is running"}

@app.post("/compute")
def compute_service():
    id = 102
    return {"Compute service is running"}

@app.put("/network")
def network_service():
    id = 103
    return {"Network service is running"}

@app.delete("/database")
def database_service():
    id = 104
    return {"Database service is running"}

@app.put("/modeling")
def machine_learning_service():
    id = 105
    return {"Modeling service is running"}


@app.get("/view-user-plan")
async def view_plan(current_user: dict = Depends(verify_token),db: AsyncIOMotorClient = Depends(get_db)):
    # Extract user details from the token payload
    user_id = current_user.get("sub")
    username = current_user.get("username")
    is_admin = current_user.get("is_admin")
    # Retrieve user details from the database
    user_details = await db.User.find_one({"_id": ObjectId(user_id)})
    if user_details:
        # If the user has a subscription plan
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
            # If the user is not subscribed to any plan
            return {
                "username": username,
                "isAdmin": is_admin,
                "message": "Not subscribed to any plan"
            }
    else:
        raise HTTPException(status_code=404, detail="User not found")
    



@app.post("/subscription-plans/", response_model=SubscriptionPlan)
async def create_subscription_plan(
    plan_data: SubscriptionPlan,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.isAdmin:
        # Check if the plan with the given name already exists
        existing_plan = await db.Subscription_Plan.find_one({"plan_id": plan_data.plan_id})
        if existing_plan:
            raise HTTPException(status_code=400, detail="Plan with this name already exists")
        # Insert the new plan into the MongoDB collection
        result = await db.Subscription_Plan.insert_one({
            "plan_id":plan_data.plan_id,
            "plan": plan_data.plan,
            "description": plan_data.description,
            "api_permissions": plan_data.api_permissions,
            "usagelimit": plan_data.usagelimit
        })

        # Retrieve the inserted plan
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
    if not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Ensure the plan with the given ID exists
    print(f"Received plan_id: {plan_id}")
    existing_plan = await db.Subscription_Plan.find_one({"plan_id": plan_id})
    print(f"Existing plan: {existing_plan}")

    if existing_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Update the plan details with only the provided fields
    await db.Subscription_Plan.update_one(
        {"plan_id": plan_id},
        {"$set": updated_plan_data.dict(exclude_unset=True)},
    )
    # Return the updated plan
    return updated_plan_data


@app.delete("/subscription-plans/{plan_id}", response_model=SubscriptionPlan)
async def delete_subscription_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    if current_user.isAdmin:
        # Ensure the plan with the given ID exists
        existing_plan = await db.Subscription_Plan.find_one({"plan_id": plan_id})
        if existing_plan is None:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Delete the plan
        await db.Subscription_Plan.delete_one({"plan_id": plan_id})

        # Return the deleted plan
        return existing_plan
    else:
        raise HTTPException(status_code=403, detail="Permission denied")










































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
        
        # Insert the new user into the MongoDB collection
        result = await db.User.insert_one({
            "username": form_data.username,
            "password": form_data.password,
            "isAdmin": form_data.isAdmin,
        })
        
        inserted_user = await db.User.find_one({"_id": result.inserted_id})


        print(f"Inserted user: {inserted_user}")  # Add this line for debugging

        if inserted_user:
            # Generate JWT token for the newly registered user
            token_data = {"sub": str(inserted_user["_id"]), "username": inserted_user["username"], "is_admin": inserted_user["isAdmin"]}
            token = create_jwt_token(token_data)

            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve inserted user")
    