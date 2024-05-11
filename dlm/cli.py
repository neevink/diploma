import logging
import sys

from dlm import DistributedLockManager
from argparse import ArgumentParser

from exceptions import ResourceLockException
from lock import Lock


def setup_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    return root_logger


logger = setup_logger()


def lock_resource(redis_endpoints: list[str], resource_id: str, rent_time_ms: int, **kwargs):
    dlm = DistributedLockManager(redis_endpoints)
    try:
        lock = dlm.lock(resource_id, rent_time_ms)
        logger.info(f'Resource `{resource_id}` was successfully locked!')
        logger.info(lock)
    except ResourceLockException as exc:
        logger.fatal(f'Can not lock resource `{resource_id}`: {exc}')
        sys.exit(-1)


def unlock_resource(redis_endpoints: list[str], resource_id: str, unique_lock_id: str, **kwargs):
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
    parser_lock.add_argument("resource_id", type=str, help="Lock resource id")
    parser_lock.add_argument("rent_time_ms", type=int, help="lock rent time in milliseconds")

    parser_lock = subparsers.add_parser('unlock', help='Release a lock')
    parser_lock.set_defaults(func=unlock_resource)
    parser_lock.add_argument("resource_id", type=str, help="Lock resource id")
    parser_lock.add_argument("unique_lock_id", type=str, help="Unique lock id")

    args = parser.parse_args()
    result = args.func(**vars(args))
    sys.exit(result)


if __name__ == '__main__':
    main()
