from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import (
    Float,
    Enum as SQLEnum
)
from sqlalchemy import ForeignKey
from app.database import (
    Base,
    int_pk
)
from enum import Enum


class RequestType(Enum):
    PROCESSING = 0
    ANALYSIS = 1
    EXPORT = 2


class DeferredOperation(Base):
    __tablename__ = "deferred_operations"

    id: Mapped[int_pk]
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    loading_state: Mapped[float] = mapped_column(Float, server_default="0.0")
    request_type: Mapped[RequestType] = mapped_column(SQLEnum(RequestType))

    # relationship
    requester: Mapped["User"] = relationship(
        back_populates="deferred_operations"
    )

    def __str__(self):
        return f"DeferredOperation(id={self.id}, type={self.request_type})"
