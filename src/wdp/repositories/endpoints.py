from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from wdp.db.models import Endpoint, EndpointSubscription
from wdp.schemas.endpoint import EndpointResponse, EndpointUpdateRequest


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


async def update_endpoint(
        session: AsyncSession,
        *,
        account_id: UUID,
        endpoint_id: UUID,
        request: EndpointUpdateRequest,
) -> tuple[Endpoint, list[str]]:
    stmt = (
        select(Endpoint)
        .where(Endpoint.id == endpoint_id)
        .where(Endpoint.account_id == account_id)
    )
    endpoint = await session.scalar(stmt)

    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    updated_data = request.model_dump(
        exclude_unset=True,
    )
    event_types = updated_data.pop("event_types", None)

    for field, value in updated_data.items():
        if field == "url":
            value = str(value)
        setattr(endpoint, field, value)

    current_event_types = await sync_event_types(
        session,
        endpoint_id=endpoint_id,
        event_types=event_types,
    )

    await session.commit()
    await session.refresh(endpoint)
    return endpoint, current_event_types


async def sync_event_types(
        session: AsyncSession,
        *,
        endpoint_id: UUID,
        event_types: list[str] | None,
) -> list[str]:
    result = await session.scalars(
        select(EndpointSubscription)
        .where(EndpointSubscription.endpoint_id == endpoint_id)
    )
    existing_subscriptions = list(result.all())
    existing_types = {
        subscription.event_type
        for subscription in existing_subscriptions
    }

    if event_types is None:
        return sorted(existing_types)

    requested_types = set(event_types)
    subscriptions_to_remove = existing_types - requested_types
    subscriptions_to_add = requested_types - existing_types

    for subscription in existing_subscriptions:
        if subscription.event_type in subscriptions_to_remove:
            await session.delete(subscription)

    for event_type in subscriptions_to_add:
        session.add(
            EndpointSubscription(
                endpoint_id=endpoint_id,
                event_type=event_type,
            )
        )

    return sorted(requested_types)