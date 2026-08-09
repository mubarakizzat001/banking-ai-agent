from redis.asyncio import Redis
from config import settingRedis

_blacklist_tokens=Redis(
    host=settingRedis.redis_host,
    port=settingRedis.redis_port,
    db=1
)

async def add_tokens_to_blacklist(jti:str):
    await _blacklist_tokens.set(jti,"blacklisted")

async def is_token_blacklisted(jti:str)->bool:
    return bool(await _blacklist_tokens.get(jti))
