from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from wdp.core.security import generate_secret, encrypt_secret
from wdp.db.models import Endpoint
from wdp.repositories import endpoints as endpoints_repository


async def create_endpoint(
        session: AsyncSession,
        account_id: UUID,
        url: str,
        event_types: list[str]
) -> tuple[Endpoint, str]:
    secret = generate_secret()
    secret_encrypted = encrypt_secret(secret)

    try:
        endpoint = await endpoints_repository.add_endpoint(
            session,
            account_id=account_id,
            url=url,
            secret_encrypted=secret_encrypted,
        )
        await endpoints_repository.add_subscriptions(
            session,
            endpoint_id=endpoint.id,
            event_types=event_types,
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return endpoint, secret
