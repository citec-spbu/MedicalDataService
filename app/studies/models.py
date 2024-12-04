from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String, Date, Time, ARRAY
from sqlalchemy import ForeignKey
from typing import List, Optional
from app.database import Base, str_uniq, int_pk, convert_to_json
from datetime import datetime


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int_pk]
    instance_uid: Mapped[str_uniq] = mapped_column(String(64))
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(64))
    accession_number: Mapped[Optional[str]] = mapped_column(String(16))
    date: Mapped[Optional[datetime]] = mapped_column(Date)
    time: Mapped[Optional[datetime]] = mapped_column(Time)
    modalities: Mapped[List[Optional[str]]] = mapped_column(ARRAY(String(16)), server_default="{}")
    series_count: Mapped[int] = mapped_column(Integer, server_default='0')
    instances_count: Mapped[int] = mapped_column(Integer, server_default='0')

    # relationship
    patient: Mapped["Patient"] = relationship(back_populates="studies")
    series: Mapped[List["Series"]] = relationship(back_populates="study")

    def __str__(self):
        return f"Study(id={self.id}, description={self.description})"

    def to_json(self):
        return dict((
            convert_to_json("00080020", self.date.strftime("%Y%m%d") if self.date else None),
            convert_to_json("00080030", self.time.strftime("%H%M%S.%f") if self.time else None),
            convert_to_json("00080050", self.accession_number),
            convert_to_json("00080061", self.modalities if self.modalities else []),
            convert_to_json("00081030", self.description),
            convert_to_json("0020000D", self.instance_uid),
            convert_to_json("00200010", self.id),
            convert_to_json("00201206", self.series_count),
            convert_to_json("00201208", self.instances_count)
        ))