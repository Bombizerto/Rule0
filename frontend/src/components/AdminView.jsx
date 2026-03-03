import React, { useState, useEffect } from 'react'

function AdminView({ eventId, onBack }) {

    const [eventData, setEventData] = useState(null);

    useEffect(() => {
        const fetchEventData = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}`);
                const data = await response.json();
                setEventData(data)
            } catch (err) {
                console.error("Error cargando datos del evento:", err);
            }
        }
        fetchEventData();
    }, [eventId]);

    const handleGenerateRound = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/generate-round`, {
                method: 'POST',
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            } else {
                const data = await response.json();
                alert("¡Ronda generada con éxito! 🎲");
                console.log("Nueva ronda:", data.round);
                setEventData(prev => ({
                    ...prev,
                    rounds: [...prev.rounds, data.round]
                }));
            }
        } catch (err) {
            console.error("Fallo al conectar con el servidor:", err);
            alert("Error de conexión con el servidor");
        }
    };
    const handleReportWinner = async (podId, winnerId, alias) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/pods/${podId}/report-winner`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ winner_id: winnerId })
            });
            if (!response.ok) throw new Error("Fallo al reportar");
            // Actualizamos la pantalla al vuelo
            setEventData(prev => ({
                ...prev,
                rounds: prev.rounds.map(r => r.id === activeRound.id ? {
                    ...r,
                    pods: r.pods.map(p => p.id === podId ? { ...p, winner_id: winnerId, is_draw: false } : p)
                } : r)
            }));
        } catch (err) {
            console.error(err);
            alert("Error al reportar victoria");
        }
    };
    const handleReportDraw = async (podId) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/pods/${podId}/report-draw`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error("Fallo al reportar");
            // Actualizamos la pantalla al vuelo
            setEventData(prev => ({
                ...prev,
                rounds: prev.rounds.map(r => r.id === activeRound.id ? {
                    ...r,
                    pods: r.pods.map(p => p.id === podId ? { ...p, is_draw: true, winner_id: null } : p)
                } : r)
            }));
        } catch (err) {
            console.error(err);
            alert("Error al reportar empate");
        }
    };
    const handleStatusChange = async (playerId, currentStatus, action) => {
        try {
            if (currentStatus === action) {
                alert("El estado del jugador ya es el mismo que el seleccionado");
                return;
            }
            const newstatus = action === "PAUSED" && currentStatus === "paused" ? "active" : action.toLowerCase()
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/change_player_status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_id: playerId,
                    status: newstatus
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            } else {
                const data = await response.json();
                alert(`¡Estado del jugador cambiado con éxito! 🎲, ${newstatus}`);
                console.log("Nuevo estado del jugador:", data);
                setEventData(prev => ({
                    ...prev,
                    players: prev.players.map(p =>
                        p.id === playerId ? { ...p, status: newstatus } : p
                    )
                }));
            }
        } catch (err) {
            console.error("Fallo al conectar con el servidor:", err);
            alert("Error de conexión con el servidor");
        }
    };
    const handleCloseRound = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/close-round`, {
                method: 'POST',
            });
            if (!response.ok) {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            } else {
                alert("¡Ronda cerrada!");
                // Actualizamos react para forzar la vuelta al panel de Preparación
                setEventData(prev => ({
                    ...prev,
                    rounds: prev.rounds.map(r => r.id === activeRound.id ? { ...r, is_active: false } : r)
                }));
            }
        } catch (err) {
            console.error("Fallo al cerrar la ronda:", err);
            alert("Error de conexión con el servidor");
        }
    };

    const handleCloseEvent = async () => {
        if (!window.confirm("¿Seguro que quieres finalizar el evento? No se podrán jugar más rondas.")) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/close-event`, {
                method: 'POST',
            });
            if (!response.ok) {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            } else {
                alert("¡Torneo finalizado con éxito!");
                setEventData(prev => ({ ...prev, status: 'completed' }));
            }
        } catch (err) {
            console.error("Fallo al finalizar el torneo:", err);
            alert("Error de conexión con el servidor");
        }
    };

    const activeRound = eventData?.rounds?.[eventData.rounds.length - 1];
    return (
        <main className="glass-panel admin-dashboard">
            <header className="admin-header" style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                {onBack && (
                    <button
                        className="primary-button"
                        onClick={onBack}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem', border: '1px solid var(--accent-secondary)' }}
                    >
                        ← Volver
                    </button>
                )}
                <h2 style={{ margin: 0 }}>Panel de Control del Organizador</h2>
                <div className="event-badge" style={{ marginLeft: 'auto' }}>
                    <span className="event-id-label">ID Evento</span>
                    <span className="event-id-value">{eventId}</span>
                </div>
            </header>

            <div className="admin-content">
                {activeRound && activeRound.is_active ? (
                    <section className="round-section fade-in">
                        <div className="section-header">
                            <h3>Ronda {activeRound.round_number} en Curso</h3>
                            <button className="danger-button close-round-btn" onClick={handleCloseRound}>
                                Cerrar Ronda
                            </button>
                        </div>

                        <div className="pods-grid">
                            {/* Recorremos todas las mesas (pods) de la ronda activa */}
                            {activeRound.pods.map(pod => (
                                <div key={pod.id} className="pod-card glass-panel-inner hover-lift">
                                    <div className="pod-header">
                                        <h4>Mesa {pod.table_number}</h4>
                                        {pod.is_draw && <span className="status-badge warning">Empate</span>}
                                        {pod.winner_id && <span className="status-badge success">Ganador Decidido</span>}
                                    </div>

                                    <div className="pod-players-list">
                                        {/* Iteramos los IDs de los jugadores sentados en esta mesa */}
                                        {pod.players_ids.map(playerId => {
                                            // El truco mágico: buscamos cómo se llama ese jugador
                                            const playerInfo = eventData.players.find(p => p.id === playerId);
                                            const alias = playerInfo ? playerInfo.alias : "Desconocido";
                                            const isWinner = pod.winner_id === playerId;

                                            return (
                                                <div key={playerId} className={`pod-player-row ${isWinner ? 'is-winner' : ''}`}>
                                                    <span className="player-alias">{alias}</span>
                                                    <button className={`win-action-btn ${isWinner ? 'active-win' : ''}`}
                                                        onClick={() => handleReportWinner(pod.id, playerId, alias)}>
                                                        {isWinner ? '🏆 Ganador' : 'Win'}
                                                    </button>
                                                </div>
                                            );
                                        })}
                                    </div>
                                    <hr className="glass-divider" />

                                    {/* Botón de empate para la mesa entera */}
                                    <button className={`draw-action-btn ${pod.is_draw ? 'active-draw' : ''}`}
                                        onClick={() => handleReportDraw(pod.id)}>
                                        🤝 Empate (Draw)
                                    </button>
                                </div>
                            ))}
                        </div>
                    </section>
                ) : (
                    <section className="preparation-section fade-in">
                        <div className="section-header">
                            <h3>Gestión de Jugadores</h3>
                            {eventData?.status === 'completed' ? (
                                <div className="event-completed-badge">
                                    🏆 Torneo Finalizado
                                </div>
                            ) : (
                                <div className="header-actions">
                                    <button className="primary-button pulse-effect" onClick={handleGenerateRound}>
                                        🎲 Generar Ronda
                                    </button>
                                    <button className="danger-button" onClick={handleCloseEvent} style={{ marginLeft: '10px' }}>
                                        🛑 Finalizar Torneo
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="players-list-container">

                            {eventData?.players?.length > 0 ? (
                                // Si hay jugadores, los recorremos uno a uno con .map()
                                eventData.players.map((player) => {
                                    const st = player.status.toLowerCase();
                                    return (
                                        <div key={player.id} className={`player-row-card glass-panel-inner hover-lift status-${st}`}>
                                            <div className="player-info-col">
                                                <h4>{player.alias}</h4>
                                                <span className={`status-badge ${st}`}>
                                                    ACTIVO
                                                </span>
                                            </div>
                                            <div className="player-actions-col">
                                                <button className={`action-btn btn-pause ${st === 'paused' ? 'is-paused' : ''}`}
                                                    onClick={() => handleStatusChange(player.id, player.status, 'PAUSED')}>
                                                    {st === 'paused' ? '▶ Reanudar' : '⏸ Pausar'}
                                                </button>
                                                <button className={`action-btn btn-drop ${st === 'dropped' ? 'is-dropped' : ''}`}
                                                    onClick={() => handleStatusChange(player.id, player.status, 'dropped')}
                                                    disabled={st === 'dropped'}>
                                                    {st === 'dropped' ? '💥 Eliminado' : '🔥 Drop'}
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })
                            ) : (
                                // Si no hay jugadores o aún está cargando
                                <div className="empty-state glass-panel-inner">
                                    <p>No hay jugadores en este evento o los datos están cargando...</p>
                                </div>
                            )}
                        </div>
                    </section>)}
            </div>
        </main>
    )
}

export default AdminView
