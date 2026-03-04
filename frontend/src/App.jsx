import React, { useState, useEffect } from 'react'
import './App.css'
import LoginView from './components/LoginView'
import PlayerHubView from './components/PlayerHubView'
import AdminView from './components/AdminView'
import OrganizerDashboard from './components/OrganizerDashboard'
import MyDashboard from './components/MyDashboard'

function App() {
  const [currentView, setCurrentView] = useState('login');
  const [currentUser, setCurrentUser] = useState(null);

  // Admin App State
  const [currentEventId, setCurrentEventId] = useState(null);

  // Player Auth State
  const [playerEventData, setPlayerEventData] = useState(null);

  useEffect(() => {
    const savedSession = localStorage.getItem('rule0_session');
    if (savedSession) {
      try {
        const user = JSON.parse(savedSession);
        setCurrentUser(user);
        if (user.role === 'admin') {
          setCurrentView('dashboard');
        } else {
          setCurrentView('player_hub');
        }
      } catch (e) {
        console.error("Session corrupta, borrando...", e);
        localStorage.removeItem('rule0_session');
      }
    }
  }, []);

  const handleLoginSuccess = (userData) => {
    setCurrentUser(userData);
    localStorage.setItem('rule0_session', JSON.stringify(userData));
    if (userData.role === 'admin') {
      setCurrentView('dashboard');
    } else {
      setCurrentView('player_hub');
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setCurrentView('login');
    setCurrentEventId(null);
    setPlayerEventData(null);
    localStorage.removeItem('rule0_session');
  };

  const handleSelectEventAdmin = (eventId) => {
    setCurrentEventId(eventId);
    setCurrentView('admin');
  };

  const handleSelectEventPlayer = (eventData) => {
    setPlayerEventData(eventData);
    setCurrentView('player_dashboard');
  };

  const renderView = () => {
    switch (currentView) {
      case 'login':
        return <LoginView onLoginSuccess={handleLoginSuccess} />;
      case 'dashboard':
        return <OrganizerDashboard
          organizerId={currentUser?.id}
          onSelectEvent={handleSelectEventAdmin}
        />;
      case 'admin':
        return <AdminView
          eventId={currentEventId}
          onBack={() => setCurrentView('dashboard')}
        />;
      case 'player_hub':
        return <PlayerHubView
          user={currentUser}
          onSelectEvent={handleSelectEventPlayer}
          onLogout={handleLogout}
        />;
      case 'player_dashboard':
        return <MyDashboard
          eventData={playerEventData}
          playerId={currentUser?.id}
          onLogout={() => setCurrentView('player_hub')}
        />;
      default:
        return <LoginView onLoginSuccess={handleLoginSuccess} />;
    }
  };

  return (
    <div className="app-container">
      <header className="app-header" style={{
        background: 'rgba(255, 255, 255, 0.05)',
        padding: '1rem',
        borderRadius: '16px',
        marginBottom: '2rem',
        borderBottom: '1px solid var(--accent-primary)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ textAlign: 'left' }}>
          <h1 style={{ fontSize: '2rem', margin: 0 }}>RULE ZERO</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.8rem', fontWeight: '600', letterSpacing: '2px' }}>
            COMMANDER SYSTEM
          </p>
        </div>

        <nav style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {currentUser && (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginRight: '1rem' }}>
              {currentUser.alias} ({currentUser.role})
            </span>
          )}

          {currentUser?.role === 'admin' && (
            <>
              <button
                className="primary-button"
                onClick={() => setCurrentView('dashboard')}
                style={{
                  background: currentView === 'dashboard' ? 'var(--accent-primary)' : 'transparent',
                  color: currentView === 'dashboard' ? 'black' : 'white',
                  border: '2px solid var(--accent-primary)',
                }}
              >
                Mis Torneos
              </button>
              {currentEventId && (
                <button
                  className="primary-button"
                  onClick={() => setCurrentView('admin')}
                  style={{
                    background: currentView === 'admin' ? 'var(--accent-secondary)' : 'transparent',
                    color: 'white',
                    border: '2px solid var(--accent-secondary)',
                  }}
                >
                  Admin Panel
                </button>
              )}
              <button
                className="primary-button"
                onClick={() => setCurrentView('player_hub')}
                style={{
                  background: currentView === 'player_hub' ? 'var(--accent-primary)' : 'transparent',
                  color: currentView === 'player_hub' ? 'black' : 'white',
                  border: '2px solid var(--accent-primary)',
                }}
              >
                Modo Jugador
              </button>
            </>
          )}

          {currentUser?.role === 'player' && (
            <button
              className="primary-button"
              onClick={() => setCurrentView('player_hub')}
              style={{
                background: currentView === 'player_hub' ? 'var(--accent-primary)' : 'transparent',
                color: currentView === 'player_hub' ? 'black' : 'white',
                border: '2px solid var(--accent-primary)',
              }}
            >
              Mis Torneos
            </button>
          )}

          {currentUser && (
            <button className="danger-button" onClick={handleLogout} style={{ marginLeft: '1rem', padding: '0.5rem 1rem' }}>
              Salir
            </button>
          )}
        </nav>
      </header>

      <main className="app-main">
        {renderView()}
      </main>

      <footer>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2rem' }}>
          Versia Way System • Multi-View Architecture
        </p>
      </footer>
    </div>
  );
}

export default App
