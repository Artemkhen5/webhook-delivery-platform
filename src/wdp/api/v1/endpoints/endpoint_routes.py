from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from wdp.api.dependencies import get_current_account
from wdp.db.models import Account
from wdp.db.session import get_session
from wdp.schemas.endpoint import EndpointCreateRequest, EndpointCreateResponse, ListEndpoints, EndpointResponse, \
    EndpointUpdateRequest
from wdp.services import endpoints as endpoints_service
from wdp.repositories import endpoints as endpoints_repository

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
AccountDep = Annotated[Account, Depends(get_current_account)]


@router.post(
    "/",
    response_model=EndpointCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_endpoint(
        request: EndpointCreateRequest,
        session: SessionDep,
        account: AccountDep,
) -> EndpointCreateResponse:
    endpoint, secret = await endpoints_service.create_endpoint(
        session=session,
        account_id=account.id,
        url=str(request.url),
        event_types=request.event_types
    )

    return EndpointCreateResponse(
        id=endpoint.id,
        url=endpoint.url,
        event_types=request.event_types,
        secret=secret,
    )


@router.get(
    "/",
    response_model=ListEndpoints,
    status_code=status.HTTP_200_OK,
)
async def get_endpoints(
        session: SessionDep,
        *,
        account: AccountDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
) -> ListEndpoints:
    rows = await endpoints_repository.get_endpoints(
        session,
        account_id=account.id,
        limit=limit,
        offset=offset
    )
    return ListEndpoints(
        endpoints=[
            EndpointResponse(
                id=endpoint.id,
                url=endpoint.url,
                event_types=event_types,
                is_active=endpoint.is_active,
            )
            for endpoint, event_types in rows
        ]
    )


@router.patch(
    "/{endpoint_id}",
    response_model=EndpointResponse,
    status_code=status.HTTP_200_OK,
)
async def update_endpoint(
        session: SessionDep,
        *,
        account: AccountDep,
        endpoint_id: UUID,
        request: EndpointUpdateRequest,
) -> EndpointResponse:
    endpoint, event_types = await endpoints_repository.update_endpoint(
        session,
        account_id=account.id,
        endpoint_id=endpoint_id,
        request=request
    )
    return EndpointResponse(
        id=endpoint.id,
        url=endpoint.url,
        event_types=event_types,
        is_active=endpoint.is_active,
    )
