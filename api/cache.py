import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()

TTL_SECONDS = 300

_client = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    decode_responses=True,
)


def key(*parts) -> str:
    return ":".join(str(p) for p in parts)


def get(cache_key):
    raw = _client.get(cache_key)
    return json.loads(raw) if raw is not None else None


def set(cache_key, value):
    _client.set(cache_key, json.dumps(value, default=str), ex=TTL_SECONDS)


def flush():
    _client.flushdb()
