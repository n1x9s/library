import axios from 'axios';

// Создаем экземпляр axios с базовой конфигурацией
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  withCredentials: true, // Включаем отправку cookies для сессий
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для запросов
apiClient.interceptors.request.use(
  (config) => {
    // Можно добавить логику для добавления токенов или других заголовков
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для ответов
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Обработка ошибок аутентификации
    if (error.response?.status === 401) {
      // Можно добавить логику для перенаправления на страницу входа
      console.log('Ошибка аутентификации');
    }
    return Promise.reject(error);
  }
);

export default apiClient;