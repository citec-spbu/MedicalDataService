from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String, Date, Time
from sqlalchemy import ForeignKey
from typing import List, Optional
from app.database import Base, int_pk, str_uniq, convert_to_json
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from datetime import datetime

class Series(Base):
    __tablename__ = "series"

    id: Mapped[int_pk]
    instance_uid: Mapped[str_uniq] = mapped_column(String(64))
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"))
    description: Mapped[Optional[str]] = mapped_column(String(64))
    modality: Mapped[Optional[str]] = mapped_column(String(16))
    date: Mapped[Optional[datetime]] = mapped_column(Date)
    time: Mapped[Optional[datetime]] = mapped_column(Time)
    character_set: Mapped[Optional[str]] = mapped_column(String(16))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(64))
    physician_name: Mapped[Optional[str]] = mapped_column(String(64))
    manufacturer_model_name: Mapped[Optional[str]] = mapped_column(String(64))
    instances_count: Mapped[int] = mapped_column(Integer, server_default='0')


    #relationship
    study: Mapped["Study"] = relationship(back_populates="series")
    instances: Mapped[List["Instance"]] = relationship(back_populates="series")


    def __str__(self):
        return f"Series(id={self.id}, description={self.description})"
    
    def to_json(self):
        return dict((
            convert_to_json("00080005", self.character_set),
            convert_to_json("00080021", self.date.strftime("%Y%m%d") if self.date != None else None),
            convert_to_json("00080031", self.time.strftime("%H%M%S.%f") if self.time != None else None),
            convert_to_json("00080060", self.modality),
            convert_to_json("00080070", self.manufacturer),
            convert_to_json("00080090", {"Alphabetic": self.physician_name} if self.physician_name != None else None),
            convert_to_json("00081090", self.manufacturer_model_name),
            convert_to_json("0008103E", self.description),
            convert_to_json("0020000E", self.instance_uid),
            convert_to_json("00200011", self.id),
            convert_to_json("00201209", self.instances_count)
            ))


update_study_function = PGFunction(
    schema="public",
    signature="update_study()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
	UPDATE studies
    SET
	series_count = (
		SELECT count(*) FROM series
		WHERE studies.id = series.study_id), 
	instances_count = (
		SELECT sum(series.instances_count) FROM series
		WHERE studies.id = series.study_id),
	modalities = (
		SELECT ARRAY(
            SELECT distinct(series.modality) FROM series
		    WHERE studies.id = series.study_id and series.modality IS NOT NULL)
		)
    WHERE id = NEW.study_id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""
)


trigger_update_study_function = PGTrigger(
    schema="public",
    signature="trigger_update_study",
    is_constraint=False,
    on_entity="series",
    definition="""
AFTER INSERT OR UPDATE OR DELETE ON series
FOR EACH ROW
EXECUTE FUNCTION update_study();
""")

