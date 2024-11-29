from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String, Date, Time, ARRAY
from sqlalchemy import ForeignKey
from typing import List, Optional
from app.database import Base, str_uniq, int_pk

class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int_pk]
    instance_uid: Mapped[str_uniq] = mapped_column(String(64))
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(64))
    accession_number: Mapped[Optional[str]] = mapped_column(String(16))
    date: Mapped[Optional[Date]] = mapped_column(Date)
    time: Mapped[Optional[Time]] = mapped_column(Time)
    modalities: Mapped[List[Optional[str]]] = mapped_column(ARRAY(String(16)), server_default="{}")
    series_count: Mapped[int] = mapped_column(Integer, server_default='0')
    instances_count: Mapped[int] = mapped_column(Integer, server_default='0')


    #relationship
    patient: Mapped["Patient"] = relationship(back_populates="studies")
    series: Mapped[List["Series"]] = relationship(back_populates="study")

    def __str__(self):
        return f"Study(id={self.id}, name={self.study_name})"
    