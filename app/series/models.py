from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String, Integer, DateTime, Date, Time, ARRAY
from sqlalchemy import ForeignKey
from datetime import datetime
from typing import List
from app.database import Base, int_pk, str_not_null
from sqlalchemy.sql import text
class Series(Base):
    __tablename__ = "series"

    id: Mapped[int_pk]
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"))
    dicom_file_id: Mapped[int] = mapped_column(ForeignKey("dicom_files.id"))
    creation_date: Mapped[datetime] = mapped_column(Date, nullable=False, server_default=text("(CURRENT_DATE)"))
    creation_time: Mapped[datetime] = mapped_column(Time, nullable=False, server_default=text("(CURRENT_TIME)"))
    scale: Mapped[int] = mapped_column(ARRAY(Integer, dimensions=1))
    series_name: Mapped[str_not_null] = mapped_column(String(100))

    #relationship
    study: Mapped["Study"] = relationship(back_populates="series")
    dicom_file: Mapped["DicomFile"] = relationship(back_populates="series")
    slices: Mapped[List["Slice"]] = relationship(back_populates="series")

    @validates("series_name")
    def validate_series_name(self, key, series_name):
        if not 3 <= len(series_name) <= 100:
            raise ValueError("Series name must be between 3 and 100 characters long.")
        return series_name

    @validates("scale")
    def validate_scale(self, key, scale):
        if not 1 <= scale <= 100:
            raise ValueError("Scale must be between 1 and 100.")
        return scale


    def __str__(self):
        return f"Series(id={self.id}, name={self.series_name})"
