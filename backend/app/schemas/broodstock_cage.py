from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BroodstockCageCreate(BaseModel):
    hatchery_id: int = Field(..., alias="hatcheryId")
    cage_code: str = Field(..., min_length=1, max_length=64, alias="cageCode")
    capacity: int = Field(..., gt=0)
    is_active: bool = Field(True, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)


class BroodstockCageUpdate(BaseModel):
    cage_code: Optional[str] = Field(None, min_length=1, max_length=64, alias="cageCode")
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = Field(None, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)


class BroodstockCageStock(BaseModel):
    count: int = Field(..., gt=0)

    model_config = ConfigDict(populate_by_name=True)


class BroodstockCageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    hatchery_id: int = Field(serialization_alias="hatcheryId")
    cage_code: str = Field(serialization_alias="cageCode")
    capacity: int
    occupied: int
    is_active: bool = Field(serialization_alias="isActive")
