from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wdp.db.models import Endpoint, EndpointSubscription


async def add_endpoint(
        session: AsyncSession,
        *,
        account_id: UUID,
        url: str,
        secret_encrypted: str,
) -> Endpoint:
    endpoint = Endpoint(
        account_id=account_id,
        url=url,
        secret_encrypted=secret_encrypted,
    )
    session.add(endpoint)
    await session.flush()
    return endpoint


async def add_subscriptions(
        session: AsyncSession,
        *,
        endpoint_id: UUID,
        event_types: list[str],
) -> None:
    subscriptions = [
        EndpointSubscription(endpoint_id=endpoint_id, event_type=event_type)
        for event_type in event_types
    ]
    session.add_all(subscriptions)
    await session.flush()


async def get_endpoints(
        session: AsyncSession,
        *,
        account_id: UUID,
        limit: int,
        offset: int,
) -> list[tuple[Endpoint, list[str]]]:
    endpoints_result = await session.execute(
        select(Endpoint).
        where(Endpoint.account_id == account_id).
        order_by(Endpoint.created_at.desc(), Endpoint.id).
        limit(limit).
        offset(offset)
    )
    endpoints = list(endpoints_result.scalars().all())

    if not endpoints:
        return []

    endpoints_ids = [endpoint.id for endpoint in endpoints]

    subscriptions_result = await session.execute(
        select(EndpointSubscription.endpoint_id, EndpointSubscription.event_type)
        .where(EndpointSubscription.endpoint_id.in_(endpoints_ids))
        .order_by(EndpointSubscription.event_type)
    )

    event_types_by_endpoint: dict[UUID, list[str]] = {
        endpoint_id: [] for endpoint_id in endpoints_ids
    }
    for endpoint_id, event_type in subscriptions_result:
        event_types_by_endpoint[endpoint_id].append(event_type)

    return [
        (endpoint, event_types_by_endpoint[endpoint.id])
        for endpoint in endpoints
    ]
