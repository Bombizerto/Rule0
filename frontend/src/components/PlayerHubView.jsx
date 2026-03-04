import React, { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

function PlayerHubView({ user, onSelectEvent, onLogout }) {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [joinCode, setJoinCode] = useState('');
    const [joining, setJoining] = useState(false);

    const fetchEvents = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE_URL}/events/player/${user.id}`);
            if (!response.ok) throw new Error('Error al cargar mis torneos');
            const data = await response.json();
            setEvents(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, [user.id]);

    const handleJoinEvent = async (e) => {
        e.preventDefault();
        if (!joinCode.trim()) return;

        setJoining(true);
        try {
            const response = await fetch(`${API_BASE_URL}/events/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.id,
                    join_code: joinCode.toUpperCase()
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'No se pudo unir al torneo');
            }

            setJoinCode('');
            alert('¡Te has unido al torneo con éxito!');
            await fetchEvents(); // Refrescar lista

        } catch (err) {
            alert(err.message);
        } finally {
            setJoining(false);
        }
    };

    if (loading && events.length === 0) return <div className="loading" style={{ marginTop: '2rem', textAlign: 'center' }}>Cargando tus torneos...</div>;

    return (
        <div className="dashboard-container" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem 1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                <h2>Mis Torneos <span style={{ color: 'var(--accent-primary)', fontSize: '1rem' }}>({user.alias})</span></h2>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="danger-button" onClick={onLogout}>Cerrar Sesión</button>
                </div>
            </div>

            {/* Zona para unirse a un nuevo torneo */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>Unirse a un Torneo</h3>
                <form onSubmit={handleJoinEvent} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <input
                        type="text"
                        placeholder="Código de Invitación (Ej: A1B2C3)"
                        value={joinCode}
                        onChange={e => setJoinCode(e.target.value.toUpperCase())}
                        style={{
                            flex: '1', padding: '0.75rem', borderRadius: '8px',
                            border: '1px solid var(--border)', background: 'rgba(255,255,255,0.05)', color: 'white',
                            minWidth: '200px'
                        }}
                    />
                    <button type="submit" className="primary-button" disabled={joining || !joinCode}>
                        {joining ? 'Uniendo...' : 'Ingresar'}
                    </button>
                </form>
            </div>

            {/* Lista de torneos */}
            {error && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem' }}>{error}</div>}

            {events.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', background: 'var(--surface)', borderRadius: '12px' }}>
                    <p>No estás apuntado a ningún torneo todavía.</p>
                </div>
            ) : (
                <div className="events-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {events.map(event => (
                        <div key={event.id} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h3 style={{ margin: '0 0 0.5rem 0' }}>{event.title}</h3>
                                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                    <span>Status: <strong style={{ color: 'var(--accent-secondary)' }}>{event.status}</strong></span>
                                </div>
                            </div>
                            <button
                                className="primary-button"
                                style={{ background: 'var(--accent-primary)', color: 'black' }}
                                onClick={() => onSelectEvent(event)}
                            >
                                Entrar a la Mesa
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default PlayerHubView;
