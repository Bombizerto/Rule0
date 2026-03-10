import React, { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

const OrganizerDashboard = ({ organizerId, onSelectEvent }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedLeaderboard, setExpandedLeaderboard] = useState(null); // event_id activo
    const [leaderboards, setLeaderboards] = useState({}); // { event_id: [...] }

    // Estado para el modal de Crear Torneo
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newEventTitle, setNewEventTitle] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [autoJoin, setAutoJoin] = useState(false);

    const fetchEvents = async () => {
        try {
            setLoading(true);
            // Endpoint local de desarrollo => Usa proxy o ruta completa según tu setup de Vite
            // El organizerId nos viene desde el componente padre (App.js)
            const response = await fetch(`${API_BASE_URL}/events/organizer/${organizerId}`);
            if (!response.ok) {
                throw new Error('Error al cargar la lista de eventos');
            }
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
    }, [organizerId]);

    // Cargar rulesets disponibles al montar
    const [rulesetId, setRulesetId] = useState(null);
    useEffect(() => {
        fetch(`${API_BASE_URL}/rulesets/`)
            .then(r => r.ok ? r.json() : [])
            .then(data => { if (data.length > 0) setRulesetId(data[0].id); })
            .catch(() => { });
    }, []);

    const handleCreateEvent = async (e) => {
        e.preventDefault();
        if (!newEventTitle.trim()) return;
        if (!rulesetId) { alert('No hay rulesets disponibles'); return; }

        setIsCreating(true);
        try {
            const response = await fetch(`${API_BASE_URL}/events/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newEventTitle,
                    organizer_id: organizerId,
                    ruleset_id: rulesetId
                })
            });

            if (!response.ok) {
                throw new Error('No se pudo crear el torneo');
            }
            const eventData = await response.json();

            // Auto-join si se ha marcado la casilla
            if (autoJoin && eventData.join_code) {
                await fetch(`${API_BASE_URL}/events/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: organizerId,
                        join_code: eventData.join_code
                    })
                });
            }

            // Refrescamos la lista cerrando el modal
            await fetchEvents();
            setShowCreateModal(false);
            setNewEventTitle('');
            setAutoJoin(false);
        } catch (err) {
            alert(err.message);
        } finally {
            setIsCreating(false);
        }
    };

    if (loading && events.length === 0) return <div className="loading" style={{ marginTop: '2rem', textAlign: 'center' }}>Cargando tus torneos...</div>;
    if (error) return <div className="error-message" style={{ color: '#ff4444', textAlign: 'center', marginTop: '2rem' }}>{error}</div>;

    return (
        <div className="dashboard-container" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem 1rem' }}>
            <style>{`
                 /* Añadiremos estos estilos en el index.css pero los dejamos aquí inline provisionalmente */
                .event-card {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                    display: grid;
                    grid-template-columns: 1fr auto;
                    gap: 1rem;
                    align-items: center;
                    transition: all 0.2s ease;
                }
                .event-card:hover { border-color: var(--primary); transform: translateY(-2px); }
                .event-card-info h3 { margin: 0 0 0.5rem 0; color: var(--text); }
                .event-card-meta { display: flex; gap: 1rem; color: var(--text-muted); font-size: 0.9rem; }
                .status-badge { 
                    padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
                }
                .status-pending { background: rgba(255,165,0,0.1); color: #ffa500; }
                .status-active { background: rgba(50,205,50,0.1); color: #32cd32; }
                .status-completed { background: rgba(128,128,128,0.1); color: #808080; }
            `}</style>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2>Mis Torneos</h2>
                <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                    + Nuevo Torneo
                </button>
            </div>

            {events.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', background: 'var(--surface)', borderRadius: '12px' }}>
                    <p>No tienes ningún torneo registrado todavía.</p>
                </div>
            ) : (
                <div className="events-grid">
                    {events.map(event => (
                        <div key={event.id} className="event-card">
                            <div className="event-card-info">
                                <h3>{event.title}</h3>
                                <div className="event-card-meta">
                                    <span>#{event.join_code}</span>
                                    <span>•</span>
                                    <span>{event.players.length} Jugadores</span>
                                </div>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                                <span className={`status-badge status-${event.status}`}>
                                    {event.status}
                                </span>
                                <button
                                    className="btn btn-secondary"
                                    style={{ background: 'transparent', border: '1px solid var(--accent-primary)', color: 'var(--accent-primary)', fontSize: '0.85rem' }}
                                    onClick={async () => {
                                        const isOpen = expandedLeaderboard === event.id;
                                        setExpandedLeaderboard(isOpen ? null : event.id);
                                        if (!isOpen && !leaderboards[event.id]) {
                                            const res = await fetch(`${API_BASE_URL}/matchmaking/events/${event.id}/leaderboard`);
                                            if (res.ok) {
                                                const data = await res.json();
                                                setLeaderboards(prev => ({ ...prev, [event.id]: data }));
                                            }
                                        }
                                    }}
                                >
                                    {expandedLeaderboard === event.id ? '▲ Clasificación' : '▼ Clasificación'}
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => onSelectEvent(event.id)}
                                >
                                    Gestionar
                                </button>
                            </div>

                            {/* Panel de leaderboard expandible */}
                            {expandedLeaderboard === event.id && (
                                <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                                    {!leaderboards[event.id] || leaderboards[event.id].length === 0 ? (
                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: 0 }}>Aún no hay rondas completadas.</p>
                                    ) : (
                                        <div className="leaderboard-list">
                                            <div className="leaderboard-header leaderboard-row">
                                                <span style={{ width: '2rem' }}>#</span>
                                                <span style={{ flex: 2 }}>Jugador</span>
                                                <span>Puntos</span>
                                            </div>
                                            {leaderboards[event.id].map((e2, i) => (
                                                <div key={e2.player_id} className="leaderboard-row">
                                                    <span style={{ width: '2rem', color: i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? '#cd7f32' : 'var(--text-muted)' }}>
                                                        {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`}
                                                    </span>
                                                    <span className="player-name" style={{ flex: 2 }}>{e2.alias}</span>
                                                    <span className="points" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{e2.points} pts</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Modal de Crear Torneo */}
            {showCreateModal && (
                <div className="modal-overlay" style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex',
                    justifyContent: 'center', alignItems: 'center', zIndex: 1000
                }}>
                    <div className="modal-content" style={{
                        background: 'var(--surface)', padding: '2rem',
                        borderRadius: '16px', border: '1px solid var(--border)',
                        width: '90%', maxWidth: '400px'
                    }}>
                        <h3 style={{ marginTop: 0, marginBottom: '1.5rem' }}>Crear Nuevo Torneo</h3>
                        <form onSubmit={handleCreateEvent}>
                            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Nombre del Torneo</label>
                                <input
                                    type="text"
                                    value={newEventTitle}
                                    onChange={(e) => setNewEventTitle(e.target.value)}
                                    placeholder="Ej: Liga de Verano 2026"
                                    required
                                    autoFocus
                                    style={{
                                        width: '100%', padding: '0.75rem',
                                        borderRadius: '8px', border: '1px solid var(--border)',
                                        background: 'rgba(255,255,255,0.05)', color: 'white'
                                    }}
                                />
                            </div>
                            <div className="form-group" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <input
                                    type="checkbox"
                                    id="autoJoin"
                                    checked={autoJoin}
                                    onChange={(e) => setAutoJoin(e.target.checked)}
                                    style={{ width: '1.2rem', height: '1.2rem', accentColor: 'var(--accent-primary)' }}
                                />
                                <label htmlFor="autoJoin" style={{ color: 'var(--text-muted)' }}>Participar en el torneo como jugador</label>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)} disabled={isCreating}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={isCreating || !newEventTitle.trim()}>
                                    {isCreating ? 'Creando...' : 'Crear Torneo'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default OrganizerDashboard;
