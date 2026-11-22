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
