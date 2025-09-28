import React from 'react';
import { Link } from 'react-router-dom';
import './BookCard.css';

const BookCard = ({ book, onBookAction, isSelected = false, currentUserId = null, onReturnBook = null }) => {
  const getStatusButton = () => {
    if (!book.is_available) {
      return (
        <button className="status-btn unavailable" disabled>
          Недоступна
        </button>
      );
    }

    // Проверяем, есть ли активное бронирование текущим пользователем
    const myActiveBooking = book.bookings && book.bookings.find(
      booking => (booking.status === 'PENDING' || booking.status === 'CONFIRMED' || booking.status === 'TAKEN') 
                 && currentUserId && booking.borrower_id === currentUserId
    );

    if (myActiveBooking) {
      if (myActiveBooking.status === 'TAKEN') {
        // Показываем кнопку "Вернуть" для взятых книг
        return (
          <button 
            className="status-btn return"
            onClick={() => {
              console.log('Возврат книги:', myActiveBooking.id);
              onReturnBook && onReturnBook(myActiveBooking.id);
            }}
          >
            Вернуть
          </button>
        );
      } else {
        // Показываем статус для ожидающих подтверждения
        const returnDate = new Date(myActiveBooking.planned_return_date).toLocaleDateString('ru-RU');
        return (
          <button className="status-btn reserved" disabled>
            Забронирована до {returnDate}
          </button>
        );
      }
    }

    // Проверяем, есть ли активное бронирование другими пользователями
    const hasOtherActiveBooking = book.bookings && book.bookings.some(
      booking => (booking.status === 'PENDING' || booking.status === 'CONFIRMED' || booking.status === 'TAKEN')
                 && (!currentUserId || booking.borrower_id !== currentUserId)
    );

    if (hasOtherActiveBooking) {
      return (
        <button className="status-btn unavailable" disabled>
          Забронирована
        </button>
      );
    }

    // Если книга выбрана, показываем кнопку "Выбрано"
    if (isSelected) {
      return (
        <button 
          className="status-btn selected"
          onClick={() => {
            console.log('Клик по кнопке "Выбрано" для книги:', book.id);
            onBookAction && onBookAction(book, 'deselect');
          }}
        >
          Выбрано
        </button>
      );
    }

    // Если книга доступна и не выбрана, показываем кнопку "Выбрать"
    return (
      <button 
        className="status-btn available"
        onClick={() => {
          console.log('Клик по кнопке "Выбрать" для книги:', book.id);
          onBookAction && onBookAction(book, 'select');
        }}
      >
        Выбрать
      </button>
    );
  };

  const getCoverImage = () => {
    if (book.cover_image_url) {
      return (
        <img 
          src={`http://localhost:8000${book.cover_image_url}`} 
          alt={`Обложка ${book.title}`}
          className="book-cover"
        />
      );
    }
    
    return (
      <div className="book-cover-placeholder">
        <span className="book-cover-text">
          {book.title.charAt(0).toUpperCase()}
        </span>
      </div>
    );
  };

  return (
    <div className="book-card">
      <Link to={`/book/${book.id}`} className="book-link">
        {getCoverImage()}
        <div className="book-info">
          <h3 className="book-title">{book.title}</h3>
          <p className="book-author">{book.author}</p>
          {book.publication_year && (
            <p className="book-year">{book.publication_year}</p>
          )}
          {book.genre && (
            <p className="book-genre">{book.genre}</p>
          )}
        </div>
      </Link>
      <div className="book-status">
        {getStatusButton()}
      </div>
    </div>
  );
};

export default BookCard;
