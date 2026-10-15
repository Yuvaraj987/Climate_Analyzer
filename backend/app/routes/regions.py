from fastapi import APIRouter

router = APIRouter(prefix="/regions", tags=["regions"])

REGIONS = [
    {"id": "kerala", "name": "Kerala, India", "latitude": 10.0, "longitude": 76.3},
    {"id": "delhi", "name": "Delhi, India", "latitude": 28.6139, "longitude": 77.2090},
    {"id": "mumbai", "name": "Mumbai, India", "latitude": 19.0760, "longitude": 72.8777},
    {"id": "chennai", "name": "Chennai, India", "latitude": 13.0827, "longitude": 80.2707},
    {"id": "new-york", "name": "New York, USA", "latitude": 40.7128, "longitude": -74.0060},
]


@router.get("")
async def list_regions():
    return {"regions": REGIONS}
