# Model describes table structure
# import enum
# from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, validates, mapped_column
from sqlalchemy.types import String
from app.database import Base, int_pk, str_uniq, str_not_null


# class UserRole(enum.Enum):
#     technical = 0
#     uploader = 1
#     moderator = 2
#     admin = 3


# TODO add roles column
class User(Base):
    id: Mapped[int_pk]
    nickname: Mapped[str_uniq] = mapped_column(String(40))
    password: Mapped[str_not_null] = mapped_column(String(60))
    # role: Mapped[UserRole] = mapped_column(
    #     Enum(UserRole), server_default="technical")

    @validates("nickname")
    def validate_nickname(self, key, nickname):
        """
        Check that nickname >= 3 characters long
        """
        min_nickname_len: int = 3
        if len(nickname) < min_nickname_len:
            raise ValueError(f"The nickname must be at least\
                             {min_nickname_len} characters long.")
        return nickname

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"nickname={self.nickname}")

    def __repr__(self):
        return str(self)
