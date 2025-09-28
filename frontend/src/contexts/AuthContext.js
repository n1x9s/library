import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../config/axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth должен использоваться внутри AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Проверка сессии при загрузке приложения
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Пытаемся получить данные пользователя из сессии
        const response = await apiClient.get('/auth/me');
        setUser(response.data);
      } catch (error) {
        // Если сессия недействительна, пользователь не аутентифицирован
        console.log('Пользователь не аутентифицирован');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password,
      });

      // После успешного входа cookie автоматически устанавливается
      // Получаем данные пользователя из ответа
      setUser(response.data);

      return { success: true };
    } catch (error) {
      console.error('Ошибка входа:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Ошибка входа';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await apiClient.post('/auth/register', userData);
      // После регистрации пользователь автоматически входит в систему
      setUser(response.data);
      return { success: true };
    } catch (error) {
      console.error('Ошибка регистрации:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Ошибка регистрации';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  const logout = async () => {
    try {
      // Вызываем эндпойнт выхода для очистки сессии на сервере
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Ошибка при выходе:', error);
    } finally {
      // Очищаем локальное состояние
      setUser(null);
    }
  };

  const updateUser = async (userData) => {
    try {
      const response = await apiClient.put('/auth/me', userData);
      setUser(response.data);
      return { success: true };
    } catch (error) {
      console.error('Ошибка обновления профиля:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Ошибка обновления профиля';
      return { 
        success: false, 
        error: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
