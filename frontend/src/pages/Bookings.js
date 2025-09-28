import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useBookings } from '../contexts/BookingContext';
import './Bookings.css';

const Bookings = () => {
  const { isAuthenticated } = useAuth();
  const { fetchUserBookings, returnBook, loading, error } = useBookings();
  const [bookings, setBookings] = useState([]);

  useEffect(() => {
    if (isAuthenticated) {
      loadBookings();
    }
  }, [isAuthenticated]);

  const loadBookings = async () => {
    try {
      const data = await fetchUserBookings();
      setBookings(data);
    } catch (err) {
      console.error('Ошибка загрузки бронирований:', err);
    }
  };

  const handleReturnBook = async (bookingId) => {
    if (window.confirm('Вы уверены, что хотите вернуть эту книгу?')) {
      const result = await returnBook(bookingId);
      if (result.success) {
        alert('Книга успешно возвращена!');
        // Обновляем список бронирований
        loadBookings();
      } else {
        alert(`Ошибка: ${result.error}`);
      }
    }
  };

  const getStatusText = (status) => {
    const statusMap = {
      'PENDING': 'Ожидает подтверждения',
      'CONFIRMED': 'Подтверждено',
      'TAKEN': 'Взято',
      'RETURNED': 'Возвращено',
      'CANCELLED': 'Отменено',
    };
    return statusMap[status] || status;
  };

  const getStatusClass = (status) => {
    const classMap = {
      'PENDING': 'status-pending',
      'CONFIRMED': 'status-confirmed',
      'TAKEN': 'status-taken',
      'RETURNED': 'status-returned',
      'CANCELLED': 'status-cancelled',
    };
    return classMap[status] || '';
  };

  if (!isAuthenticated) {
    return (
      <div className="bookings">
        <div className="container">
          <div className="auth-required">
            <h2>Необходима авторизация</h2>
            <p>Войдите в систему, чтобы просмотреть бронирования.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bookings">
      <div className="container">
        <div className="page-header">
          <h1>Мои бронирования</h1>
        </div>

        {loading && (
          <div className="loading">
            <p>Загрузка бронирований...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>Ошибка: {error}</p>
          </div>
        )}

        {!loading && !error && bookings.length === 0 && (
          <div className="no-bookings">
            <h3>У вас нет бронирований</h3>
            <p>Начните с поиска интересных книг!</p>
          </div>
        )}

        {!loading && !error && bookings.length > 0 && (
          <div className="bookings-list">
            {bookings.map((booking) => (
              <div key={booking.id} className="booking-card">
                <div className="booking-header">
                  <h3 className="booking-title">
                    {booking.book?.title || 'Неизвестная книга'}
                  </h3>
                  <span className={`booking-status ${getStatusClass(booking.status)}`}>
                    {getStatusText(booking.status)}
                  </span>
                </div>
                
                <div className="booking-details">
                  <p><strong>Автор:</strong> {booking.book?.author || 'Неизвестно'}</p>
                  <p><strong>Дата бронирования:</strong> {new Date(booking.booking_date).toLocaleDateString('ru-RU')}</p>
                  <p><strong>Планируемая дата получения:</strong> {new Date(booking.planned_pickup_date).toLocaleDateString('ru-RU')}</p>
                  <p><strong>Планируемая дата возврата:</strong> {new Date(booking.planned_return_date).toLocaleDateString('ru-RU')}</p>
                  {booking.booking_point && (
                    <p><strong>Пункт выдачи:</strong> {booking.booking_point.name}</p>
                  )}
                  {booking.notes && (
                    <p><strong>Примечания:</strong> {booking.notes}</p>
                  )}
                </div>

                <div className="booking-actions">
                  {booking.status === 'TAKEN' && (
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleReturnBook(booking.id)}
                      disabled={loading}
                    >
                      {loading ? 'Возвращаем...' : 'Вернуть книгу'}
                    </button>
                  )}
                  {booking.status === 'RETURNED' && (
                    <span className="status-badge returned">
                      Книга возвращена
                    </span>
                  )}
                  {booking.status === 'CANCELLED' && (
                    <span className="status-badge cancelled">
                      Бронирование отменено
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Bookings;
