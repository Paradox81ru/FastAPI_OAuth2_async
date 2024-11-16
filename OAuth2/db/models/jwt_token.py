from datetime import datetime
from OAuth2.db.models import Base, User
from sqlalchemy import String, SMALLINT, UUID, ForeignKey, DATETIME, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class JWTToken(Base):
    """ JWT токены """
    __tablename__ = "accounts_jwt_token"

    jti: Mapped[hex] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id"))
    expire: Mapped[datetime] = mapped_column(DATETIME)
    subject: Mapped[User] = relationship(back_populates='jwt_tokens')
