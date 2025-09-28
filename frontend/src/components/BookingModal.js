import React, { useState, useEffect } from 'react';
import { useBookings } from '../contexts/BookingContext';
import './BookingModal.css';

const BookingModal = ({ isOpen, onClose, selectedBooks, onBookingSuccess }) => {
  const { createBooking, fetchBookingPoints, loading } = useBookings();
  const [bookingPoints, setBookingPoints] = useState([]);
  const [formData, setFormData] = useState({
    planned_pickup_date: '',
    planned_return_date: '',
    booking_point_id: '',
    notes: '',
  });
  const [error, setError] = useState('');

  // Загружаем пункты выдачи при открытии модального окна
  useEffect(() => {
    if (isOpen) {
      loadBookingPoints();
    }
  }, [isOpen]);

  const loadBookingPoints = async () => {
    try {
      const points = await fetchBookingPoints();
      setBookingPoints(points);
    } catch (err) {
      console.error('Ошибка загрузки пунктов выдачи:', err);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Валидация
    if (!formData.planned_pickup_date || !formData.planned_return_date || !formData.booking_point_id) {
      setError('Пожалуйста, заполните все обязательные поля');
      return;
    }

    if (new Date(formData.planned_pickup_date) < new Date()) {
      setError('Дата получения не может быть в прошлом');
      return;
    }

    if (new Date(formData.planned_return_date) <= new Date(formData.planned_pickup_date)) {
      setError('Дата возврата должна быть позже даты получения');
      return;
    }

    try {
      // Создаем бронирования для каждой выбранной книги
      const bookingPromises = Array.from(selectedBooks).map(bookId => 
        createBooking({
          book_id: bookId,
          planned_pickup_date: formData.planned_pickup_date,
          planned_return_date: formData.planned_return_date,
          booking_point_id: formData.booking_point_id,
          notes: formData.notes,
        })
      );

      const results = await Promise.all(bookingPromises);
      
      // Проверяем, все ли бронирования созданы успешно
      const failedBookings = results.filter(result => !result.success);
      
      if (failedBookings.length > 0) {
        setError(`Не удалось забронировать ${failedBookings.length} книг`);
        return;
      }

      // Успешно созданы все бронирования
      alert(`Успешно забронировано ${results.length} книг!`);
      onBookingSuccess();
      onClose();
      
    } catch (err) {
      console.error('Ошибка создания бронирований:', err);
      setError('Ошибка при создании бронирований');
    }
  };

  const handleClose = () => {
    setFormData({
      planned_pickup_date: '',
      planned_return_date: '',
      booking_point_id: '',
      notes: '',
    });
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Бронирование книг</h2>
          <button className="modal-close" onClick={handleClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="planned_pickup_date" className="form-label">
              Дата получения *
            </label>
            <input
              type="date"
              id="planned_pickup_date"
              name="planned_pickup_date"
              value={formData.planned_pickup_date}
              onChange={handleChange}
              className="form-input"
              required
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="form-group">
            <label htmlFor="planned_return_date" className="form-label">
              Дата возврата *
            </label>
            <input
              type="date"
              id="planned_return_date"
              name="planned_return_date"
              value={formData.planned_return_date}
              onChange={handleChange}
              className="form-input"
              required
              min={formData.planned_pickup_date || new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="form-group">
            <label htmlFor="booking_point_id" className="form-label">
              Пункт выдачи *
            </label>
            <select
              id="booking_point_id"
              name="booking_point_id"
              value={formData.booking_point_id}
              onChange={handleChange}
              className="form-input"
              required
            >
              <option value="">Выберите пункт выдачи</option>
              {bookingPoints.map(point => (
                <option key={point.id} value={point.id}>
                  {point.name} - {point.address}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="notes" className="form-label">
              Примечания
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              className="form-textarea"
              rows="3"
              placeholder="Дополнительная информация..."
            />
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClose}
              disabled={loading}
            >
              Отмена
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Создание...' : `Забронировать ${selectedBooks.size} книг`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BookingModal;