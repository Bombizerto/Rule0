import React, { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

function LoginView({ onLoginSuccess }) {
    const [isGuestMode, setIsGuestMode] = useState(false);
    const [isRegistering, setIsRegistering] = useState(false);
    const [alias, setAlias] = useState('');
    const [password, setPassword] = useState('');
    const [joinCode, setJoinCode] = useState('');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        if (code) {
            setIsGuestMode(true);
            setJoinCode(code.toUpperCase());
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            let url = `${API_BASE_URL}/auth/login`;
            if (isGuestMode) url = `${API_BASE_URL}/auth/guest_join`;
            else if (isRegistering) url = `${API_BASE_URL}/auth/signup`;

            let bodyObj;
            if (isGuestMode) {
                // Recuperar el device_token para ESTE alias concreto (no global)
                const storedTokens = JSON.parse(localStorage.getItem('rule0_guest_tokens') || '{}');
                bodyObj = { alias, join_code: joinCode };
                if (storedTokens[alias]) bodyObj.device_token = storedTokens[alias];
            } else {
                bodyObj = { alias, password };
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bodyObj)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Fallo en la operación');
            }

            const userData = await response.json();

            // Si el servidor devuelve un device_token (invitados), guardarlo asociado a este alias
            if (userData.device_token) {
                const storedTokens = JSON.parse(localStorage.getItem('rule0_guest_tokens') || '{}');
                storedTokens[userData.alias] = userData.device_token;
                localStorage.setItem('rule0_guest_tokens', JSON.stringify(storedTokens));
            }

            onLoginSuccess(userData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-panel" style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>
                {isGuestMode ? 'Unirse como Invitado' : (isRegistering ? 'Crear Cuenta' : 'Iniciar Sesión')}
            </h2>

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                <button
                    type="button"
                    onClick={() => { setIsGuestMode(false); setError(''); }}
                    style={{
                        flex: 1, padding: '0.5rem',
                        background: !isGuestMode ? 'var(--accent-primary)' : 'transparent',
                        color: !isGuestMode ? 'black' : 'white',
                        border: '1px solid var(--accent-primary)', borderRadius: '8px', cursor: 'pointer'
                    }}
                >
                    Registrado
                </button>
                <button
                    type="button"
                    onClick={() => { setIsGuestMode(true); setError(''); }}
                    style={{
                        flex: 1, padding: '0.5rem',
                        background: isGuestMode ? 'var(--accent-secondary)' : 'transparent',
                        color: 'white',
                        border: '1px solid var(--accent-secondary)', borderRadius: '8px', cursor: 'pointer'
                    }}
                >
                    Invitado
                </button>
            </div>

            {error && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Alias / Nombre en Juego</label>
                    <input
                        type="text"
                        value={alias}
                        onChange={e => setAlias(e.target.value)}
                        required
                        style={{
                            width: '100%', padding: '0.75rem', borderRadius: '8px',
                            border: '1px solid var(--border)', background: 'rgba(255,255,255,0.05)', color: 'white'
                        }}
                    />
                </div>

                {!isGuestMode ? (
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Contraseña</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                            style={{
                                width: '100%', padding: '0.75rem', borderRadius: '8px',
                                border: '1px solid var(--border)', background: 'rgba(255,255,255,0.05)', color: 'white'
                            }}
                        />
                    </div>
                ) : (
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Código de Invitación</label>
                        <input
                            type="text"
                            value={joinCode}
                            onChange={e => setJoinCode(e.target.value.toUpperCase())}
                            placeholder="Ej: MTG99"
                            required
                            style={{
                                width: '100%', padding: '0.75rem', borderRadius: '8px',
                                border: '1px solid var(--border)', background: 'rgba(255,255,255,0.05)', color: 'white',
                                textTransform: 'uppercase'
                            }}
                        />
                    </div>
                )}

                <button
                    type="submit"
                    className="primary-button"
                    style={{ width: '100%', padding: '1rem', fontSize: '1.1rem' }}
                    disabled={loading || !alias || (!isGuestMode ? !password : !joinCode)}
                >
                    {loading ? 'Cargando...' : (isGuestMode ? 'Unirme al Torneo' : (isRegistering ? 'Registrarse' : 'Entrar'))}
                </button>
            </form>

            {!isGuestMode && (
                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                    <button
                        type="button"
                        onClick={() => { setIsRegistering(!isRegistering); setError(''); }}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--accent-secondary)',
                            cursor: 'pointer',
                            textDecoration: 'underline'
                        }}
                    >
                        {isRegistering ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Crea una'}
                    </button>
                </div>
            )}

            <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Versia Way System • Acceso Restringido
            </p>
        </div>
    );
}

export default LoginView;
