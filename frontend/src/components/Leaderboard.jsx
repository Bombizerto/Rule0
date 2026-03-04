import React, { useState, useEffect } from 'react';

/**
 * Reusable Leaderboard component.
 * @param {string} eventId - The ID of the event to fetch the leaderboard for.
 * @param {string} highlightPlayerId - Optional player ID to highlight in the ranking.
 * @param {boolean} refreshTrigger - Optional trigger to force a refresh from parent components.
 */
function Leaderboard({ eventId, highlightPlayerId, refreshTrigger }) {
    const [leaderboard, setLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchLeaderboard = async () => {
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/leaderboard`);
            if (response.ok) {
                const data = await response.json();
                setLeaderboard(data);
            } else {
                const errData = await response.json().catch(() => ({ detail: "Error desconocido" }));
                setError(errData.detail || "Fallo al cargar clasificación");
            }
        } catch (err) {
            console.error("Error fetching leaderboard:", err);
            setError("Error de conexión con el servidor");
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        if (eventId) {
            fetchLeaderboard();
        }
    }, [eventId, refreshTrigger]);

    if (loading) return <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Cargando clasificación...</p>;

    if (error) {
        return (
            <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger-color)', borderRadius: '12px', color: 'var(--danger-color)' }}>
                <p>⚠️ {error}</p>
                <button
                    className="primary-button"
                    style={{ marginTop: '0.5rem', fontSize: '0.8rem', background: 'transparent' }}
                    onClick={fetchLeaderboard}
                >
                    ↻ Reintentar
                </button>
            </div>
        );
    }

    if (leaderboard.length === 0) {
        return (
            <div style={{ textAlign: 'center', padding: '1.5rem', background: 'var(--bg-card)', borderRadius: '12px', color: 'var(--text-muted)' }}>
                <p>Aún no hay rondas completadas o no hay datos disponibles.</p>
            </div>
        );
    }

    return (
        <div className="leaderboard-list fade-in">
            <div className="leaderboard-header leaderboard-row">
                <span style={{ width: '2rem' }}>#</span>
                <span style={{ flex: 2 }}>Jugador</span>
                <span>Puntos</span>
            </div>
            {leaderboard.map((entry, i) => (
                <div
                    key={entry.player_id}
                    className="leaderboard-row"
                    style={{
                        background: entry.player_id === highlightPlayerId ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                        fontWeight: entry.player_id === highlightPlayerId ? 'bold' : 'normal',
                        borderLeft: entry.player_id === highlightPlayerId ? '4px solid var(--accent-primary)' : 'none'
                    }}
                >
                    <span style={{ width: '2rem', color: i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? '#cd7f32' : 'var(--text-muted)' }}>
                        {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`}
                    </span>
                    <span className="player-name" style={{ flex: 2 }}>
                        {entry.alias} {entry.player_id === highlightPlayerId ? '(Tú)' : ''}
                    </span>
                    <span className="points" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>
                        {entry.points} pts
                    </span>
                </div>
            ))}
        </div>
    );
}

export default Leaderboard;
