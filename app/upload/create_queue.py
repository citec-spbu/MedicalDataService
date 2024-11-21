import pika
from app.config import rabbitmq_settings


RABBIT_URL = rabbitmq_settings.url
QUEUE_NAME = "dicom_processing"

def setup_rabbitmq():

    connection_params = pika.URLParameters(RABBIT_URL)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    try:

        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True

        )
        print(f"Очередь '{QUEUE_NAME}' успешно создана.")
    except Exception as e:
        print(f"Ошибка при создании очереди: {str(e)}")
    finally:
        connection.close()


setup_rabbitmq()
