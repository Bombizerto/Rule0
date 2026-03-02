import React, { useState, useEffect } from 'react'

function AdminView({ eventId }) {

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
            }
        } catch (err) {
            console.error("Fallo al conectar con el servidor:", err);
            alert("Error de conexión con el servidor");
        }
    };
    
    const handleStatusChange = async (playerId, currentStatus, action) => {
        try{
            if(currentStatus === action){
                alert("El estado del jugador ya es el mismo que el seleccionado");
                return;
            }
            const newstatus= action=== "PAUSED" && currentStatus === "paused" ? "active" : action.toLowerCase()
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
        }catch(err){
            console.error("Fallo al conectar con el servidor:", err);
            alert("Error de conexión con el servidor");
        }
    };
    return (
        <main className="glass-panel">
            <h2>Panel de Control del Organizador</h2>
            <p style={{ color: 'var(--text-muted)' }}>ID del Evento: {eventId}</p>

            <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <section>
                    <h3>Jugadores Registrados</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>

                        {/* Usamos el condicional ? para evitar que explote si no hay datos */}
                        {eventData?.players?.length > 0 ? (
                            // Si hay jugadores, los recorremos uno a uno con .map()
                            eventData.players.map((player) => (
                                <div
                                    key={player.id} // Requisito de React: cada tarjeta debe tener una key única
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        padding: '1rem',
                                        borderRadius: '12px',
                                        background: 'rgba(255, 255, 255, 0.05)',
                                        border: '1px solid rgba(255, 255, 255, 0.1)'
                                    }}
                                >
                                    <div>
                                        <h4 style={{ margin: 0, fontSize: '1.1rem' }}>{player.alias}</h4>
                                        <span style={{
                                            fontSize: '0.8rem',
                                            color: player.status === 'Active' ? 'var(--accent-secondary)' : '#95a5a6',
                                            fontWeight: 'bold'
                                        }}>
                                            ESTADO: {player.status}
                                        </span>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        {/* Botones preparados, pero aún no hacen nada */}
                                        <button className="primary-button" 
                                                style={{ 
                                                    padding: '0.4rem 0.8rem', 
                                                    fontSize: '0.8rem',
                                                    background: player.status === 'paused' ? '#f39c12' : 'var(--glass-border)'
                                                }} onClick={() => handleStatusChange(player.id, player.status, 'PAUSED')}>
                                            {player.status === 'paused' ? 'Reanudar' : 'Pausar'}
                                        </button>
                                        <button 
                                            className="primary-button" 
                                            style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', background: player.status === 'dropped' ? '#c0392b' : '#e74c3c' }}
                                            onClick={() => handleStatusChange(player.id, player.status, 'dropped')}
                                            disabled={player.status === 'dropped'}
                                        >
                                            {player.status === 'dropped' ? 'Eliminado' : 'Drop'}
</button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            // Si no hay jugadores o aún está cargando
                            <p style={{ color: 'var(--text-muted)' }}>Cargando o no hay jugadores en este evento.</p>
                        )}

                    </div>
                </section>
            </div>
        </main>
    )
}

export default AdminView
