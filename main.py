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
async def storage_service(current_user: User = Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if the user has the necessary permission to access the /storage endpoint
    required_permission = "/storage"

    # Check if the usage limit has been exhausted
    if current_user.usage <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")

    # Check if the required permission is in the user's subscription plan
    if required_permission not in current_user.subscription_plan.get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Reduce the usage by 1
    current_user.usage -= 1
    
    await db.User.update_one({"_id": ObjectId(current_user["_id"])},
        {"$set": {"usage": current_user["usage"]}})

    # Your existing logic for the /storage service goes here
    return {"message": "Storage service is running"}

@app.get("/compute")
async def compute_service(current_user: User = Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    # Check if the user is authenticated
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if the user has the necessary permission to access the /compute endpoint
    required_permission = "/compute"

    # Check if the usage limit has been exhausted
    if current_user.usage <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")

    # Check if the required permission is in the user's subscription plan
    if required_permission not in current_user.subscription_plan.get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Reduce the usage by 1
    current_user.usage -= 1

    # Your existing logic for the /compute service goes here
    return {"message": "Compute service is running"}

@app.get("/network")
async def network_service(current_user: User = Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    # Check if the user is authenticated
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if the user has the necessary permission to access the /network endpoint
    required_permission = "/network"

    # Check if the usage limit has been exhausted
    if current_user.usage <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")

    # Check if the required permission is in the user's subscription plan
    if required_permission not in current_user.subscription_plan.get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Reduce the usage by 1
    current_user.usage -= 1

    # Your existing logic for the /network service goes here
    return {"message": "Network service is running"}

@app.get("/database")
async def database_service(current_user: User = Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    required_permission = "/database"
    if current_user.limit <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")
    if required_permission not in current_user.subscription_plan.get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    current_user.limit -= 1
    return {"message": "Database service is running"}

@app.get("/modeling")
async def modeling_service(current_user: User = Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    # Check if the user is authenticated
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if the user has the necessary permission to access the /modeling endpoint
    required_permission = "/modeling"

    # Check if the usage limit has been exhausted
    if current_user.usage <= 0:
        raise HTTPException(status_code=403, detail="Usage limit exhausted")

    # Check if the required permission is in the user's subscription plan
    if required_permission not in current_user.subscription_plan.get("api_permissions", []):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Reduce the usage by 1
    current_user.usage -= 1

    # Your existing logic for the /modeling service goes here
    return {"message": "Modeling service is running"}


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


#endpoint for user to subscribe after login.
@app.post("/subscriptions/{plan_id}", response_model=dict)
async def subscribe_to_plan(
    plan_id: int,
    current_user: dict = Depends(verify_token),
    db: AsyncIOMotorClient = Depends(get_db)
):
    # Retrieve the subscription plan details
    subscription_plan = await db.Subscription_Plan.find_one({"plan_id":plan_id})

    if not subscription_plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    usagelimit = subscription_plan.get("usagelimit", 0)
    # Update the user model with subscription details
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
        # Check if the permission with the given name already exists
        existing_permission = await db.Permissions.find_one({"name": permission_request.name})
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission with this name already exists")

        # Insert the new permission into the MongoDB collection
        result = await db.Permissions.insert_one(permission_request.dict())

        # Retrieve the inserted permission
        inserted_permission = await db.Permissions.find_one({"_id": result.inserted_id})

        return inserted_permission
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
    
    
    