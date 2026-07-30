import "./Navbar.css";
import { MoreHorizontal } from "lucide-react";

function Navbar({ onToggleDrawer }) {
  return (
    <header className="navbar">
      <div className="navbar__container">
        <div className="navbar__logo">
          <div className="navbar__logoIcon">
            <span>S</span>
          </div>
          <span className="navbar__logoText">Scriptloom</span>
        </div>

        <div className="navbar__right">
          <button 
            className="navbar__menuTrigger"
            onClick={onToggleDrawer}
            title="Toggle AI Workspace Navigation"
            aria-label="Toggle drawer"
          >
            <MoreHorizontal size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;