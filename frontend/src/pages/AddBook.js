import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useBooks } from '../contexts/BookContext';
import { validateBookData } from '../utils/bookUtils';
import './AddBook.css';

const AddBook = () => {
  const { isAuthenticated } = useAuth();
  const { createBook, uploadBookCover } = useBooks();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    description: '',
    genre: '',
    publication_year: '',
    condition: 'good',
  });
  
  const [coverFile, setCoverFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e) => {
    setCoverFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      setError('Необходима авторизация');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Валидируем и подготавливаем данные книги
      const bookData = validateBookData(formData);

      console.log('Отправляем данные книги:', bookData);
      const result = await createBook(bookData);
      console.log('Результат создания книги:', result);
      
      if (result.success) {
        // Если есть обложка, загружаем её
        if (coverFile) {
          console.log('Загружаем обложку для книги:', result.book.id);
          const coverResult = await uploadBookCover(result.book.id, coverFile);
          if (!coverResult.success) {
            console.warn('Ошибка загрузки обложки:', coverResult.error);
            // Не прерываем процесс, просто показываем предупреждение
          }
        }
        
        navigate('/my-shelf');
      } else {
        // Правильно обрабатываем ошибку
        const errorMessage = typeof result.error === 'string' 
          ? result.error 
          : JSON.stringify(result.error);
        setError(errorMessage);
      }
    } catch (err) {
      console.error('Ошибка при создании книги:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка при создании книги';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="add-book">
        <div className="container">
          <div className="auth-required">
            <h2>Необходима авторизация</h2>
            <p>Войдите в систему, чтобы добавить книгу.</p>
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/login')}
            >
              Войти
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="add-book">
      <div className="container">
        <div className="page-header">
          <h1>Добавить книгу</h1>
        </div>

        <div className="form-container">
          <form onSubmit={handleSubmit} className="book-form">
            {error && (
              <div className="error-message">
                {typeof error === 'string' ? error : JSON.stringify(error)}
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="title" className="form-label">
                  Название книги *
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="form-input"
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="author" className="form-label">
                  Автор *
                </label>
                <input
                  type="text"
                  id="author"
                  name="author"
                  value={formData.author}
                  onChange={handleChange}
                  className="form-input"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="genre" className="form-label">
                  Жанр
                </label>
                <select
                  id="genre"
                  name="genre"
                  value={formData.genre}
                  onChange={handleChange}
                  className="form-input"
                  disabled={loading}
                >
                  <option value="">Выберите жанр</option>
                  <option value="Художественная литература">Художественная литература</option>
                  <option value="Научная литература">Научная литература</option>
                  <option value="Детективы">Детективы</option>
                  <option value="Фантастика">Фантастика</option>
                  <option value="Биографии">Биографии</option>
                  <option value="История">История</option>
                  <option value="Психология">Психология</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="publication_year" className="form-label">
                  Год издания
                </label>
                <input
                  type="number"
                  id="publication_year"
                  name="publication_year"
                  value={formData.publication_year}
                  onChange={handleChange}
                  className="form-input"
                  min="1000"
                  max={new Date().getFullYear() + 1}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="condition" className="form-label">
                Состояние книги
              </label>
              <select
                id="condition"
                name="condition"
                value={formData.condition}
                onChange={handleChange}
                className="form-input"
                disabled={loading}
              >
                <option value="excellent">Отличное</option>
                <option value="good">Хорошее</option>
                <option value="fair">Удовлетворительное</option>
                <option value="poor">Плохое</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="description" className="form-label">
                Описание
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                className="form-textarea"
                rows="4"
                disabled={loading}
                placeholder="Краткое описание книги..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="cover" className="form-label">
                Обложка книги
              </label>
              <input
                type="file"
                id="cover"
                name="cover"
                onChange={handleFileChange}
                className="form-file"
                accept="image/*"
                disabled={loading}
              />
              <small className="form-help">
                Рекомендуемый размер: 800x600px. Поддерживаемые форматы: JPG, PNG
              </small>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/my-shelf')}
                disabled={loading}
              >
                Отмена
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Добавление...' : 'Добавить книгу'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddBook;
