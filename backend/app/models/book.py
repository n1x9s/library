"""
Модель книги
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BookCondition(str, enum.Enum):
    """Состояние книги"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class Book(Base):
    """Модель книги"""

    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True, index=True)
    publication_year = Column(Integer, nullable=True)
    condition = Column(Enum(BookCondition), nullable=False, default=BookCondition.GOOD)
    cover_image_url = Column(String(500), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Связи
    owner = relationship("User", back_populates="books")
    bookings = relationship(
        "Booking", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author})>"
