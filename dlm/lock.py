from dataclasses import dataclass


@dataclass
class Lock:
    resource_id: str
    unique_lock_id: str
    rent_time_ms: int = 0
