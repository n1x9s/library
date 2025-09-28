"""
Модель пункта выдачи
"""

import uuid
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class BookingPoint(Base):
    """Модель пункта выдачи"""

    __tablename__ = "booking_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    coordinates = Column(String(100), nullable=True)  # "lat,lng" format
    working_hours = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    bookings = relationship("Booking", back_populates="booking_point")

    def __repr__(self):
        return f"<BookingPoint(id={self.id}, name={self.name})>"
