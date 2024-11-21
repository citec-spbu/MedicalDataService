from faststream.rabbit import RabbitBroker
from app.config import rabbitmq_settings

broker = RabbitBroker(rabbitmq_settings.url)