import pathlib
import os
from dotenv import get_key

ENV_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), ".env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_TOKEN = get_key(ENV_PATH, "JWT_TOKEN")

ORS_TOKEN = get_key(ENV_PATH, "OPEN_ROUTE_SERVICE_TOKEN")
ORS_BASE_URL = "https://api.openrouteservice.org"
ORS_COORDS_URL = f"{ORS_BASE_URL}/geocode/search/structured?api_key={ORS_TOKEN}&country=RO&boundary.country=RO&locality="
ORS_DISTANCE_URL = f"{ORS_BASE_URL}/v2/directions/driving-car"
ORS_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
    "Authorization": ORS_TOKEN
}
