import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";
import { loginUser, loginWithGoogle } from "../../api/auth";
import { api } from "../../api/client";
import { ArrowRight, Lock, Mail, AlertCircle, CheckCircle2 } from "lucide-react";
import GoogleLoginButton from "../../components/auth/GoogleLoginButton";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [showReset, setShowReset] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  const handleGoogleSuccess = async (accessToken) => {
    setLoading(true);
    setError("");
    try {
      await loginWithGoogle(accessToken);
      navigate("/dashboard");
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
    setSuccess(false);

    try {
      await loginUser(email, password);
      navigate("/dashboard");
    } catch (err) {
      const msg = err.message || "Authentication failed. Please check your credentials.";
      if (err.status === 401) {
        setError("Invalid email or password. Double-check your credentials, or create a new account if you haven't registered.");
      } else if (err.status === 429) {
        setError("Too many login attempts. Please wait a minute and try again.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    if (!resetEmail) return;
    setResetLoading(true);
    setError("");
    try {
      await api.post("/auth/forgot-password", { email: resetEmail });
      setSuccess(true);
      setShowReset(false);
    } catch {
      setSuccess(true);
      setShowReset(false);
    } finally {
      setResetLoading(false);
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
          <h3>Welcome Back</h3>
          <p>Sign in to access your content studio.</p>
        </div>

        {error && (
          <div className="authCard__alert authCard__alert--error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {success && !showReset && (
          <div className="authCard__alert authCard__alert--success">
            <CheckCircle2 size={16} />
            <span>If that email is registered, a password reset link has been sent.</span>
          </div>
        )}

        {/* Google SSO — error-boundary isolated so it can't break email login */}
        <GoogleLoginButton onSuccess={handleGoogleSuccess} onError={setError} loading={loading} />

        <div className="authCard__divider">
          <span>or sign in with email</span>
        </div>

        <form onSubmit={handleSubmit} className="authCard__form">
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
            <span>{loading ? "Signing in..." : "Sign In"}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        {showReset ? (
          <form onSubmit={handleForgotPassword} className="authCard__form" style={{ marginTop: "16px" }}>
            <div className="authCard__inputGroup">
              <label>Reset Password</label>
              <div className="authCard__inputWrapper">
                <Mail size={16} className="authCard__inputIcon" />
                <input
                  type="email"
                  placeholder="you@company.com"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="authCard__row">
              <button type="submit" className="authCard__submitBtn" disabled={resetLoading}>
                <span>{resetLoading ? "Sending..." : "Send Reset Link"}</span>
              </button>
              <button type="button" className="authCard__submitBtn authCard__submitBtn--ghost" onClick={() => setShowReset(false)}>
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="authCard__forgotRow">
            <button type="button" className="authCard__forgotBtn" onClick={() => { setShowReset(true); setResetEmail(email); setError(""); }}>
              Forgot password?
            </button>
          </div>
        )}

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
