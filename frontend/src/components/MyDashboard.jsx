import React, { useState } from 'react';

function MyDashboard({ eventData, playerId, onLogout }) {
    const [loadingAction, setLoadingAction] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [localEventData, setLocalEventData] = useState(eventData);

    if (!localEventData) return null;

    // Buscar al jugador
    const player = localEventData.players.find(p => p.id === playerId);

    // Buscar la mesa activa (en la última ronda o ronda activa)
    let currentPod = null;
    let currentRound = null;

    const activeRound = localEventData.rounds.find(r => r.is_active);
    if (activeRound) {
        currentRound = activeRound;
        currentPod = activeRound.pods.find(p => p.players_ids.includes(playerId));
    }

    const refreshEventData = async () => {
        try {
            const resp = await fetch(`http://127.0.0.1:8000/matchmaking/events/login-player`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    join_code: localEventData.join_code,
                    player_alias: player.alias
                })
            });
            if (resp.ok) {
                const data = await resp.json();
                setLocalEventData(data.event_data);
            }
        } catch (err) {
            console.error("Error refreshing data:", err);
        }
    };

    const handleProposeResult = async (winnerId, isDraw) => {
        setLoadingAction(true);
        setActionError(null);
        try {
            const resp = await fetch(`http://127.0.0.1:8000/matchmaking/pods/${currentPod.id}/propose-result`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    player_id: playerId,
                    winner_id: winnerId,
                    is_draw: isDraw
                })
            });
            if (!resp.ok) {
                const data = await resp.json();
                throw new Error(data.detail || "Error al proponer resultado");
            }
            await refreshEventData();
        } catch (err) {
            setActionError(err.message);
        } finally {
            setLoadingAction(false);
        }
    };

    const handleConfirmResult = async () => {
        setLoadingAction(true);
        setActionError(null);
        try {
            const resp = await fetch(`http://127.0.0.1:8000/matchmaking/pods/${currentPod.id}/confirm-result`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            });
            if (!resp.ok) {
                const data = await resp.json();
                throw new Error(data.detail || "Error al confirmar");
            }
            await refreshEventData();
        } catch (err) {
            setActionError(err.message);
        } finally {
            setLoadingAction(false);
        }
    };

    const handleRejectResult = async () => {
        if (!window.confirm("¿Seguro que quieres rechazar el resultado? Esto pondrá la mesa en Disputa.")) return;
        setLoadingAction(true);
        setActionError(null);
        try {
            const resp = await fetch(`http://127.0.0.1:8000/matchmaking/pods/${currentPod.id}/reject-result`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            });
            if (!resp.ok) {
                const data = await resp.json();
                throw new Error(data.detail || "Error al rechazar");
            }
            await refreshEventData();
        } catch (err) {
            setActionError(err.message);
        } finally {
            setLoadingAction(false);
        }
    };

    // Render helpers
    const renderActionPanel = () => {
        if (!currentPod) return null;

        // Caso 1: Mesa cerrada
        if (currentPod.winner_id || currentPod.is_draw) {
            return (
                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid var(--success-color)', borderRadius: '8px', textAlign: 'center' }}>
                    <h4 style={{ color: 'var(--success-color)', margin: 0 }}>Mesa Finalizada ✓</h4>
                    <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                        {currentPod.is_draw ? "Empate (Draw)" : `Ganador: ${localEventData.players.find(p => p.id === currentPod.winner_id)?.alias}`}
                    </p>
                </div>
            );
        }

        // Caso 2: Mesa en disputa
        if (currentPod.is_disputed) {
            return (
                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger-color)', borderRadius: '8px', textAlign: 'center' }}>
                    <h4 style={{ color: 'var(--danger-color)', margin: 0 }}>Mesa en Disputa ⚠️</h4>
                    <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                        Alguien ha rechazado los resultados. Llama a un Organizador.
                    </p>
                </div>
            );
        }

        // Caso 3: Alguien ha propuesto un resultado
        if (currentPod.proposed_winner_id || currentPod.proposed_is_draw) {
            const hasConfirmed = currentPod.confirmations?.[playerId] === true;

            let propuestaTarget = "Empate";
            if (currentPod.proposed_winner_id) {
                propuestaTarget = "Ganador: " + localEventData.players.find(p => p.id === currentPod.proposed_winner_id)?.alias;
            }

            return (
                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--accent-secondary)', borderRadius: '8px', textAlign: 'center' }}>
                    <h4 style={{ color: 'var(--accent-secondary)', marginTop: 0 }}>Resultado Propuesto</h4>
                    <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{propuestaTarget}</p>

                    {hasConfirmed ? (
                        <p style={{ color: 'var(--success-color)', fontWeight: 'bold' }}>✓ Has confirmado. Esperando al resto...</p>
                    ) : (
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1rem' }}>
                            <button className="primary-button" style={{ background: 'var(--success-color)', borderColor: 'var(--success-color)' }} onClick={handleConfirmResult} disabled={loadingAction}>
                                Confirmar ✓
                            </button>
                            <button className="danger-button" onClick={handleRejectResult} disabled={loadingAction}>
                                Rechazar ✗
                            </button>
                        </div>
                    )}
                </div>
            );
        }

        // Caso 4: No hay propuesta, el jugador puede proponer
        return (
            <div style={{ marginTop: '2rem' }}>
                <h4 style={{ marginBottom: '1rem' }}>Reportar Resultado (Propuesta)</h4>
                {actionError && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem', fontSize: '0.9rem' }}>{actionError}</div>}
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <button
                        className="primary-button"
                        style={{ flex: 1, minWidth: '150px' }}
                        onClick={() => handleProposeResult(playerId, false)}
                        disabled={loadingAction}
                    >
                        🏆 He Ganado
                    </button>
                    <button
                        className="primary-button"
                        style={{ flex: 1, minWidth: '150px', background: 'var(--accent-secondary)', borderColor: 'var(--accent-secondary)' }}
                        onClick={() => handleProposeResult(null, true)}
                        disabled={loadingAction}
                    >
                        🤝 Empate (Draw)
                    </button>
                    {currentPod.players_ids.filter(id => id !== playerId).map(opp_id => {
                        const oppInfo = localEventData.players.find(p => p.id === opp_id);
                        return (
                            <button
                                key={opp_id}
                                className="action-button"
                                style={{ flex: '1 1 auto', minWidth: '120px' }}
                                onClick={() => handleProposeResult(opp_id, false)}
                                disabled={loadingAction}
                            >
                                Ganó: {oppInfo ? oppInfo.alias : opp_id}
                            </button>
                        )
                    })}
                </div>
            </div>
        );
    };

    return (
        <main className="glass-panel fade-in" style={{ maxWidth: '800px', margin: '2rem auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <h2 style={{ margin: 0 }}>Vista de: <span style={{ color: 'var(--accent-primary)' }}>{player ? player.alias : playerId}</span></h2>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="primary-button" style={{ background: 'transparent' }} onClick={refreshEventData}>↻ Refrescar</button>
                    <button className="danger-button" onClick={onLogout}>Salir</button>
                </div>
            </div>

            <div className="pod-card">
                <h3 style={{ color: 'var(--text-primary)', margin: '0 0 0.5rem 0' }}>Torneo: {localEventData.title}</h3>
                <p style={{ margin: 0, color: 'var(--text-muted)' }}>Status: <span style={{ color: 'var(--accent-secondary)', fontWeight: 'bold' }}>{localEventData.status}</span></p>
            </div>

            {currentRound && currentPod ? (
                <div style={{ marginTop: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem', color: 'var(--accent-primary)' }}>Ronda {currentRound.round_number} - Mesa {currentPod.table_number}</h3>
                    <div className="leaderboard-list">
                        <div className="leaderboard-header leaderboard-row">
                            <span style={{ flex: 2 }}>Jugador</span>
                            <span>Estado</span>
                        </div>
                        {currentPod.players_ids.map(pid => {
                            const pInfo = localEventData.players.find(x => x.id === pid);
                            const confirmed = currentPod.confirmations?.[pid] === true;
                            return (
                                <div key={pid} className="leaderboard-row" style={{ background: pid === playerId ? 'rgba(56, 189, 248, 0.15)' : 'transparent' }}>
                                    <span className="player-name" style={{ flex: 2, fontWeight: pid === playerId ? 'bold' : 'normal' }}>
                                        {pInfo ? pInfo.alias : pid} {pid === playerId ? "(Tú)" : ""}
                                    </span>
                                    <span className="points" style={{ fontSize: '0.85rem' }}>
                                        {currentPod.winner_id === pid ? "🏆 Ganador" :
                                            (confirmed && !currentPod.winner_id && !currentPod.is_draw ? "✅ Confirmado" : "-")}
                                    </span>
                                </div>
                            )
                        })}
                    </div>

                    {renderActionPanel()}

                </div>
            ) : (
                <div style={{ marginTop: '2rem', padding: '2rem', textAlign: 'center', background: 'var(--bg-card)', borderRadius: '12px' }}>
                    <h3 style={{ color: 'var(--text-muted)' }}>Esperando emparejamientos...</h3>
                    <p style={{ marginTop: '0.5rem' }}>El organizador aún no ha lanzado tu ronda.</p>
                </div>
            )}

        </main>
    )
}

export default MyDashboard;
