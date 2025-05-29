from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB connection string
    MONGO_URI: str
    
    # Any additional settings can go here
    APP_ENV: str = "development"  # Default to development
    
    SECRET_KEY: str

    # Cloudinary credentials
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    class Config:
        env_file = ".env.development"  # Path to the .env file
        
# Create a singleton instance of the settings class
settings = Settings()    