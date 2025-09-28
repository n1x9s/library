import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { BookProvider } from './contexts/BookContext';
import { BookingProvider } from './contexts/BookingContext';
import Header from './components/Header';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import MyShelf from './pages/MyShelf';
import BookDetails from './pages/BookDetails';
import AddBook from './pages/AddBook';
import Bookings from './pages/Bookings';
import Profile from './pages/Profile';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BookProvider>
        <BookingProvider>
          <Router>
            <div className="App">
              <Header />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/my-shelf" element={<MyShelf />} />
                  <Route path="/book/:id" element={<BookDetails />} />
                  <Route path="/add-book" element={<AddBook />} />
                  <Route path="/bookings" element={<Bookings />} />
                  <Route path="/profile" element={<Profile />} />
                </Routes>
              </main>
            </div>
          </Router>
        </BookingProvider>
      </BookProvider>
    </AuthProvider>
  );
}

export default App;
