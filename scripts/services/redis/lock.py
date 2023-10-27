import random
import redis
import uuid as id


class Lock:
    """
    Distributed lock using Redis
    """

    def __init__(self, client: redis.StrictRedis, name: str):
        self.client = client
        self.name = Lock.uuid(name)

    def acquire(self) -> bool:
        """
        Acquire lock
        """
        return self.client.setnx(self.name, 1)

    def release(self) -> bool:
        """
        Release lock
        """
        return self.client.delete(self.name)

    @staticmethod
    def uuid(name: str) -> str:
        """
        Generate UUID
        """
        r = random.Random()
        r.seed(name)
        return str(id.UUID(int=r.getrandbits(128)))
