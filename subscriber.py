import asyncio
import json
import random
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database import async_engine
from database import redis as redis_client
from models import Status
from repository import TaskRepository


def run_task(task_id: int):
    try:
        redis_client.publish('start_task', task_id)
        print('Started useful load')
        time.sleep(random.randint(0, 10))
        print('Finished useful load')
        data = json.dumps({'task_id': task_id, 'finished_at': datetime.now().isoformat()})
        redis_client.publish('finish_task', data)
    except Exception as e:
        print(e)


class Subscriber:
    def __enter__(self):
        self._redis = redis.Redis(host=config.redis.host, port=config.redis.port)
        self._pool = ProcessPoolExecutor(max_workers=config.app.worker_count)
        return self

    async def run(self):
        sub = self._redis.pubsub()
        sub.subscribe('create_task', 'start_task', 'finish_task')
        while True:
            message = sub.get_message()
            if message is None:
                continue

            channel = message['channel'].decode()
            msg_type = message['type']

            if msg_type == 'subscribe':
                print(f'Established pubsub connection for {channel}')

            if msg_type == 'message':
                match channel:
                    case 'create_task':
                        task_id = int(message['data'].decode())
                        self._pool.submit(run_task, task_id)
                    case 'start_task':
                        task_id = int(message['data'].decode())
                        await self.start_task(task_id)
                    case 'finish_task':
                        data = json.loads(message['data'])
                        await self.finish_task(data.get('task_id'), datetime.fromisoformat(data.get('finished_at')))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pool.shutdown()
        self._redis.close()

    async def start_task(self, task_id: int) -> None:
        async with AsyncSession(async_engine) as session:
            try:
                repo = TaskRepository(session=session)
                await repo.update(task_id, {'status': Status.RUN.value, 'start_time': datetime.now()})
                await session.commit()
            except Exception as err:
                print(f'Error occurred, rolling back session {err}')
                await session.rollback()

    async def finish_task(self, task_id: int, finish_time: datetime) -> None:
        async with AsyncSession(async_engine) as session:
            try:
                repo = TaskRepository(session=session)
                task = await repo.get(task_id)
                await repo.update(
                    task_id, {
                        'status': Status.Completed.value,
                        'execution_time': (finish_time - task.start_time).seconds,
                    },
                )
                await session.commit()
            except Exception as err:
                print(f'Error occurred, rolling back session {err}')
                await session.rollback()


async def main():
    with Subscriber() as subscriber:
        await subscriber.run()


if __name__ == '__main__':
    asyncio.run(main())
