"""
Модель бронирования
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Text, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BookingStatus(str, enum.Enum):
    """Статус бронирования"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    TAKEN = "taken"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class Booking(Base):
    """Модель бронирования"""
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    booking_point_id = Column(UUID(as_uuid=True), ForeignKey("booking_points.id"), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    booking_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    planned_pickup_date = Column(Date, nullable=False)
    actual_pickup_date = Column(DateTime, nullable=True)
    planned_return_date = Column(Date, nullable=False)
    actual_return_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Связи
    book = relationship("Book", back_populates="bookings")
    borrower = relationship("User", back_populates="bookings_as_borrower", foreign_keys=[borrower_id])
    booking_point = relationship("BookingPoint", back_populates="bookings")
    notifications = relationship("Notification", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Booking(id={self.id}, book_id={self.book_id}, borrower_id={self.borrower_id}, status={self.status})>"
