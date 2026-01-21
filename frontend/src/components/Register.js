import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Added import

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const Register = () => {
    // 2. Initialize the navigation hook
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        full_names: "", 
        username: "",
        email: "", 
        password: "",
        confirmation: "",
        full_names: ""
    });
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState({ type: '', msg: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (formData.password !== formData.confirmation) {
            setStatus({ type: 'danger', msg: 'Passwords do not match!' });
            return;
        }

        setLoading(true);
        setStatus({ type: '', msg: '' });

        try {
            const response = await fetch(`${API_BASE_URL}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData) 
            });

            const data = await response.json();

            if (response.ok) {
                setStatus({ type: 'success', msg: 'Account created! Redirecting to login...' });
                
                // 3. Redirect to login after 2 seconds so the user can see the success message 🏎️
                setTimeout(() => { 
                    navigate('/login'); 
                }, 2000);
            } else {
                setStatus({ type: 'danger', msg: data.error || 'Registration failed' });
            }
        } catch (err) {
            setStatus({ type: 'danger', msg: 'Server connection error.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-3">
            {status.msg && <div className={`alert alert-${status.type}`}>{status.msg}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label className="form-label">Full Name</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        placeholder="Joe Doe"
                        value={formData.full_names}
                        onChange={(e) => setFormData({...formData, full_names: e.target.value})}
                        required 
                    />
                </div>
                <div className="form-group">
                    <label className="form-label">Username</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        value={formData.username}
                        onChange={(e) => setFormData({...formData, username: e.target.value})}
                        required 
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Email Address</label>
                    <input 
                        type="email" 
                        className="form-control" 
                        placeholder="email@example.com"
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                        required 
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Password</label>
                    <input 
                        type="password" 
                        className="form-control" 
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        required 
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Confirm Password</label>
                    <input 
                        type="password" 
                        className="form-control" 
                        value={formData.confirmation}
                        onChange={(e) => setFormData({...formData, confirmation: e.target.value})}
                        required 
                    />
                </div>

                <div className="mt-4">
                    <button type="submit" className="btn btn-success btn-block btn-lg" disabled={loading}>
                        {loading ? "Creating Account..." : "Register Now"}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default Register;