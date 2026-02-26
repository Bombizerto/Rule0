import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const eventId = "test-event-123" // ID del evento de prueba

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`http://localhost:8000/matchmaking/events/${eventId}/leaderboard`)
      const data = await response.json()
      setLeaderboard(data)
      setLoading(false)
    } catch (error) {
      console.error("Error fetching leaderboard:", error)
    }
  }

  useEffect(() => {
    fetchLeaderboard()
    const interval = setInterval(fetchLeaderboard, 10000) // Actualizar cada 10s
    return () => clearInterval(interval)
  }, [])

  const getRankClass = (index) => {
    if (index === 0) return "rank-1"
    if (index === 1) return "rank-2"
    if (index === 2) return "rank-3"
    return ""
  }

  return (
    <div className="app-container">
      <header>
        <h1>RULE ZERO</h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '-1.5rem', fontWeight: '600', letterSpacing: '2px' }}>
          COMMANDER LEADERBOARD
        </p>
      </header>

      <main className="glass-panel">
        {loading ? (
          <div className="loading">Cargando clasificación...</div>
        ) : (
          <div className="leaderboard-list">
            <div className="leaderboard-header leaderboard-row" style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
              <span>Pos</span>
              <span>Jugador</span>
              <span>Puntos</span>
            </div>
            {leaderboard.map((item, index) => (
              <div key={item.player_id} className="leaderboard-row">
                <span className={`rank ${getRankClass(index)}`}>
                  {index < 3 ? ['🥇', '🥈', '🥉'][index] : index + 1}
                </span>
                <span className="player-name">{item.alias}</span>
                <span className="points">
                  <span className="score-badge">{item.points} PTS</span>
                </span>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2rem' }}>
          Versia Way System • Real-Time Matchmaking Engine
        </p>
      </footer>
    </div>
  )
}

export default App
