import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

import PodCard from './PodCard';
import PlayerList from './PlayerList';
import Leaderboard from './Leaderboard';


function AdminView({ eventId, onBack }) {
    const [eventData, setEventData] = useState(null);
    const [refreshLeaderboard, setRefreshLeaderboard] = useState(0);

    const triggerLeaderboardRefresh = () => setRefreshLeaderboard(prev => prev + 1);


    useEffect(() => {
        const fetchEventData = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}`);
                const data = await response.json();
                setEventData(data);
            } catch (err) {
                console.error("Error cargando datos del evento:", err);
            }
        };
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
            setEventData(prev => ({
                ...prev,
                rounds: prev.rounds.map(r => r.id === activeRound.id ? {
                    ...r,
                    pods: r.pods.map(p => p.id === podId ? {
                        ...p,
                        winner_id: winnerId,
                        is_draw: false,
                        is_disputed: false,
                        proposed_winner_id: null,
                        proposed_is_draw: false,
                        confirmations: []
                    } : p)
                } : r)
            }));
            triggerLeaderboardRefresh();
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
            setEventData(prev => ({
                ...prev,
                rounds: prev.rounds.map(r => r.id === activeRound.id ? {
                    ...r,
                    pods: r.pods.map(p => p.id === podId ? {
                        ...p,
                        is_draw: true,
                        winner_id: null,
                        is_disputed: false,
                        proposed_winner_id: null,
                        proposed_is_draw: false,
                        confirmations: []
                    } : p)
                } : r)
            }));
            triggerLeaderboardRefresh();
        } catch (err) {
            console.error(err);
            alert("Error al reportar empate");
        }
    };

    const handleStatusChange = async (playerId, currentStatus, action) => {
        try {
            let newStatus;

            if (action === "PAUSED") {
                newStatus = currentStatus === "paused" ? "active" : "paused";
            } else {
                newStatus = action.toLowerCase(); // 'dropped', 'active', etc.
            }

            if (currentStatus === newStatus) {
                return;
            }

            const response = await fetch(`http://127.0.0.1:8000/matchmaking/events/${eventId}/change_player_status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_id: playerId,
                    status: newStatus
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            } else {
                // Actualizar localmente el estado del jugador
                setEventData(prev => ({
                    ...prev,
                    players: prev.players.map(p =>
                        p.id === playerId ? { ...p, status: newStatus } : p
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
                setEventData(prev => ({
                    ...prev,
                    rounds: prev.rounds.map(r => r.id === activeRound.id ? { ...r, is_active: false } : r)
                }));
                triggerLeaderboardRefresh();
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

    const onDragEnd = async (result) => {
        const { destination, source, draggableId } = result;

        if (!destination) return;
        if (
            destination.droppableId === source.droppableId &&
            destination.index === source.index
        ) {
            return;
        }

        // 1. Optimistic Update Local
        console.log(`DND: Se movió el jugador ${draggableId} de ${source.droppableId} a ${destination.droppableId}`);

        // Guardamos copia de seguridad para revertir si hay fallo (ej: mesa llena)
        const previousEventData = eventData;

        setEventData(prev => {
            const newEventData = { ...prev };
            // Hacemos deep copy inmutable de los arrays (rounds y pods)
            newEventData.rounds = prev.rounds.map((round, idx) => {
                if (idx !== prev.rounds.length - 1) return round;

                return {
                    ...round,
                    pods: round.pods.map(pod => {
                        // Quitamos del origen
                        if (pod.id === source.droppableId) {
                            return { ...pod, players_ids: pod.players_ids.filter(id => id !== draggableId) };
                        }
                        // Metemos en destino respetando la posición
                        if (pod.id === destination.droppableId) {
                            const newPlayers = [...pod.players_ids];
                            newPlayers.splice(destination.index, 0, draggableId);
                            return { ...pod, players_ids: newPlayers };
                        }
                        return pod;
                    })
                };
            });
            return newEventData;
        });

        // 2. Llamada a Backend
        try {
            const response = await fetch(`http://127.0.0.1:8000/matchmaking/pods/swap-players`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_pod_id: source.droppableId,
                    target_pod_id: destination.droppableId,
                    player_id: draggableId
                })
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Error al mover jugador: ${error.detail}`);
                // Revertimos el Optimistic Update
                setEventData(previousEventData);
            }
        } catch (err) {
            console.error("Fallo llamada swap:", err);
            alert("Error de conexión al mover jugador");
            // Revertimos en caso de fallo de red
            setEventData(previousEventData);
        }
    };

    const activeRound = eventData?.rounds?.[eventData.rounds.length - 1];

    if (!eventData) return (
        <div className="loading-state glass-panel fade-in">
            <div className="spinner"></div>
            <p>Cargando torneo...</p>
        </div>
    );

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
                        <DragDropContext onDragEnd={onDragEnd}>
                            <div className="pods-grid">
                                {activeRound.pods.map(pod => (
                                    <Droppable droppableId={pod.id.toString()} key={pod.id}>
                                        {(provided) => (
                                            <div
                                                ref={provided.innerRef}
                                                {...provided.droppableProps}
                                                style={{ minHeight: '150px' }} // Asegura a droppable tener espacio
                                            >
                                                <PodCard
                                                    pod={pod}
                                                    activeRound={activeRound}
                                                    eventData={eventData}
                                                    handleReportWinner={handleReportWinner}
                                                    handleReportDraw={handleReportDraw}
                                                />
                                                {provided.placeholder}
                                            </div>
                                        )}
                                    </Droppable>
                                ))}
                            </div>
                        </DragDropContext>
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
                            <PlayerList players={eventData?.players} handleStatusChange={handleStatusChange} />
                        </div>
                    </section>
                )}

                <section className="leaderboard-section fade-in" style={{ marginTop: '2.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem' }}>
                    <div className="section-header">
                        <h3 style={{ color: 'var(--accent-primary)' }}>🏆 Clasificación Actual</h3>
                    </div>
                    <Leaderboard eventId={eventId} refreshTrigger={refreshLeaderboard} />
                </section>
            </div>

        </main>
    );
}

export default AdminView;

