import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const styles: Record<string, React.CSSProperties> = {
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 24px",
    background: "#1a1a2e",
    color: "#fff",
  },
  title: { fontSize: 18, fontWeight: 700 },
  userInfo: { display: "flex", alignItems: "center", gap: 16, fontSize: 14 },
  badge: {
    background: "#e94560",
    padding: "2px 10px",
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 600,
  },
  logoutBtn: {
    background: "transparent",
    color: "#fff",
    border: "1px solid #555",
    borderRadius: 4,
    padding: "4px 12px",
    cursor: "pointer",
  },
  main: { maxWidth: 1100, margin: "0 auto", padding: 24 },
};

export default function Layout() {
  const { username, tenantName, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <>
      <header style={styles.header}>
        <div
          style={{ ...styles.title, cursor: "pointer" }}
          onClick={() => navigate("/")}
        >
          🚗 Plate Scan & Case Matching
        </div>
        <div style={styles.userInfo}>
          <span>{username}</span>
          <span style={styles.badge}>{tenantName}</span>
          <span style={{ opacity: 0.7 }}>{role}</span>
          <button style={styles.logoutBtn} onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>
      <main style={styles.main}>
        <Outlet />
      </main>
    </>
  );
}
