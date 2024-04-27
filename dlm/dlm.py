from redis import StrictRedis

from exceptions import ResourceAlreadyLockedException
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
    return redis.call("EXPIRE", KEYS[1], ARGV[2])
else
    return 0
end
'''
EXTEND_LOCK_COMMAND_NUMKEYS = 1


class DistributedLockManager:

    def __init__(self, connection_strings: list[str]):
        self.redis_instances = []
        for connection_string in connection_strings:
            redis_connection = StrictRedis.from_url(connection_string)
            self.redis_instances.append(redis_connection)
        self.qourum_requirement = len(self.redis_instances) // 2 + 1

    def lock(self, resource_id: str, rent_time_ms: int) -> Lock:
        lock_id = new_unique_lock_id()
        print(len(lock_id))
        for instance in self.redis_instances:
            successfully_locked = DistributedLockManager._lock_on_instance(instance, resource_id, lock_id, rent_time_ms)
            if not successfully_locked:
                raise ResourceAlreadyLockedException
        return Lock(resource_id, lock_id, rent_time_ms)

    def unlock(self, lock: Lock) -> bool:
        for instance in self.redis_instances:
            DistributedLockManager._unlock_on_instance(instance, lock.resource_id, lock.unique_lock_id)

    def extend(self, lock: Lock, new_rent_time_ms: int) -> bool:
        for instance in self.redis_instances:
            DistributedLockManager._extend_on_instance(
                instance,
                lock.resource_id,
                lock.unique_lock_id,
                new_rent_time_ms
            )

    @staticmethod
    def _lock_on_instance(redis_instance: StrictRedis, resource_id: str, client_id: str, rent_time_ms: int) -> bool:
        return redis_instance.set(resource_id, client_id, nx=True, px=rent_time_ms)

    @staticmethod
    def _unlock_on_instance(redis_instance: StrictRedis, resource_id: str, unique_lock_id: str):
        return redis_instance.eval(DELETE_LOCK_COMMAND, DELETE_LOCK_COMMAND_NUMKEYS, resource_id, unique_lock_id)

    @staticmethod
    def _extend_on_instance(redis_instance: StrictRedis, resource_id: str, unique_lock_id: str, new_rent_time_ms: int):
        return redis_instance.eval(
            EXTEND_LOCK_COMMAND,
            EXTEND_LOCK_COMMAND_NUMKEYS,
            resource_id,
            unique_lock_id,
            str(new_rent_time_ms)
        )
