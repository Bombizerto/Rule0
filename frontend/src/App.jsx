import React, { useState } from 'react'
import './App.css'
import PublicView from './components/PublicView'
import AdminView from './components/AdminView'
import OrganizerDashboard from './components/OrganizerDashboard'

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [currentEventId, setCurrentEventId] = useState(null);

  // MOCK: Suponemos que el usuario logueado es siempre 'test-org-123' (Aidan)
  const LOGGED_IN_ORGANIZER = "test-org-123";

  const handleSelectEvent = (eventId) => {
    setCurrentEventId(eventId);
    setCurrentView('admin'); // Al elegir un torneo, pasamos al panel de control de ese torneo
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <OrganizerDashboard
          organizerId={LOGGED_IN_ORGANIZER}
          onSelectEvent={handleSelectEvent}
        />;
      case 'admin':
        return <AdminView
          eventId={currentEventId}
          onBack={() => setCurrentView('dashboard')}
        />;
      case 'public':
        return <PublicView eventId={currentEventId} />;
      default:
        return <OrganizerDashboard organizerId={LOGGED_IN_ORGANIZER} onSelectEvent={handleSelectEvent} />;
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

        <nav style={{ display: 'flex', gap: '15px' }}>
          <button
            className="primary-button"
            onClick={() => setCurrentView('dashboard')}
            style={{
              background: currentView === 'dashboard' ? 'var(--accent-primary)' : 'transparent',
              color: currentView === 'dashboard' ? 'black' : 'white',
              border: '2px solid var(--accent-primary)',
            }}
          >
            Dashboard
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

          {currentEventId && (
            <button
              className="primary-button"
              onClick={() => setCurrentView('public')}
              style={{
                background: currentView === 'public' ? 'var(--accent-primary)' : 'transparent',
                color: currentView === 'public' ? 'black' : 'white',
                border: '2px solid var(--accent-primary)',
              }}
            >
              Public View
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
