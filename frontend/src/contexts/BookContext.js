import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../config/axios';

const BookContext = createContext();

export const useBooks = () => {
  const context = useContext(BookContext);
  if (!context) {
    throw new Error('useBooks должен использоваться внутри BookProvider');
  }
  return context;
};

export const BookProvider = ({ children }) => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0,
  });

  const [filters, setFilters] = useState({
    search: '',
    genre: '',
    author: '',
    available_only: true,
  });

  // Загрузка книг
  const fetchBooks = async (params = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const queryParams = {
        page: pagination.page,
        limit: pagination.limit,
        ...filters,
        ...params,
      };

      // Удаляем пустые параметры
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === '' || queryParams[key] === null) {
          delete queryParams[key];
        }
      });

      const response = await apiClient.get('/books', { params: queryParams });
      console.log('Ответ API для книг:', response.data);
      const { books: fetchedBooks, total, page, limit, pages } = response.data;
      
      console.log('Загруженные книги:', fetchedBooks);
      setBooks(fetchedBooks);
      setPagination({ page, limit, total, pages });
    } catch (err) {
      console.error('Ошибка загрузки книг:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки книг';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    } finally {
      setLoading(false);
    }
  };

  // Загрузка книги по ID
  const fetchBook = async (bookId) => {
    try {
      const response = await apiClient.get(`/books/${bookId}`);
      return response.data;
    } catch (err) {
      console.error('Ошибка загрузки книги:', err);
      throw err;
    }
  };

  // Создание книги
  const createBook = async (bookData) => {
    try {
      const response = await apiClient.post('/books', bookData);
      // Обновляем список книг
      await fetchBooks();
      return { success: true, book: response.data };
    } catch (err) {
      console.error('Ошибка создания книги:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка создания книги';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  // Обновление книги
  const updateBook = async (bookId, bookData) => {
    try {
      const response = await apiClient.put(`/books/${bookId}`, bookData);
      // Обновляем список книг
      await fetchBooks();
      return { success: true, book: response.data };
    } catch (err) {
      console.error('Ошибка обновления книги:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка обновления книги';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  // Удаление книги
  const deleteBook = async (bookId) => {
    try {
      await apiClient.delete(`/books/${bookId}`);
      // Обновляем список книг
      await fetchBooks();
      return { success: true };
    } catch (err) {
      console.error('Ошибка удаления книги:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка удаления книги';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  // Загрузка обложки книги
  const uploadBookCover = async (bookId, file) => {
    try {
      console.log('Начинаем загрузку обложки для книги:', bookId);
      console.log('Файл:', file.name, 'Размер:', file.size, 'Тип:', file.type);
      
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Отправляем запрос на загрузку обложки...');
      const response = await apiClient.post(`/books/${bookId}/cover`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Ответ от сервера:', response.data);
      
      // Обновляем список книг
      await fetchBooks();
      return { success: true, book: response.data };
    } catch (err) {
      console.error('Ошибка загрузки обложки:', err);
      console.error('Детали ошибки:', err.response?.data);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки обложки';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  // Загрузка моих книг
  const fetchMyBooks = async () => {
    try {
      const response = await apiClient.get('/books/my/books');
      return response.data.books;
    } catch (err) {
      console.error('Ошибка загрузки моих книг:', err);
      throw err;
    }
  };

  // Обновление фильтров
  const updateFilters = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  // Сброс фильтров
  const resetFilters = () => {
    setFilters({
      search: '',
      genre: '',
      author: '',
      available_only: true,
    });
  };

  // Изменение страницы
  const changePage = (page) => {
    setPagination(prev => ({ ...prev, page }));
  };

  // Загрузка книг при изменении фильтров или страницы
  useEffect(() => {
    fetchBooks();
  }, [filters, pagination.page]);

  const value = {
    books,
    loading,
    error,
    pagination,
    filters,
    fetchBooks,
    fetchBook,
    createBook,
    updateBook,
    deleteBook,
    uploadBookCover,
    fetchMyBooks,
    updateFilters,
    resetFilters,
    changePage,
  };

  return (
    <BookContext.Provider value={value}>
      {children}
    </BookContext.Provider>
  );
};
