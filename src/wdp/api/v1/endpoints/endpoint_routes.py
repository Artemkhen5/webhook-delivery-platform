from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from wdp.api.dependencies import get_current_account
from wdp.db.models import Account, Endpoint
from wdp.db.session import get_session
from wdp.schemas.endpoint import EndpointCreateRequest, EndpointCreateResponse, ListEndpoints, EndpointResponse
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
