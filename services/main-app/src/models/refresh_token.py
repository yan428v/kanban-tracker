from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import relationship

from models import Base, BaseModelMixin


class RefreshToken(Base, BaseModelMixin):
    __tablename__ = "refresh_token"

    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token_jti = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
