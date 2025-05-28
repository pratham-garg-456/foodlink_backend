from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.config import settings
from contextlib import asynccontextmanager
from app.routes import auth, misc, volunteer, individual, donor
from app.routes.foodbank import (
    volunteer_mangement,
    inventory,
    events,
    food_items,
    appointments,
    donations,
    jobs,
    details
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting application in {settings.APP_ENV} environment...")
    try:
        await init_db()
        print("Database connection initialized successfully.")
    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")
    yield


# Create FastAPI instance
app = FastAPI(
    title="FastAPI with FoodLink",
    description="An application that handles the inside functionalities of FoodLink App",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route
app.include_router(auth.router, prefix="/api/v1/foodlink/auth", tags=["Authentication"])
app.include_router(misc.router, prefix="/api/v1/foodlink/misc", tags=["Misc"])
app.include_router(
    volunteer.router, prefix="/api/v1/foodlink/volunteer", tags=["Volunteer"]
)
app.include_router(
    individual.router, prefix="/api/v1/foodlink/individual", tags=["Individual"]
)
app.include_router(donor.router, prefix="/api/v1/foodlink/donor", tags=["Donor"])

# APIs route for foodbank
app.include_router(
    inventory.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"]
)

app.include_router(events.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"])

app.include_router(
    food_items.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"]
)

app.include_router(
    appointments.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"]
)

app.include_router(
    donations.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"]
)

app.include_router(jobs.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"])

app.include_router(
    volunteer_mangement.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"]
)

app.include_router(
    details.router, prefix="/api/v1/foodlink/foodbank", tags=["FoodBank"]
) 


# Root endpoint for health checks or basic info
@app.get("/")
async def root():
    return {"message": "Welcome to the FoodLink application "}
