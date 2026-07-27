from pydantic_settings import BaseSettings, SettingsConfigDic


_base_model=SettingsConfigDic(
    env_file=".env",
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


settingDB=databseconfig()