import React, { useState, useEffect } from 'react'

function PublicView({ eventId, onBack }) {
    const [leaderboard, setLeaderboard] = useState([])
    const [loading, setLoading] = useState(true)

    const fetchLeaderboard = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/leaderboard`)
            const data = await response.json()
            setLeaderboard(data)
            setLoading(false)
        } catch (error) {
            console.error("Error fetching leaderboard:", error)
        }
    }

    useEffect(() => {
        fetchLeaderboard()
        const interval = setInterval(fetchLeaderboard, 10000)
        return () => clearInterval(interval)
    }, [eventId])

    const getRankClass = (index) => {
        if (index === 0) return "rank-1"
        if (index === 1) return "rank-2"
        if (index === 2) return "rank-3"
        return ""
    }

    return (
        <main className="glass-panel">
            {onBack && (
                <div style={{ marginBottom: '1.5rem', display: 'flex' }}>
                    <button
                        className="primary-button"
                        onClick={onBack}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem', border: '1px solid var(--accent-primary)' }}
                    >
                        ← Volver
                    </button>
                    <h2 style={{ margin: '0 0 0 1rem', display: 'flex', alignItems: 'center' }}>Clasificación Pública</h2>
                </div>
            )}
            {loading ? (
                <div className="loading">Cargando clasificación...</div>
            ) : (
                <div className="leaderboard-list">
                    <div className="leaderboard-header leaderboard-row" style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px', paddingBottom: '0.5rem' }}>
                        <span style={{ textAlign: 'center' }}>Pos</span>
                        <span style={{ textAlign: 'left', paddingLeft: '0.5rem' }}>Jugador</span>
                        <span style={{ textAlign: 'right' }}>Puntos</span>
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
    )
}

export default PublicView
