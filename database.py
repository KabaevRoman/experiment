import logging

import redis as r
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import config

async_engine = create_async_engine(config.db.url, echo=config.db.echo_log, future=True)

logger = logging.getLogger(__file__)


async def get_session() -> AsyncSession:
    async with AsyncSession(async_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception as err:
            logger.warning('Error occurred, rolling back session', exc_info=err)
            await session.rollback()
            raise err


redis = r.Redis(host=config.redis.host, port=config.redis.port)
