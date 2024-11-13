from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String
from sqlalchemy import ForeignKey
from typing import List
from app.database import Base, int_pk, str_not_null

class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int_pk]
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    study_name: Mapped[str_not_null] = mapped_column(String(100))

    #relationship
    patient: Mapped["Patient"] = relationship(back_populates="studies")
    series: Mapped[List["Series"]] = relationship(back_populates="study")

    @validates("study_name")
    def validate_study_name(self, key, study_name):
        if not 3 <= len(study_name) <= 100:
            raise ValueError("Study name must be between 3 and 100 characters long.")
        return study_name


    def __str__(self):
        return f"Study(id={self.id}, name={self.study_name})"
