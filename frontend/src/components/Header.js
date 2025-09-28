import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Header.css';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    setShowUserMenu(false);
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          {/* Навигация */}
          <nav className="nav">
            <Link to="/" className="nav-link">Обзор</Link>
            <Link to="/my-shelf" className="nav-link">Моя полка</Link>
            <Link to="/add-book" className="nav-link">Поделиться</Link>
            <Link to="/bookings" className="nav-link">Взять</Link>
            <Link to="/add-book" className="nav-link">Книга</Link>
          </nav>

          {/* Поиск */}
          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              className="search-input"
              placeholder="Ищете что-то? Напишите: Автор — Название"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>

          {/* Пользовательские действия */}
          <div className="user-actions">
            {isAuthenticated ? (
              <div className="user-menu">
                <button 
                  className="user-menu-toggle"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                >
                  <div className="user-avatar">
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt="Аватар" />
                    ) : (
                      <span>{user?.username?.charAt(0).toUpperCase()}</span>
                    )}
                  </div>
                </button>
                
                {showUserMenu && (
                  <div className="user-dropdown">
                    <Link 
                      to="/profile" 
                      className="dropdown-item"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Профиль
                    </Link>
                    <Link 
                      to="/my-shelf" 
                      className="dropdown-item"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Мои книги
                    </Link>
                    <Link 
                      to="/bookings" 
                      className="dropdown-item"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Бронирования
                    </Link>
                    <button 
                      className="dropdown-item logout"
                      onClick={handleLogout}
                    >
                      Выйти
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="auth-buttons">
                <Link to="/login" className="btn btn-secondary">Войти</Link>
                <Link to="/register" className="btn btn-primary">Регистрация</Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
