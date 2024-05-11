class ResourceLockException(Exception):
    def __init__(self, errors: list[Exception], *args):
        super(ResourceLockException, self).__init__(*args)
        self.errors = errors

    def __eq__(self, other):
        if not isinstance(other, ResourceLockException):
            return NotImplemented
        return str(self) == str(other)

    def __str__(self):
        return f'ResourceLockException([{ ",".join(sorted([str(e) for e in self.errors])) }])'

    def __repr__(self):
        return self.__str__()


class ResourceAlreadyLockedException(Exception):
    def __init__(self, *args):
        super(ResourceAlreadyLockedException, self).__init__(*args)

    def __eq__(self, other):
        if not isinstance(other, ResourceAlreadyLockedException):
            return NotImplemented
        return True

    def __str__(self):
        return f'ResourceAlreadyLockedException()'

    def __repr__(self):
        return self.__str__()


class WrongUniqueLockIdException(Exception):
    def __init__(self, unique_lock_id: str, *args):
        super(WrongUniqueLockIdException, self).__init__(*args)
        self.unique_lock_id = unique_lock_id

    def __eq__(self, other):
        if not isinstance(other, WrongUniqueLockIdException):
            return NotImplemented
        return self.unique_lock_id == other.unique_lock_id

    def __str__(self):
        return f'WrongUniqueLockIdException({self.unique_lock_id})'

    def __repr__(self):
        return self.__str__()
