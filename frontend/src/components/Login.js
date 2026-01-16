import React, { useState } from 'react';

const Login = ({ setToken, onRegisterClick }) => {
    const [creds, setCreds] = useState({ username: "", password: "" });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // FIX: Map 'username' to 'username_or_email' for the backend
                body: JSON.stringify({
                    username_or_email: creds.username,
                    password: creds.password
                })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                setToken(data.access_token);
            } else {
                // Shows the "Invalid credentials" or "Missing..." error from Flask
                setError(data.error || "Invalid username or password");
            }
        } catch (err) {
            setError("Cannot connect to the backend server.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-3">
            {error && (
                <div className="alert alert-danger fade show" role="alert">
                    {error}
                </div>
            )}

            <form onSubmit={handleLogin}>
                <div className="form-group">
                    <label className="form-label">Username or Email</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        placeholder="Enter your username or email"
                        value={creds.username}
                        onChange={e => setCreds({...creds, username: e.target.value})}
                        required 
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Password</label>
                    <input 
                        type="password" 
                        className="form-control" 
                        placeholder="Enter your password"
                        value={creds.password}
                        onChange={e => setCreds({...creds, password: e.target.value})}
                        required 
                    />
                </div>

                <div className="mt-4">
                    <button 
                        type="submit" 
                        className="btn btn-primary btn-block btn-lg"
                        disabled={loading}
                    >
                        {loading ? "Verifying..." : "Secure Login"}
                    </button>
                    
                    <div className="text-center mt-3">
                        <p className="text-muted small">New to C$50 Finance?</p>
                        <button 
                            type="button" 
                            className="btn btn-outline-info btn-sm"
                            onClick={onRegisterClick}
                        >
                            Create an Account
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default Login;