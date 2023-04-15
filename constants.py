from dotenv import get_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_TOKEN = get_key(".env", "JWT_TOKEN")
