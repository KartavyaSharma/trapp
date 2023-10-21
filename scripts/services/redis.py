import redis
import subprocess
import os

import constants.constants as constants


class RedisService:

    def __init__(self, password: str):
        self.password = password

    def connect(self) -> redis.StrictRedis:
        """
        Connect to redis through python client
        """
        # Check if Redis is running
        if not self.status():
            raise Exception("Redis is not running")
        return redis.StrictRedis(
            host=constants.REDIS_HOST,
            port=constants.REDIS_PORT,
            db=0,
            password=self.password,
            errors="strict",
        )

    def flush(self) -> None:
        """
        Flush Redis database
        """
        # Make sure Redis is running
        if not self.status():
            raise Exception("Redis is not running")
        with open(f"{constants.REDIS_LOG_FILE}", "a") as log:
            subprocess.call(f"docker exec \
                            -it {constants.REDIS_CONTAINER_NAME} \
                            /bin/sh -c 'export REDISCLI_AUTH={self.password}; redis-cli flushall; unset REDISCLI_AUTH'",
                            shell=True, stdout=log, stderr=log)

    def stop(self) -> None:
        # Clear Redis database
        self.flush()
        # Stop Redis service, remove container and volume
        with open(f"{constants.REDIS_LOG_FILE}", "a") as log:
            subprocess.call(
                f"docker rm -f {constants.REDIS_CONTAINER_NAME}", shell=True, stdout=log, stderr=log)
            subprocess.call(
                f"docker volume rm {constants.REDIS_DATA_DIR}", shell=True, stdout=log, stderr=log)

    def init(password: str) -> None:
        """
        Start the Redis service through Docker
        """
        # Make sure Redis is not running
        if RedisService.status():
            raise Exception("Redis is already running")
        # Create docker volume for Redis data
        with open(f"{constants.REDIS_LOG_FILE}", "a") as log:
            subprocess.call(f"docker volume create {constants.REDIS_DATA_DIR}",
                            shell=True, stdout=log, stderr=log)
            subprocess.call(f"docker run -d \
                            -h redis \
                            -e REDIS_PASSWORD=redis \
                            -v {constants.REDIS_DATA_DIR}:/data \
                            -p {constants.REDIS_PORT}:{constants.REDIS_PORT}\
                            --name {constants.REDIS_CONTAINER_NAME} \
                            --restart always \
                            redis:5.0.5-alpine3.9 /bin/sh -c 'redis-server --appendonly yes --requirepass {password}'",
                            shell=True, stdout=log, stderr=log)

    def status() -> bool:
        """
        Check if Redis is running
        """
        with open(f"{constants.REDIS_STATUS_TMP}", "a") as log:
            subprocess.call(f"docker inspect -f '{{.State.Running}}' {constants.REDIS_CONTAINER_NAME}",
                            shell=True, stdout=log, stderr=log)
        with open("logs/redis.log", "r") as log:
            status = log.read().strip()
        # Remove temporary file
        os.remove(f"{constants.REDIS_STATUS_TMP}")
        if status == "true":
            return True
        else:
            return False
