import React, { createContext, useContext, useState } from 'react';
import apiClient from '../config/axios';

const BookingContext = createContext();

export const useBookings = () => {
  const context = useContext(BookingContext);
  if (!context) {
    throw new Error('useBookings должен использоваться внутри BookingProvider');
  }
  return context;
};

export const BookingProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Получение бронирований пользователя
  const fetchUserBookings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get('/bookings');
      return response.data.bookings;
    } catch (err) {
      console.error('Ошибка загрузки бронирований:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки бронирований';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Создание бронирования
  const createBooking = async (bookingData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post('/bookings', bookingData);
      return { success: true, booking: response.data };
    } catch (err) {
      console.error('Ошибка создания бронирования:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка создания бронирования';
      const errorString = typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
      setError(errorString);
      return { success: false, error: errorString };
    } finally {
      setLoading(false);
    }
  };

  // Возврат книги
  const returnBook = async (bookingId) => {
    try {
      setLoading(true);
      setError(null);
      
      await apiClient.post(`/bookings/${bookingId}/confirm-return`);
      return { success: true };
    } catch (err) {
      console.error('Ошибка возврата книги:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка возврата книги';
      const errorString = typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
      setError(errorString);
      return { success: false, error: errorString };
    } finally {
      setLoading(false);
    }
  };

  // Отмена бронирования
  const cancelBooking = async (bookingId) => {
    try {
      setLoading(true);
      setError(null);
      
      await apiClient.delete(`/bookings/${bookingId}`);
      return { success: true };
    } catch (err) {
      console.error('Ошибка отмены бронирования:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка отмены бронирования';
      const errorString = typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
      setError(errorString);
      return { success: false, error: errorString };
    } finally {
      setLoading(false);
    }
  };

  // Получение пунктов выдачи
  const fetchBookingPoints = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get('/bookings/booking-points');
      return response.data;
    } catch (err) {
      console.error('Ошибка загрузки пунктов выдачи:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки пунктов выдачи';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    loading,
    error,
    fetchUserBookings,
    createBooking,
    returnBook,
    cancelBooking,
    fetchBookingPoints,
  };

  return (
    <BookingContext.Provider value={value}>
      {children}
    </BookingContext.Provider>
  );
};