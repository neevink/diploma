import sys

from dlm import DistributedLockManager
from argparse import ArgumentParser

from lock import Lock


def lock_resource(redis_endpoints: list[str], resource_id: str, rent_time_ms: int, retry_count: int = 3, retry_delay: int = 200, **kwargs):
    dlm = DistributedLockManager(redis_endpoints)
    lock = dlm.lock(resource_id, rent_time_ms)
    print(lock)


def unlock_resource(redis_endpoints: list[str], resource_id: str, unique_lock_id: str, retry_count: int = 3, retry_delay: int = 200, **kwargs):
    dlm = DistributedLockManager(redis_endpoints)
    lock = Lock(resource_id, unique_lock_id)
    dlm.unlock(lock)


def main():
    parser = ArgumentParser(
        prog='dlm-client',
        description='distributed lock manager client',
    )
    parser.add_argument("--redis-endpoints", action="append", default=None,
                        help="Redis URL (eg. redis://:glsRjb9LOP@localhost:6379/0", metavar="URL")

    subparsers = parser.add_subparsers()
    parser_lock = subparsers.add_parser('lock', help='Acquire a lock')
    parser_lock.set_defaults(func=lock_resource)
    # parser_lock.add_argument("--retry-count", type=int, default=3, help="Number of retries")
    # parser_lock.add_argument("--retry-delay", type=int, default=200, help="Milliseconds between retries")
    parser_lock.add_argument("resource_id", type=str, help="Lock resource id")
    parser_lock.add_argument("rent_time_ms", type=int, help="lock rent time in milliseconds")

    parser_lock = subparsers.add_parser('unlock', help='Release a lock')
    parser_lock.set_defaults(func=unlock_resource)
    # parser_lock.add_argument("--retry-count", type=int, default=3, help="Number of retries")
    # parser_lock.add_argument("--retry-delay", type=int, default=200, help="Milliseconds between retries")
    parser_lock.add_argument("resource_id", type=str, help="Lock resource id")
    parser_lock.add_argument("unique_lock_id", type=str, help="Unique lock id")

    args = parser.parse_args()
    result = args.func(**vars(args))
    sys.exit(result)


if __name__ == '__main__':
    main()
