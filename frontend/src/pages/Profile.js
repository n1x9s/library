import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Profile.css';

const Profile = () => {
  const { user, updateUser, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    phone: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || '',
        username: user.username || '',
        full_name: user.full_name || '',
        phone: user.phone || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const result = await updateUser(formData);
    
    if (result.success) {
      setSuccess('Профиль успешно обновлен');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  if (!isAuthenticated) {
    return (
      <div className="profile">
        <div className="container">
          <div className="auth-required">
            <h2>Необходима авторизация</h2>
            <p>Войдите в систему, чтобы просмотреть профиль.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="container">
        <div className="page-header">
          <h1>Мой профиль</h1>
        </div>

        <div className="profile-content">
          <div className="profile-avatar">
            {user?.avatar_url ? (
              <img 
                src={`http://localhost:8000${user.avatar_url}`} 
                alt="Аватар"
                className="avatar-image"
              />
            ) : (
              <div className="avatar-placeholder">
                <span className="avatar-text">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
            )}
            <button className="btn btn-secondary avatar-upload">
              Изменить фото
            </button>
          </div>

          <div className="profile-form-container">
            <form onSubmit={handleSubmit} className="profile-form">
              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              {success && (
                <div className="success-message">
                  {success}
                </div>
              )}

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="email" className="form-label">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="form-input"
                    disabled={loading}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="username" className="form-label">
                    Имя пользователя
                  </label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="form-input"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="full_name" className="form-label">
                  Полное имя
                </label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="form-input"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone" className="form-label">
                  Телефон
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="form-input"
                  disabled={loading}
                  placeholder="+7 (999) 123-45-67"
                />
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Сохранение...' : 'Сохранить изменения'}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="profile-stats">
          <h3>Статистика</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">0</span>
              <span className="stat-label">Книг в обмене</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">0</span>
              <span className="stat-label">Успешных обменов</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">0</span>
              <span className="stat-label">Дней использования</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
