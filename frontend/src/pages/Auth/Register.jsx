import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";
import "./Register.css";
import { registerUser } from "../../api/auth";
import { ArrowRight, Lock, Mail, User, AlertCircle } from "lucide-react";

function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setError("Please fill out all fields.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await registerUser(name, email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Registration failed. Email may already be registered.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="authPage">
      <div className="authCard">
        <Link to="/" className="authCard__logo">
          <div className="authCard__logoIcon">
            <span>S</span>
          </div>
          <h2>Scriptloom</h2>
        </Link>

        <div className="authCard__header">
          <h3>Create Your Free Account</h3>
          <p>Start repurposing long-form content today.</p>
        </div>

        {error && (
          <div className="authCard__alert authCard__alert--error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="authCard__form">
          <div className="authCard__inputGroup">
            <label>Full Name</label>
            <div className="authCard__inputWrapper">
              <User size={16} className="authCard__inputIcon" />
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="authCard__inputGroup">
            <label>Email</label>
            <div className="authCard__inputWrapper">
              <Mail size={16} className="authCard__inputIcon" />
              <input
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="authCard__inputGroup">
            <label>Password</label>
            <div className="authCard__inputWrapper">
              <Lock size={16} className="authCard__inputIcon" />
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="authCard__submitBtn" disabled={loading}>
            <span>{loading ? "Creating Account..." : "Create Account"}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        <div className="authCard__footer">
          <p>
            Already have an account? <Link to="/login">Sign In</Link>
          </p>
          <Link to="/" className="authCard__homeLink">
            ← Return to Homepage
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
