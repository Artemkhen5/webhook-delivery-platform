from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from wdp.api.dependencies import get_current_account
from wdp.db.models import Account
from wdp.db.session import get_session
from wdp.schemas.endpoint import EndpointCreateRequest, EndpointCreateResponse
from wdp.services import endpoints as endpoints_service

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
