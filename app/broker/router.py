from faststream.rabbit.fastapi import RabbitRouter, Logger
from pydantic import BaseModel
from app.patients.dao import PatientDAO
from app.users.dao import UserDAO
from enum import Enum

router = RabbitRouter("amqp://guest:guest@localhost:5672/")
session_patients: set = set()
dao_types = [PatientDAO, UserDAO]


class TableType(Enum):
    PATIENTS = 0
    USERS = 1


class SqlQuery(BaseModel):
    table_type: TableType
    value: dict


@router.subscriber("sql_query")
async def receive_archive(query: SqlQuery, logger: Logger):
    await dao_types[query.table_type.value].add(**query.value)
    return {"response": "Hello, Rabbit!"}
