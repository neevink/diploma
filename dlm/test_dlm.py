import time
from dlm import DistributedLockManager
from exceptions import ResourceAlreadyLockedException, WrongUniqueLockIdException, ResourceLockException

import pytest

from lock import Lock


@pytest.fixture
def dlm():
    dlm = DistributedLockManager(
        [
            "redis://:glsRjb9LOP@localhost:6379/0"
        ]
    )
    return dlm


def test_lock_and_unlock(dlm):
    lock = dlm.lock("test-resource-1", 1000)
    assert lock.resource_id == "test-resource-1"
    dlm.unlock(lock)
    lock = dlm.lock("test-resource-1", 10)
    dlm.unlock(lock)


def test_exception_on_acquired_lock(dlm):
    lock = dlm.lock("test-resource-2", 1000)
    with pytest.raises(ResourceLockException) as exc:
        _ = dlm.lock("test-resource-2", 10)
    assert len(exc.value.errors) == 1
    assert exc.value == ResourceLockException(
        [
            ResourceAlreadyLockedException(),
        ]
    )
    dlm.unlock(lock)


def test_extend(dlm):
    lock = dlm.lock("maybe-baby", 1000)
    assert lock.resource_id == "maybe-baby"
    assert 500 < lock.rent_time_ms <= 1000
    extended_lock = dlm.extend(lock, 2000)
    assert 1500 < extended_lock.rent_time_ms <= 2000
    dlm.unlock(extended_lock)


def test_unlock_with_wrong_unique_lock_id(dlm):
    lock = dlm.lock("test-resource-4", 1000)
    assert lock.resource_id == "test-resource-4"
    with pytest.raises(ResourceLockException) as exc:
        dlm.unlock(Lock(
            "test-resource-4",
            "wrong-unique-lock-id",
            0,
        ))
    assert len(exc.value.errors) == 1
    assert exc.value == ResourceLockException(
        [
            WrongUniqueLockIdException("wrong-unique-lock-id")
        ]
    )
    dlm.unlock(lock)


def test_auto_unlock(dlm):
    lock = dlm.lock("test-resource-5", 10)
    assert lock.resource_id == "test-resource-5"
    time.sleep(0.1)  # rent time has expired
    lock = dlm.lock("test-resource-5", 10)
    assert lock.resource_id == "test-resource-5"
