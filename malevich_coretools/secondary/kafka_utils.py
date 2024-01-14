from typing import Generator, Optional

from kafka import KafkaConsumer

from malevich_coretools.abstract import AppLogs
from malevich_coretools.secondary import Config


def __logs_topic(operation_id: str) -> str:
    return f"{operation_id}-logs"


def handle_logs(operation_id: str, kafka_host_port: Optional[str] = None) -> Generator[AppLogs, None, None]:
    if kafka_host_port is None:
        kafka_host_port = Config.KAFKA_HOST_PORT
    assert kafka_host_port is not None, "kafka_host_port not set"

    topic = __logs_topic(operation_id)
    consumer = KafkaConsumer(topic, bootstrap_servers=kafka_host_port)

    try:
        for message in consumer:
            if message.value == b'end':
                return
            try:
                logs = AppLogs.model_validate_json(message.value)
            except BaseException as ex:
                Config.logger.error(message.value)
                raise ex
            yield logs
    except KeyboardInterrupt:
        pass
