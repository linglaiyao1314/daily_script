from sqlalchemy import Column, Integer, ForeignKey, String, Text, Time
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))
    description = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    genre = Column(Integer)
    genre_detail = Column(Text)
    status = Column(Integer)
    created_at = Column(Time)
    updated_at = Column(Time)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="sources")


