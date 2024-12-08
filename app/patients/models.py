from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String
from app.database import (
    int_pk,
    str_nullable,
    Base
)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int_pk]
    name: Mapped[str_nullable] = mapped_column(String(60))
    sex: Mapped[str_nullable] = mapped_column(String(1))

    # relationship
    studies: Mapped[List["Study"]] = relationship(back_populates="patient")

    @validates("name")
    def validate_patient_name(self, key, patient_name):
        if (patient_name is not None) and (not 3 <= len(patient_name) <= 100):
            raise ValueError(
                "Patient name must be between 3 and 100 characters long.")
        return patient_name

    @validates("sex")
    def validate_patient_sex(self, key, patient_sex):
        if patient_sex is not None and\
                patient_sex != 'M' and patient_sex != 'F':
            raise ValueError(
                "Patient sex must be between 3 and 100 characters long.")
        return patient_sex

    def __str__(self):
        return f"Patient(id={self.id}, name={self.patient_name})"
