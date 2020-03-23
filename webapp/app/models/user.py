from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(64), index=True)
    email = Column(String(64), unique=True, index=True)
    hashed_password = Column(String(128))
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    sources = relationship("Source", back_populates="owner")
