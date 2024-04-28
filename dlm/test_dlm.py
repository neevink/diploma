import pytest as pytest
from dlm import DistributedLockManager
from exceptions import ResourceAlreadyLockedException


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
    with pytest.raises(ResourceAlreadyLockedException):
        _ = dlm.lock("test-resource-2", 10)
    dlm.unlock(lock)


def test_extend(dlm):
    lock = dlm.lock("test-resource-3", 1000)
    assert lock.resource_id == "test-resource-3"
    assert lock.rent_time_ms == 1000
    extended_lock = dlm.extend(lock, 2000)
    assert extended_lock.rent_time_ms == 2000
    dlm.unlock(extended_lock)
