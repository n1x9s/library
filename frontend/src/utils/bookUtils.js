/**
 * Утилиты для работы с книгами
 */

/**
 * Получает читаемое название состояния книги
 * @param {string} condition - Состояние книги (excellent, good, fair, poor)
 * @returns {string} - Читаемое название состояния
 */
export const getBookConditionText = (condition) => {
  const conditionMap = {
    'excellent': 'Отличное',
    'good': 'Хорошее', 
    'fair': 'Удовлетворительное',
    'poor': 'Плохое',
    // Поддержка старых значений в верхнем регистре
    'EXCELLENT': 'Отличное',
    'GOOD': 'Хорошее',
    'FAIR': 'Удовлетворительное', 
    'POOR': 'Плохое'
  };
  
  return conditionMap[condition] || 'Неизвестно';
};

/**
 * Получает CSS класс для состояния книги
 * @param {string} condition - Состояние книги
 * @returns {string} - CSS класс
 */
export const getBookConditionClass = (condition) => {
  const classMap = {
    'excellent': 'condition-excellent',
    'good': 'condition-good',
    'fair': 'condition-fair', 
    'poor': 'condition-poor',
    'EXCELLENT': 'condition-excellent',
    'GOOD': 'condition-good',
    'FAIR': 'condition-fair',
    'POOR': 'condition-poor'
  };
  
  return classMap[condition] || 'condition-unknown';
};

/**
 * Валидирует данные книги перед отправкой
 * @param {object} bookData - Данные книги
 * @returns {object} - Валидированные данные
 */
export const validateBookData = (bookData) => {
  const validatedData = { ...bookData };
  
  // Преобразуем год публикации в число
  if (validatedData.publication_year) {
    validatedData.publication_year = parseInt(validatedData.publication_year);
  }
  
  // Убеждаемся, что состояние в нижнем регистре
  if (validatedData.condition) {
    validatedData.condition = validatedData.condition.toLowerCase();
  }
  
  return validatedData;
};
