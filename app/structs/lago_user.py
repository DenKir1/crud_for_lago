from pydantic import BaseModel, ConfigDict, field_validator
import uuid


class BaseUserStruct(BaseModel):
    uuid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class CreateUserStruct(BaseUserStruct):
    pass


class UpdateUserStruct(BaseUserStruct):
    pass


class UserStruct(BaseUserStruct):
    pass
    # measures: list[int] = []
    #
    # @field_validator("measures", mode="before")
    # @classmethod
    # def validate_measures(cls, value):
    #     if value:
    #         return [el for el in value]
    #     return []
