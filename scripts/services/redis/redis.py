import constants
import redis
import os
import pathlib
import sys
import uuid


# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils.process import SubprocessService
from scripts.utils.errors import ServiceAlreadyRunningError, ServiceNotRunningError


class RedisService:
    def __init__(self, password: str):
        self.password = password

    def connect(self) -> redis.StrictRedis:
        """
        Connect to redis through python client
        """
        # Check if Redis is running
        if not RedisService.status():
            raise ServiceNotRunningError("Redis")
        # Return Redis client
        return redis.StrictRedis(
            host=constants.REDIS_HOST,
            port=constants.REDIS_PORT,
            username=constants.REDIS_USERNAME,
            password=self.password,
            errors=constants.REDIS_ERRORS,
            charset=constants.REDIS_CHARSET,
            decode_responses=True,
            db=0,
        )

    def flush(self) -> None:
        """
        Flush Redis database
        """
        # Make sure Redis is running
        if not RedisService.status():
            raise ServiceNotRunningError("Redis")
        try:
            self.connect().flushall()
        except redis.exceptions.ConnectionError:
            raise ServiceNotRunningError("Redis")

    def stop(self) -> None:
        # Clear Redis database
        self.flush()
        # Stop Redis service, remove container and volume
        with open(f"{constants.REDIS_LOG_FILE}", "w") as log:
            SubprocessService(
                [f"docker rm -f {constants.REDIS_CONTAINER_NAME}"],
                {"stdout": log, "stderr": log, "shell": True},
            ).call()
            SubprocessService(
                [f"docker volume rm {constants.REDIS_DATA_DIR}"],
                {"stdout": log, "stderr": log, "shell": True},
            ).call()

    def init(self) -> None:
        """
        Start the Redis service through Docker
        """
        # Make sure Redis is not running
        if RedisService.status():
            raise ServiceAlreadyRunningError("Redis")
        # Create docker volume for Redis data
        with open(f"{constants.REDIS_LOG_FILE}", "w") as log:
            SubprocessService(
                [f"docker volume create {constants.REDIS_DATA_DIR}"],
                {"stdout": log, "stderr": log, "shell": True},
            ).call()
            SubprocessService(
                [
                    f"docker run -d \
                    -h redis \
                    -e REDIS_PASSWORD={self.password} \
                    -v {constants.REDIS_DATA_DIR}:/data \
                    -p {constants.REDIS_PORT}:{constants.REDIS_PORT}\
                    --name {constants.REDIS_CONTAINER_NAME} \
                    --restart always \
                    {constants.REDIS_DOCKER_IMAGE_TAG} /bin/bash -c 'redis-server --appendonly yes --requirepass ${{REDIS_PASSWORD}}'"
                ],
                {"stdout": log, "stderr": log, "shell": True},
            ).call()

    @staticmethod
    def status() -> bool:
        """
        Check if Redis is running
        """
        filename = f"{constants.REDIS_STATUS_TMP}_{uuid.uuid4()}"
        with open(filename, "w") as log:
            SubprocessService(
                [
                    "docker inspect -f '{{.State.Running}}' "
                    + f"{constants.REDIS_CONTAINER_NAME}"
                ],
                {"stdout": log, "stderr": log, "shell": True},
            ).call()
        with open(filename, "r") as log:
            status = log.read().strip()
        # Remove temporary file
        os.remove(filename)
        if status == "true":
            return True
        return False
