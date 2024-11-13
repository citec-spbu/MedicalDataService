from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String, DateTime, String, Date, Time
from sqlalchemy import ForeignKey
from datetime import datetime
from typing import List
from app.database import Base, int_pk, str_not_null
from sqlalchemy.sql import text

class DicomFile(Base):
    __tablename__ = "dicom_files"

    id: Mapped[int_pk]
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    file_name: Mapped[str_not_null] = mapped_column(String(255))
    upload_date: Mapped[datetime] = mapped_column(Date, nullable=False, server_default=text("(CURRENT_DATE)"))
    upload_time: Mapped[datetime] = mapped_column(Time, nullable=False, server_default=text("(CURRENT_TIME)"))
    #relationship
    uploader: Mapped["User"] = relationship(back_populates="uploaded_files")
    series: Mapped[List["Series"]] = relationship(back_populates="dicom_file")

    @validates("file_name")
    def validate_file_name(self, key, file_name):
        if not 1 <= len(file_name) <= 255:
            raise ValueError("File name must be between 1 and 255 characters long.")
        return file_name

    def __str__(self):
        return f"DicomFile(id={self.id}, file_name={self.file_name})"
