from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
OWNER_ADDRESS = os.getenv("OWNER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")