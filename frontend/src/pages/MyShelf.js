import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useBooks } from '../contexts/BookContext';
import BookCard from '../components/BookCard';
import './MyShelf.css';

const MyShelf = () => {
  const { user, isAuthenticated } = useAuth();
  const { createBook, uploadBookCover } = useBooks();
  const [myBooks, setMyBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchMyBooks();
    }
  }, [isAuthenticated]);

  const fetchMyBooks = async () => {
    try {
      setLoading(true);
      const response = await fetch('/books/my/books', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Ошибка загрузки книг');
      }
      
      const data = await response.json();
      setMyBooks(data.books);
    } catch (err) {
      console.error('Ошибка загрузки моих книг:', err);
      setError('Ошибка загрузки книг');
    } finally {
      setLoading(false);
    }
  };

  const handleBookAction = (book, action) => {
    console.log(`Действие ${action} для книги:`, book);
    // Здесь будет логика для управления книгой
  };

  if (!isAuthenticated) {
    return (
      <div className="my-shelf">
        <div className="container">
          <div className="auth-required">
            <h2>Необходима авторизация</h2>
            <p>Войдите в систему, чтобы просмотреть свои книги.</p>
            <Link to="/login" className="btn btn-primary">
              Войти
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="my-shelf">
      <div className="container">
        <div className="page-header">
          <h1>Моя полка</h1>
          <Link to="/add-book" className="btn btn-primary">
            Добавить книгу
          </Link>
        </div>

        {loading && (
          <div className="loading">
            <p>Загрузка ваших книг...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>Ошибка: {error}</p>
          </div>
        )}

        {!loading && !error && myBooks.length === 0 && (
          <div className="no-books">
            <h3>У вас пока нет книг</h3>
            <p>Добавьте первую книгу, чтобы начать обмен!</p>
            <Link to="/add-book" className="btn btn-primary">
              Добавить книгу
            </Link>
          </div>
        )}

        {!loading && !error && myBooks.length > 0 && (
          <div className="books-section">
            <div className="books-stats">
              <p>Всего книг: {myBooks.length}</p>
              <p>Доступно для обмена: {myBooks.filter(book => book.is_available).length}</p>
            </div>
            
            <div className="book-grid">
              {myBooks.map((book) => (
                <BookCard
                  key={book.id}
                  book={book}
                  onBookAction={handleBookAction}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyShelf;
