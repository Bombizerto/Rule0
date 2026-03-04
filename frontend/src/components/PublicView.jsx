import React, { useState } from 'react';

function PublicView({ onLogin, onBack }) {
    const [joinCode, setJoinCode] = useState('');
    const [alias, setAlias] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const resp = await fetch(`http://127.0.0.1:8000/matchmaking/events/login-player`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    join_code: joinCode,
                    player_alias: alias,
                    password: password
                })
            });

            const data = await resp.json();

            if (!resp.ok) {
                throw new Error(data.detail || "Error al autenticar");
            }

            // Exitoso! Guardamos sesión y pasamos los datos hacia arriba
            localStorage.setItem('rule0_player_session', JSON.stringify({
                event_data: data.event_data,
                player_id: data.player_id,
                join_code: joinCode,
                alias: alias
            }));

            if (onLogin) {
                onLogin(data.event_data, data.player_id);
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="glass-panel" style={{ maxWidth: '500px', margin: '2rem auto' }}>
            <div style={{ marginBottom: '1.5rem', display: 'flex' }}>
                <button
                    className="primary-button"
                    onClick={onBack}
                    style={{ padding: '0.5rem 1rem', fontSize: '0.9rem', border: '1px solid var(--accent-primary)', background: 'transparent' }}
                >
                    ← Volver
                </button>
                <h2 style={{ margin: '0 0 0 1rem', display: 'flex', alignItems: 'center' }}>Portal de Jugador</h2>
            </div>

            {error && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem', textAlign: 'center', fontWeight: 'bold' }}>{error}</div>}

            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontWeight: 'bold' }}>Código de Unión (Join Code)</label>
                    <input
                        type="text"
                        className="search-input"
                        value={joinCode}
                        onChange={(e) => setJoinCode(e.target.value)}
                        required
                        placeholder="Ej: ABC-123"
                    />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontWeight: 'bold' }}>Tu Alias</label>
                    <input
                        type="text"
                        className="search-input"
                        value={alias}
                        onChange={(e) => setAlias(e.target.value)}
                        required
                        placeholder="Ej: Jugador1"
                    />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontWeight: 'bold' }}>Contraseña</label>
                    <input
                        type="password"
                        className="search-input"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        placeholder="Contraseña o PIN personal"
                    />
                </div>

                <button
                    type="submit"
                    className="primary-button"
                    style={{ width: '100%', marginTop: '1rem' }}
                    disabled={loading}
                >
                    {loading ? 'Conectando...' : 'Entrar al Torneo'}
                </button>
            </form>
        </main>
    );
}

export default PublicView;
