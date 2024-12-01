from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String, Date
from app.database import Base, int_pk, convert_to_json
from datetime import datetime


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int_pk]
    name: Mapped[Optional[str]] = mapped_column(String(64))
    sex: Mapped[Optional[str]] = mapped_column(String(1))
    birth_date: Mapped[Optional[datetime]] = mapped_column(Date)
    issuer: Mapped[Optional[str]] = mapped_column(String(64))

    #relationship
    studies: Mapped[List["Study"]] = relationship(back_populates="patient")

    @validates("name")
    def validate_name(self, key, name):
        if (name is not None) and (not 3 <= len(name) <= 100):
            raise ValueError("Patient name must be between 3 and 100 characters long.")
        return name


    def __str__(self):
        return f"Patient(id={self.id}, name={self.name})"
    
    def to_json(self):
        return dict((
            convert_to_json("00100010", {"Alphabetic": self.name} if self.name != None else None),
            convert_to_json("00100020", self.id),
            convert_to_json("00100021", self.issuer),
            convert_to_json("00100030", self.birth_date.strftime("%Y%m%d")),
            convert_to_json("00100040", self.sex)
            ))
