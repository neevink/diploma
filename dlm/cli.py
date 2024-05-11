import logging
import sys
from argparse import ArgumentParser

from dlm import DistributedLockManager
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
    try:
        lock = Lock(resource_id, unique_lock_id)
        new_lock = dlm.unlock(lock)
        logger.info(f'Resource `{resource_id}` was successfully unlocked!')
        logger.info(new_lock)
    except ResourceLockException as exc:
        logger.fatal(f'Can not unlock resource `{resource_id}`: {exc}')
        sys.exit(-1)


def extend_lock(redis_endpoints: list[str], resource_id: str, unique_lock_id: str, new_rent_time_ms: int, **kwargs):
    dlm = DistributedLockManager(redis_endpoints)
    try:
        lock = Lock(resource_id, unique_lock_id)
        new_lock = dlm.extend(lock, new_rent_time_ms)
        logger.info(f'Resource lock `{resource_id}` was successfully extended!')
        logger.info(new_lock)
    except ResourceLockException as exc:
        logger.fatal(f'Can not extend lock `{resource_id}`: {exc}')
        sys.exit(-1)


def main():
    parser = ArgumentParser(
        prog='dlm-client',
        description='distributed lock manager client',
    )
    parser.add_argument("--redis-endpoints", action="append", default=None,
                        help="Redis URL (eg. redis://:glsRjb9LOP@localhost:6379/0", metavar="URL")

    subparsers = parser.add_subparsers()
    parser_lock = subparsers.add_parser('lock', help='acquire lock')
    parser_lock.set_defaults(func=lock_resource)
    parser_lock.add_argument("resource_id", type=str, help="resource id")
    parser_lock.add_argument("rent_time_ms", type=int, help="lock rent time in milliseconds")

    parser_unlock = subparsers.add_parser('unlock', help='release lock')
    parser_unlock.set_defaults(func=unlock_resource)
    parser_unlock.add_argument("resource_id", type=str, help="resource id")
    parser_unlock.add_argument("unique_lock_id", type=str, help="unique lock id")

    parser_extend = subparsers.add_parser('extend', help='extend lock')
    parser_extend.set_defaults(func=extend_lock)
    parser_extend.add_argument("resource_id", type=str, help="resource id")
    parser_extend.add_argument("unique_lock_id", type=str, help="unique lock id")
    parser_extend.add_argument("new_rent_time_ms", type=int, help="new lock rent time in milliseconds")

    args = parser.parse_args()
    result = args.func(**vars(args))
    sys.exit(result)


if __name__ == '__main__':
    main()
