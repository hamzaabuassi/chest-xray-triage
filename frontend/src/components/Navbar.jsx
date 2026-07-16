import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="navbar">
      <span className="brand">Triage Assistant</span>
      <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : ""}>
        Dashboard
      </Link>
      <Link to="/history" className={location.pathname === "/history" ? "active" : ""}>
        History
      </Link>
      <button onClick={handleLogout}>Sign out</button>
    </nav>
  );
}
