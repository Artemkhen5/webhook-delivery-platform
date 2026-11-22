from uuid import UUID

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
