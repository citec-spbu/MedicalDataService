from typing import Annotated, TypeAlias
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from app.config import get_db_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncAttrs
from pydicom.datadict import dictionary_VR

DATABASE_URL: str = get_db_url()

# Asynchronous connection to the database
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Setting up annotations
int_pk: TypeAlias = Annotated[int, mapped_column(primary_key=True)]
str_uniq: TypeAlias = Annotated[str,
                                mapped_column(unique=True, nullable=False)]
str_not_null: TypeAlias = Annotated[str, mapped_column(nullable=False)]


def convert_to_json(tag, value):
    body = {"vr": dictionary_VR(tag)}
    if value != None:
        body |= {"Value": [value]}
        
    return (
        tag, body
    )

class Base(AsyncAttrs, DeclarativeBase):
    """
    An abstract class from which all database table Patients are inherited.
    """

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
    
