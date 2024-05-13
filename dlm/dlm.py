from time import time

from redis import Redis, RedisError
from redis.exceptions import ConnectionError as RedisConnectionError

from exceptions import ResourceAlreadyLockedException, WrongUniqueLockIdException, ResourceLockException
from lock import Lock
from util import new_unique_lock_id


DELETE_LOCK_COMMAND = '''
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
'''
DELETE_LOCK_COMMAND_NUMKEYS = 1

EXTEND_LOCK_COMMAND = '''
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("PEXPIRE", KEYS[1], ARGV[2])
else
    return 0
end
'''
EXTEND_LOCK_COMMAND_NUMKEYS = 1


class DistributedLockManager:

    def __init__(self, connection_strings: list[str]):
        self.redis_instances = []
        for connection_string in connection_strings:
            redis_connection = Redis.from_url(connection_string)
            self.redis_instances.append(redis_connection)
        self.quorum_requirement = len(self.redis_instances) // 2 + 1

    def lock(self, resource_id: str, rent_time_ms: int) -> Lock:
        lock_id = new_unique_lock_id()
        errors = []

        start_time = int(time() * 1000)
        for instance in self.redis_instances:
            try:
                successfully_locked = DistributedLockManager._lock_on_instance(instance, resource_id, lock_id, rent_time_ms)
                if not successfully_locked:
                    errors.append(ResourceAlreadyLockedException())
            except RedisConnectionError as exc:
                errors.append(exc)

        elapsed_time = int(time() * 1000) - start_time
        remaining_time = int(rent_time_ms - elapsed_time)

        if remaining_time > 0 and len(self.redis_instances) - len(errors) >= self.quorum_requirement:
            return Lock(resource_id, lock_id, remaining_time)
        else:
            for server in self.redis_instances:
                try:
                    DistributedLockManager._unlock_on_instance(server, resource_id, lock_id)
                except:
                    pass
            raise ResourceLockException(errors)

    def unlock(self, lock: Lock):
        errors = []
        for instance in self.redis_instances:
            try:
                changed_rows_count = DistributedLockManager._unlock_on_instance(instance, lock.resource_id, lock.unique_lock_id)
                if changed_rows_count != 1:
                    errors.append(WrongUniqueLockIdException(lock.unique_lock_id))
            except (RedisConnectionError, RedisError) as e:
                errors.append(e)
        if len(self.redis_instances) - len(errors) < self.quorum_requirement:
            raise ResourceLockException(errors)

    def extend(self, lock: Lock, new_rent_time_ms: int) -> Lock:
        errors = []

        start_time = int(time() * 1000)
        for instance in self.redis_instances:
            try:
                changed_rows_count = DistributedLockManager._extend_on_instance(
                    instance,
                    lock.resource_id,
                    lock.unique_lock_id,
                    new_rent_time_ms
                )
                if changed_rows_count != 1:
                    errors.append(WrongUniqueLockIdException(lock.unique_lock_id))
            except RedisConnectionError as exc:
                errors.append(exc)
        elapsed_time = int(time() * 1000) - start_time
        remaining_time = int(new_rent_time_ms - elapsed_time)

        if remaining_time > 0 and len(self.redis_instances) - len(errors) >= self.quorum_requirement:
            return Lock(lock.resource_id, lock.unique_lock_id, remaining_time)
        else:
            raise ResourceLockException(errors)

    @staticmethod
    def _lock_on_instance(redis_instance: Redis, resource_id: str, client_id: str, rent_time_ms: int) -> bool:
        return redis_instance.set(resource_id, client_id, nx=True, px=rent_time_ms)

    @staticmethodgit
    def _unlock_on_instance(redis_instance: Redis, resource_id: str, unique_lock_id: str) -> str:
        return redis_instance.eval(
            DELETE_LOCK_COMMAND,
            DELETE_LOCK_COMMAND_NUMKEYS,
            resource_id,
            unique_lock_id,
        )

    @staticmethod
    def _extend_on_instance(redis_instance: Redis, resource_id: str, unique_lock_id: str, new_rent_time_ms: int) -> str:
        return redis_instance.eval(
            EXTEND_LOCK_COMMAND,
            EXTEND_LOCK_COMMAND_NUMKEYS,
            resource_id,
            unique_lock_id,
            str(new_rent_time_ms),
        )
