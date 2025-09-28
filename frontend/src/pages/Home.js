import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useBooks } from '../contexts/BookContext';
import { useAuth } from '../contexts/AuthContext';
import { useBookings } from '../contexts/BookingContext';
import BookCard from '../components/BookCard';
import BookingModal from '../components/BookingModal';
import './Home.css';

const Home = () => {
  const { books, loading, error, filters, updateFilters, resetFilters } = useBooks();
  const { isAuthenticated, user } = useAuth();
  const { returnBook } = useBookings();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBooks, setSelectedBooks] = useState(new Set());
  const [showBookingModal, setShowBookingModal] = useState(false);

  // Инициализация поискового запроса из URL
  useEffect(() => {
    const search = searchParams.get('search');
    if (search) {
      setSearchQuery(search);
      updateFilters({ search });
    }
  }, [searchParams, updateFilters]);

  const handleSearch = (e) => {
    e.preventDefault();
    updateFilters({ search: searchQuery });
    setSearchParams({ search: searchQuery });
  };

  const handleFilterChange = (filterName, value) => {
    updateFilters({ [filterName]: value });
  };

  const handleBookAction = (book, action) => {
    console.log(`Действие ${action} для книги:`, book);
    console.log('Текущие выбранные книги:', Array.from(selectedBooks));
    
    // Проверяем аутентификацию
    if (!isAuthenticated) {
      alert('Для бронирования книг необходимо войти в систему');
      return;
    }
    
    if (action === 'select') {
      // Добавляем книгу в выбранные
      setSelectedBooks(prev => {
        const newSet = new Set([...prev, book.id]);
        console.log('Новые выбранные книги:', Array.from(newSet));
        return newSet;
      });
    } else if (action === 'deselect') {
      // Убираем книгу из выбранных
      setSelectedBooks(prev => {
        const newSet = new Set(prev);
        newSet.delete(book.id);
        console.log('Новые выбранные книги после отмены:', Array.from(newSet));
        return newSet;
      });
    }
  };

  const handleReturnBook = async (bookingId) => {
    if (window.confirm('Вы уверены, что хотите вернуть эту книгу?')) {
      const result = await returnBook(bookingId);
      if (result.success) {
        alert('Книга успешно возвращена!');
        // Обновляем список книг
        window.location.reload();
      } else {
        alert(`Ошибка: ${result.error}`);
      }
    }
  };

  return (
    <div className="home">
      {/* Героическая секция */}
      <section className="hero-section">
        <div className="container">
          <h1 className="hero-title">BookSwap</h1>
          <p className="hero-subtitle">
            Обменивайтесь книгами с другими читателями
          </p>
        </div>
      </section>

      {/* Поиск и фильтры */}
      <section className="search-section">
        <div className="container">
          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              className="search-input"
              placeholder="Ищете что-то? Напишите: Автор — Название"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="search-btn">
              Найти
            </button>
          </form>

          <div className="filters">
            <select
              className="filter-select"
              value={filters.genre}
              onChange={(e) => handleFilterChange('genre', e.target.value)}
            >
              <option value="">Все жанры</option>
              <option value="Художественная литература">Художественная литература</option>
              <option value="Научная литература">Научная литература</option>
              <option value="Детективы">Детективы</option>
              <option value="Фантастика">Фантастика</option>
              <option value="Биографии">Биографии</option>
              <option value="История">История</option>
              <option value="Психология">Психология</option>
            </select>

            <select
              className="filter-select"
              value={filters.available_only ? 'true' : 'false'}
              onChange={(e) => handleFilterChange('available_only', e.target.value === 'true')}
            >
              <option value="true">Только доступные</option>
              <option value="false">Все книги</option>
            </select>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={resetFilters}
            >
              Сбросить фильтры
            </button>
          </div>
        </div>
      </section>

      {/* Секция популярных книг */}
      <section className="section">
        <div className="container">
          <div className="section-title">
            <h2>Самое популярное:</h2>
            <div className="section-actions">
              <div style={{ marginRight: '10px', fontSize: '14px', color: '#666' }}>
                Выбрано: {selectedBooks.size} книг
              </div>
              {selectedBooks.size > 0 && (
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    console.log('Клик по кнопке "Забронировать выбранные"');
                    console.log('isAuthenticated:', isAuthenticated);
                    console.log('selectedBooks.size:', selectedBooks.size);
                    
                    if (!isAuthenticated) {
                      alert('Для бронирования книг необходимо войти в систему');
                      return;
                    }
                    
                    console.log('Открываем модальное окно бронирования');
                    setShowBookingModal(true);
                  }}
                >
                  Забронировать выбранные ({selectedBooks.size})
                </button>
              )}
              <button className="btn btn-secondary">Добавить</button>
            </div>
          </div>

          {loading && (
            <div className="loading">
              <p>Загрузка книг...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>Ошибка: {error}</p>
            </div>
          )}

          {!loading && !error && books.length === 0 && (
            <div className="no-books">
              <p>Книги не найдены. Попробуйте изменить параметры поиска.</p>
            </div>
          )}

          {!loading && !error && books.length > 0 && (
            <div className="book-grid">
              {books.map((book) => {
                console.log('Рендеринг книги:', book.id, 'isSelected:', selectedBooks.has(book.id));
                return (
                  <BookCard
                    key={book.id}
                    book={book}
                    onBookAction={handleBookAction}
                    isSelected={selectedBooks.has(book.id)}
                    currentUserId={user?.id}
                    onReturnBook={handleReturnBook}
                  />
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Модальное окно бронирования */}
      <BookingModal
        isOpen={showBookingModal}
        onClose={() => setShowBookingModal(false)}
        selectedBooks={selectedBooks}
        onBookingSuccess={() => {
          setSelectedBooks(new Set());
          // Можно добавить обновление списка книг
        }}
      />
    </div>
  );
};

export default Home;
