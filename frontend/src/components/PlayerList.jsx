import React from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

function PlayerList({ players, handleStatusChange }) {
    if (!players || players.length === 0) {
        return (
            <div className="empty-state glass-panel-inner">
                <p>No hay jugadores en este evento o los datos están cargando...</p>
            </div>
        );
    }

    return (
        <React.Fragment>
            {players.map((player) => {
                const st = player.status.toLowerCase();
                const isDropped = st === 'dropped' || st === 'self_dropped';

                return (
                    <div key={player.id} className={`player-row-card glass-panel-inner hover-lift status-${st}`}>
                        <div className="player-info-col">
                            <h4>{player.alias}</h4>
                            <span className={`status-badge ${st}`}>
                                {st === 'self_dropped' ? 'VOLUNTARY DROP' : st.toUpperCase()}
                            </span>
                        </div>
                        <div className="player-actions-col">
                            <button className={`action-btn btn-pause ${st === 'paused' ? 'is-paused' : ''}`}
                                onClick={() => handleStatusChange(player.id, player.status, 'PAUSED')}
                                disabled={isDropped}>
                                {st === 'paused' ? '▶ Reanudar' : '⏸ Pausar'}
                            </button>
                            <button className={`action-btn btn-drop ${isDropped ? 'is-dropped' : ''}`}
                                onClick={() => handleStatusChange(player.id, player.status, isDropped ? 'active' : 'dropped')}>
                                {isDropped ? '♻️ Reactivar' : '🔥 Drop'}
                            </button>
                        </div>
                    </div>
                );
            })}
        </React.Fragment>
    );
}

export default PlayerList;
