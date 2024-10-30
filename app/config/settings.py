from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AccessSettings(BaseSettings):
    IS_PROD: bool = Field(False, alias="IS_PROD")
    API_LAGO_KEY: str = Field("b111111-2222-3g33-4444-555f66f7777a", alias="API_LAGO_KEY")
    API_URL: str = Field("https://bill.rnd.flowai.ru/api/v1", alias="API_URL")
    PLAN_CODE: str = Field("Your_plan", alias="PLAN_CODE")

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding="utf-8")


class AppSettings(BaseModel):
    app: AccessSettings = AccessSettings()
    title: str = "LagoCRUDFastApi"
    version: str = "0.1.1"


settings = AppSettings()
