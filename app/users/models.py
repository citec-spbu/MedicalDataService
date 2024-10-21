from sqlalchemy.orm import Mapped, validates, mapped_column
from app.database import Base, int_pk, str_uniq, str_not_null
from sqlalchemy.types import String


# TODO add roles column
# TODO store passwords in hash
class User(Base):
    id: Mapped[int_pk]
    nickname: Mapped[str_uniq] = mapped_column(String(40))
    password: Mapped[str_not_null] = mapped_column(String(80))

    @validates("nickname")
    def nickname_validator(self, key, nickname):
        """
        Check that nickname >= 3 characters long
        """
        min_nickname_len: int = 3
        if len(nickname) < min_nickname_len:
            raise ValueError(f"The nickname must be at least\
                             {min_nickname_len} characters long.")
        return nickname

    @validates("password")
    def password_validator(self, key, password):
        """
        Check that password >= 8 characters long
        """
        min_password_len: int = 8
        if len(password) < min_password_len:
            raise ValueError(f"The password must be at least\
                    {min_password_len} characters long.")
        return password

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"nickname={self.nickname}")

    def __repr__(self):
        return str(self)
