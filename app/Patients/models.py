from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String
from sqlalchemy import ForeignKey
from app.database import Base, int_pk, str_not_null


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int_pk]
    patient_name: Mapped[str_not_null] = mapped_column(String(100))

    #relationship
    studies: Mapped[List["Study"]] = relationship(back_populates="patient")

    @validates("patient_name")
    def validate_patient_name(self, key, patient_name):
        if not 3 <= len(patient_name) <= 100:
            raise ValueError("Patient name must be between 3 and 100 characters long.")
        return patient_name


    def __str__(self):
        return f"Patient(id={self.id}, name={self.patient_name})"
