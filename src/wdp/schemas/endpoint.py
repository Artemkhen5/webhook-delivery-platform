from uuid import UUID

from pydantic import BaseModel, HttpUrl


class EndpointCreateRequest(BaseModel):
    url: HttpUrl
    event_types: list[str]


class EndpointCreateResponse(BaseModel):
    id: UUID
    url: str
    event_types: list[str]
    secret: str


class EndpointResponse(BaseModel):
    id: UUID
    url: str
    event_types: list[str]
    is_active: bool


class ListEndpoints(BaseModel):
    endpoints: list[EndpointResponse]


class EndpointUpdateRequest(BaseModel):
    url: HttpUrl | None = None
    event_types: list[str] | None = None
    is_active: bool | None = None
