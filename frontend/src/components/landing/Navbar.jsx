import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Navbar.css";
import { LayoutDashboard, LogIn, LogOut, ChevronDown } from "lucide-react";
import { isAuthenticated, getUserProfile, logoutUser } from "../../api/auth";

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [authed, setAuthed] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    Promise.resolve().then(() => {
      const isUserAuthed = isAuthenticated();
      setAuthed(isUserAuthed);
      setUserProfile(isUserAuthed ? getUserProfile() : null);
    });
  }, [location.pathname]);

  const handleLogout = () => {
    logoutUser();
    setAuthed(false);
    setUserProfile(null);
    setIsDropdownOpen(false);
    navigate("/");
  };

  const handleNavClick = (e, targetId) => {
    e.preventDefault();
    if (location.pathname !== "/") {
      navigate("/");
      setTimeout(() => {
        const elem = document.getElementById(targetId);
        if (elem) elem.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } else {
      const elem = document.getElementById(targetId);
      if (elem) elem.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header className="navbar">
      <div className="navbar__container">
        {/* Brand Logo */}
        <Link to="/" className="navbar__logo">
          <div className="navbar__logoIcon">
            <span>S</span>
          </div>
          <span className="navbar__logoText">Scriptloom</span>
        </Link>

        {/* Center Nav Links */}
        <nav className="navbar__centerNav">
          <a href="#features" onClick={(e) => handleNavClick(e, "features")} className="navbar__link">
            Pipeline
          </a>
          <a href="#comparison" onClick={(e) => handleNavClick(e, "comparison")} className="navbar__link">
            Why Scriptloom
          </a>
          <a href="#pricing" onClick={(e) => handleNavClick(e, "pricing")} className="navbar__link">
            Pricing
          </a>
        </nav>

        {/* Right CTA Actions */}
        <div className="navbar__right">
          {authed && userProfile ? (
            <>
              <Link to="/dashboard" className="navbar__dashboardBtn">
                <LayoutDashboard size={15} />
                <span>Go to Dashboard</span>
              </Link>

              {/* User Dropdown */}
              <div className="navbar__profileWrapper">
                <button
                  className="navbar__profileBtn"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                >
                  <img
                    src={userProfile.avatarUrl}
                    alt={userProfile.name}
                    className="navbar__avatarImg"
                  />
                  <span className="navbar__userName">{userProfile.name}</span>
                  <ChevronDown size={14} />
                </button>

                {isDropdownOpen && (
                  <div className="navbar__dropdownMenu">
                    <div className="navbar__dropdownHeader">
                      <strong>{userProfile.name}</strong>
                      <p>{userProfile.email}</p>
                    </div>
                    <div className="navbar__dropdownDivider" />
                    <button onClick={() => { setIsDropdownOpen(false); navigate("/dashboard"); }}>
                      <LayoutDashboard size={15} /> Dashboard
                    </button>
                    <button className="navbar__logoutBtn" onClick={handleLogout}>
                      <LogOut size={15} /> Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar__linkBtn">
                <LogIn size={15} />
                <span>Sign In</span>
              </Link>

              <Link to="/register" className="navbar__dashboardBtn">
                <span>Get Started Free</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
