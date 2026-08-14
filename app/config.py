from pydantic_settings import BaseSettings, SettingsConfigDict


_base_model=SettingsConfigDict(
    env_file=(".env",".env.test"),
    env_ignore_empty=True,
    extra="ignore"
)
class databseconfig(BaseSettings):
    postgres_server:str
    postgres_port:int
    postgres_user:str
    postgres_password:str
    postgres_db:str

    model_config=_base_model
    @property
    def async_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

class jwtconfig(BaseSettings):
    jwt_secret:str
    jwt_algorithm:str

    model_config=_base_model
    
class redisconfig(BaseSettings):
    redis_host:str
    redis_port:int

    model_config=_base_model
settingDB=databseconfig()
settingJWT=jwtconfig()
settingRedis=redisconfig()
