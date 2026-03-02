import React, { useState } from 'react'
import './App.css'
import PublicView from './components/PublicView'
import AdminView from './components/AdminView'

function App() {
  const [view, setView] = useState('public') // 'public' | 'admin'
  const eventId = "test-event-123"

  console.log("App Rendering - Current view:", view);

  return (
    <div className="app-container">
      <header style={{
        background: 'rgba(255, 255, 255, 0.05)',
        padding: '1rem',
        borderRadius: '16px',
        marginBottom: '2rem',
        borderBottom: '1px solid var(--accent-primary)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ textAlign: 'left' }}>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>RULE ZERO</h1>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.8rem', fontWeight: '600', letterSpacing: '2px' }}>
              COMMANDER SYSTEM
            </p>
          </div>
          <nav style={{ display: 'flex', gap: '15px' }}>
            <button
              className="primary-button"
              onClick={() => { console.log("Switching to public"); setView('public'); }}
              style={{
                background: view === 'public' ? 'var(--accent-primary)' : 'transparent',
                color: view === 'public' ? 'black' : 'white',
                border: '2px solid var(--accent-primary)',
              }}
            >
              Public View
            </button>
            <button
              className="primary-button"
              onClick={() => { console.log("Switching to admin"); setView('admin'); }}
              style={{
                background: view === 'admin' ? 'var(--accent-secondary)' : 'transparent',
                color: 'white',
                border: '2px solid var(--accent-secondary)',
              }}
            >
              Admin Panel
            </button>
          </nav>
        </div>
      </header>

      {view === 'public' ? (
        <PublicView eventId={eventId} />
      ) : (
        <AdminView eventId={eventId} />
      )}

      <footer>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2rem' }}>
          Versia Way System • Multi-View Architecture
        </p>
      </footer>
    </div>
  )
}

export default App
