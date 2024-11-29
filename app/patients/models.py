from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String, Date
from app.database import Base, int_pk


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int_pk]
    name: Mapped[Optional[str]] = mapped_column(String(64))
    sex: Mapped[Optional[str]] = mapped_column(String(1))
    birth_date: Mapped[Optional[Date]] = mapped_column(Date)
    issuer: Mapped[Optional[str]] = mapped_column(String(64))

    #relationship
    studies: Mapped[List["Study"]] = relationship(back_populates="patient")

    @validates("patient_name")
    def validate_patient_name(self, key, patient_name):
        if (patient_name is not None) and (not 3 <= len(patient_name) <= 100):
            raise ValueError("Patient name must be between 3 and 100 characters long.")
        return patient_name


    def __str__(self):
        return f"Patient(id={self.id}, name={self.patient_name})"
