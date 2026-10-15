from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None
database = None

# In-memory fallback makes the app runnable without MongoDB, but data is lost on restart.
memory_weather: dict[str, list[dict]] = {}
memory_analysis: dict[str, dict] = {}


async def connect_to_mongo() -> None:
    global client, database
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=1500)
        await client.admin.command("ping")
        database = client[settings.mongodb_database]
        await database.weather_observations.create_index(
            [("cache_key", 1), ("date", 1)], unique=True
        )
        await database.hazard_analyses.create_index("analysis_key", unique=True)
        print("Connected to MongoDB.")
    except Exception as exc:
        if client:
            client.close()
        client = None
        database = None
        print(f"MongoDB unavailable; using in-memory demo cache ({exc}).")


async def close_mongo_connection() -> None:
    global client
    if client:
        client.close()
        client = None


async def get_cached_weather(cache_key: str) -> list[dict] | None:
    if database is not None:
        docs = await database.weather_observations.find(
            {"cache_key": cache_key}, {"_id": 0, "cache_key": 0}
        ).sort("date", 1).to_list(length=None)
        return docs or None
    return memory_weather.get(cache_key)


async def save_weather(cache_key: str, rows: list[dict]) -> None:
    if database is not None:
        if rows:
            await database.weather_observations.delete_many({"cache_key": cache_key})
            await database.weather_observations.insert_many(
                [{"cache_key": cache_key, **row} for row in rows],
                ordered=False,
            )
    else:
        memory_weather[cache_key] = rows


async def get_cached_analysis(analysis_key: str) -> dict | None:
    if database is not None:
        doc = await database.hazard_analyses.find_one(
            {"analysis_key": analysis_key}, {"_id": 0, "analysis_key": 0}
        )
        return doc
    return memory_analysis.get(analysis_key)


async def save_analysis(analysis_key: str, result: dict) -> None:
    if database is not None:
        await database.hazard_analyses.replace_one(
            {"analysis_key": analysis_key},
            {"analysis_key": analysis_key, **result},
            upsert=True,
        )
    else:
        memory_analysis[analysis_key] = result
