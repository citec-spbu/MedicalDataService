from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates
)
from sqlalchemy.types import (
    String,
    Integer
)
from sqlalchemy import ForeignKey
from app.database import (
    Base,
    int_pk,
    str_not_null
)


class Slice(Base):
    __tablename__ = "slices"

    id: Mapped[int_pk]
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"))
    number_in_series: Mapped[int] = mapped_column(Integer, nullable=False)
    slice_name: Mapped[str_not_null] = mapped_column(String(100))
    # check_sum: Mapped[str_not_null] = mapped_column(String(64))

    # relationship
    series: Mapped["Series"] = relationship(back_populates="slices")

    @validates("slice_name")
    def validate_slice_name(self, key, slice_name):
        if not 3 <= len(slice_name) <= 100:
            raise ValueError(
                "Slice name must be between 3 and 100 characters long.")
        return slice_name

    def __str__(self):
        return f"Slice(id={self.id}, name={self.slice_name})"
