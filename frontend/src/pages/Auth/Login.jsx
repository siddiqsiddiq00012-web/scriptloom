import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";
import { loginUser, loginWithGoogle } from "../../api/auth";
import { ArrowRight, Lock, Mail, AlertCircle, CheckCircle2 } from "lucide-react";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleGoogleLogin = async () => {
    let targetEmail = email;
    if (!targetEmail) {
      targetEmail = window.prompt("Enter your Gmail address to sign in with Google:", "creator@gmail.com");
    }
    if (!targetEmail) return;

    const name = targetEmail.split("@")[0].replace(".", " ");
    const formattedName = name.charAt(0).toUpperCase() + name.slice(1);

    setLoading(true);
    setError("");

    try {
      await loginWithGoogle(
        targetEmail,
        formattedName,
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80"
      );
      setSuccess(true);
      setTimeout(() => navigate("/dashboard"), 500);
    } catch (err) {
      setError(err.message || "Google authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await loginUser(email, password);
      setSuccess(true);
      setTimeout(() => {
        navigate("/dashboard");
      }, 600);
    } catch (err) {
      setError(err.message || "Authentication failed. Please check your credentials.");
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
          <h3>Welcome Back to Scriptloom</h3>
          <p>AI Content OS & Personal Brand Engine for Knowledge Creators</p>
        </div>

        {error && (
          <div className="authCard__alert authCard__alert--error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="authCard__alert authCard__alert--success">
            <CheckCircle2 size={16} />
            <span>Authenticated! Redirecting to OS Workspace...</span>
          </div>
        )}

        {/* Google SSO Button */}
        <button type="button" className="authCard__googleBtn" onClick={handleGoogleLogin}>
          <svg width="18" height="18" viewBox="0 0 18 18">
            <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.259h2.908c1.702-1.567 2.684-3.874 2.684-6.617z" />
            <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" />
            <path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" />
            <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" />
          </svg>
          <span>Continue with Google / Gmail</span>
        </button>

        <div className="authCard__divider">
          <span>or sign in with email</span>
        </div>

        <form onSubmit={handleSubmit} className="authCard__form">
          <div className="authCard__inputGroup">
            <label>Work Email</label>
            <div className="authCard__inputWrapper">
              <Mail size={16} className="authCard__inputIcon" />
              <input
                type="email"
                placeholder="creator@gmail.com"
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
            <span>{loading ? "Authenticating..." : "Sign In to OS Workspace"}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        <div className="authCard__footer">
          <p>
            Don't have an account? <Link to="/register">Create Account</Link>
          </p>
          <Link to="/" className="authCard__homeLink">
            ← Return to Homepage
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;