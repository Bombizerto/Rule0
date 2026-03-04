import React, { useState } from 'react';

function LoginView({ onLoginSuccess }) {
    const [alias, setAlias] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ alias, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Fallo en la autenticación');
            }

            const userData = await response.json();
            // userData tiene: id, alias, role
            onLoginSuccess(userData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-panel" style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>Iniciar Sesión</h2>
            {error && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Alias / Usuario</label>
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

                <button
                    type="submit"
                    className="primary-button"
                    style={{ width: '100%', padding: '1rem', fontSize: '1.1rem' }}
                    disabled={loading || !alias || !password}
                >
                    {loading ? 'Cargando...' : 'Entrar'}
                </button>
            </form>

            <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Versia Way System • Acceso Restringido
            </p>
        </div>
    );
}

export default LoginView;
