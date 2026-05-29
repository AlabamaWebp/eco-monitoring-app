from pydantic import BaseModel, ConfigDict, Field, field_validator


class PolygonWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Название полигона обязательно.")
        return normalized

    @field_validator("location", "description")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class MeasurementUnitWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    symbol: str = Field(min_length=1, max_length=50)
    description: str | None = None

    @field_validator("name", "symbol")
    @classmethod
    def normalize_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Обязательное поле не заполнено.")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class SensorTypeWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=100)
    description: str | None = None

    @field_validator("name", "code")
    @classmethod
    def normalize_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Обязательное поле не заполнено.")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class PolygonRead(BaseModel):
    polygon_id: int
    name: str
    location: str | None
    description: str | None


class MeasurementUnitRead(BaseModel):
    unit_id: int
    name: str
    symbol: str
    description: str | None


class SensorTypeRead(BaseModel):
    sensor_type_id: int
    unit_id: int
    name: str
    code: str
    description: str | None
    unit_symbol: str
