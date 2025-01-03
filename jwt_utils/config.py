from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Load values from the .env file
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_DAYS = os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")

# Check if all required values are present
if not SECRET_KEY or not ALGORITHM or not ACCESS_TOKEN_EXPIRE_DAYS:
    raise ValueError("One or more environment variables are missing. Please ensure that all required variables are set.")
