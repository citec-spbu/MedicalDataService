from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey
from app.database import Base, int_pk, str_not_null, str_uniq
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger


class Instance(Base):
    __tablename__ = "instances"

    id: Mapped[int_pk]
    sop_instance_uid: Mapped[str_uniq] = mapped_column(String(64))
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id"))
    dicom_file_id: Mapped[int] = mapped_column(ForeignKey("dicom_files.id"))
    dicom_file_name: Mapped[int] = mapped_column(String(64))
    check_sum: Mapped[str_not_null] = mapped_column(String(64))
    metadata_: Mapped[dict] = mapped_column(JSONB)
    pixel_data_path: Mapped[str_not_null] = mapped_column(String(512))

    # relationship
    series: Mapped["Series"] = relationship(back_populates="instances")
    dicom_file: Mapped["DicomFile"] = relationship(back_populates="instances")

    def __str__(self):
        return f"Instance(id={self.id}, sop_uid={self.sop_instance_uid})"


update_series_function = PGFunction(
    schema="public",
    signature="update_series()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
	UPDATE series
    SET
	instances_count = (
		SELECT COUNT(*) FROM instances
		WHERE series.id = instances.series_id)
    WHERE id = NEW.series_id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
""")

trigger_update_series_function = PGTrigger(
    schema="public",
    signature="trigger_update_series",
    is_constraint=False,
    on_entity="public.instances",
    definition="""
AFTER INSERT OR UPDATE OR DELETE ON instances
FOR EACH ROW
EXECUTE FUNCTION update_series();
""")