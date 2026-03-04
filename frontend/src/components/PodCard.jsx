import React from 'react';
import { Draggable } from '@hello-pangea/dnd';

function PodCard({ pod, activeRound, eventData, handleReportWinner, handleReportDraw }) {
    const isFinished = !!pod.winner_id;
    const isDraw = pod.is_draw;
    const isDisputed = pod.is_disputed;
    const isPending = !isFinished && !isDraw && (pod.proposed_winner_id || pod.proposed_is_draw);

    let cardClass = 'pod-card glass-panel-inner hover-lift';
    if (isFinished) cardClass += ' is-finished';
    if (isDraw) cardClass += ' is-draw';
    if (isDisputed) cardClass += ' is-disputed';
    if (isPending) cardClass += ' is-pending';

    return (
        <div className={cardClass} style={
            isDisputed ? { border: '2px solid var(--danger-color)', background: 'rgba(239, 68, 68, 0.1)' } :
                isPending ? { border: '2px solid var(--accent-secondary)', background: 'rgba(245, 158, 11, 0.1)' } : {}
        }>
            <div className="pod-header">
                <h4>Mesa {pod.table_number}</h4>
                {pod.is_draw && <span className="status-badge success" style={{ marginLeft: '10px' }}>Empate ✓</span>}
                {pod.winner_id && <span className="status-badge success" style={{ marginLeft: '10px' }}>Ganador ✓</span>}
                {isDisputed && <span className="status-badge danger" style={{ marginLeft: '10px', background: 'var(--danger-color)' }}>Disputa ⚠️</span>}
                {isPending && <span className="status-badge warning" style={{ marginLeft: '10px', background: 'var(--accent-secondary)' }}>Falta Confirmar ⏳</span>}
            </div>

            <div className="pod-players-list">
                {pod.players_ids.map((playerId, index) => {
                    const playerInfo = eventData.players.find(p => p.id === playerId);
                    const alias = playerInfo ? playerInfo.alias : "Desconocido";
                    const isWinner = pod.winner_id === playerId;

                    return (
                        <Draggable key={playerId.toString()} draggableId={playerId.toString()} index={index}>
                            {(provided, snapshot) => (
                                <div
                                    className={`pod-player-row ${isWinner ? 'is-winner' : ''} ${snapshot.isDragging ? 'is-dragging' : ''}`}
                                    ref={provided.innerRef}
                                    {...provided.draggableProps}
                                    {...provided.dragHandleProps}
                                    style={{
                                        ...provided.draggableProps.style,
                                        opacity: snapshot.isDragging ? 0.8 : 1,
                                    }}
                                >
                                    <span className="player-alias">
                                        <span className="drag-handle" style={{ marginRight: '8px', opacity: 0.5 }}>≡</span>
                                        {alias}
                                    </span>
                                    <button className={`win-action-btn ${isWinner ? 'active-win' : ''}`}
                                        onClick={() => handleReportWinner(pod.id, playerId, alias)}>
                                        {isWinner ? '🏆 Ganador' : 'Win'}
                                    </button>
                                </div>
                            )}
                        </Draggable>
                    );
                })}
            </div>
            <hr className="glass-divider" />

            <button className={`draw-action-btn ${pod.is_draw ? 'active-draw' : ''}`}
                onClick={() => handleReportDraw(pod.id)}>
                🤝 Empate (Draw)
            </button>
        </div>
    );
}

export default PodCard;
