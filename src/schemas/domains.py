from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class AddNewDomain(BaseModel):
    domain_name: str
    image_uri: str
    created_at: datetime = Field(default_factory=datetime.now)


class AddCoursesDomain(BaseModel):
    domain_id: str
    courses_ids: List[str]


class UpdateOnDemandDomain(BaseModel):
    domain_id: str
    on_demand: bool


class UpdateDomain(BaseModel):
    domain_id: str
    domain_name: str
    description: str


class RemoveSegmentFromDomain(BaseModel):
    domain_id: str
    segment_ids: List[str]


class AddSegmentsToDomain(BaseModel):
    domain_id: str
    segment_ids: List[str]
