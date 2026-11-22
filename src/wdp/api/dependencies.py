from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wdp.db.models import Account
from wdp.db.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TEST_ACCOUNT_ID = UUID("01a1f1dd-b4d2-7421-a3ec-f5b4f4361eec")


async def get_current_account(session: SessionDep) -> Account:
    result = await session.execute(
        select(Account)
        .where(Account.id == TEST_ACCOUNT_ID)
    )
    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found",
        )

    return account
