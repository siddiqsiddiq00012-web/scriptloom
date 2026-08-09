import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "./Login.css";
import { resetPassword } from "../../api/auth";
import { Lock, AlertCircle, CheckCircle2 } from "lucide-react";

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setError("This password reset link is invalid. Please request a new one.");
      return;
    }
    if (!password || password.length < 6) {
      setError("Your new password must be at least 6 characters long.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess(false);
    try {
      await resetPassword(token, password);
      setSuccess(true);
    } catch (err) {
      if (err.status === 400) {
        setError("This password reset link is invalid or has expired. Please request a new one.");
      } else if (err.status === 429) {
        setError("Too many requests. Please wait a minute and try again.");
      } else {
        setError(err?.message || "Something went wrong. Please try again.");
      }
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
          <h3>Reset Password</h3>
          <p>Choose a new password for your account.</p>
        </div>

        {error && (
          <div className="authCard__alert authCard__alert--error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {success ? (
          <>
            <div className="authCard__alert authCard__alert--success">
              <CheckCircle2 size={16} />
              <span>Your password has been updated. You can now sign in.</span>
            </div>
            <Link to="/login" className="authCard__submitBtn" style={{ textDecoration: "none" }}>
              Sign In
            </Link>
          </>
        ) : !token ? (
          <div className="authCard__alert authCard__alert--error">
            <AlertCircle size={16} />
            <span>This password reset link is invalid. Please request a new one from the login page.</span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="authCard__form">
            <div className="authCard__inputGroup">
              <label>New Password</label>
              <div className="authCard__inputWrapper">
                <Lock size={16} className="authCard__inputIcon" />
                <input
                  type="password"
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={6}
                  required
                />
              </div>
            </div>

            <div className="authCard__inputGroup">
              <label>Confirm New Password</label>
              <div className="authCard__inputWrapper">
                <Lock size={16} className="authCard__inputIcon" />
                <input
                  type="password"
                  placeholder="Re-enter your new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  minLength={6}
                  required
                />
              </div>
            </div>

            <button type="submit" className="authCard__submitBtn" disabled={loading}>
              <span>{loading ? "Updating..." : "Update Password"}</span>
            </button>
          </form>
        )}

        <div className="authCard__footer">
          <p>
            Remembered your password? <Link to="/login">Back to Sign In</Link>
          </p>
          <Link to="/" className="authCard__homeLink">
            ← Return to Homepage
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ResetPassword;
