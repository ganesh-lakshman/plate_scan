import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/api";

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    background: "#1a1a2e",
  },
  card: {
    background: "#fff",
    borderRadius: 8,
    padding: 40,
    width: 380,
    boxShadow: "0 4px 24px rgba(0,0,0,0.2)",
  },
  title: { fontSize: 22, fontWeight: 700, marginBottom: 8, textAlign: "center" as const },
  subtitle: { fontSize: 13, color: "#888", textAlign: "center" as const, marginBottom: 24 },
  label: { display: "block", fontSize: 13, fontWeight: 600, marginBottom: 4 },
  input: {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #ddd",
    borderRadius: 4,
    fontSize: 14,
    marginBottom: 16,
  },
  button: {
    width: "100%",
    padding: 12,
    background: "#e94560",
    color: "#fff",
    border: "none",
    borderRadius: 4,
    fontWeight: 700,
    fontSize: 15,
    cursor: "pointer",
  },
  error: {
    background: "#fdecea",
    color: "#c0392b",
    padding: 10,
    borderRadius: 4,
    fontSize: 13,
    marginBottom: 12,
  },
  hint: {
    marginTop: 16,
    fontSize: 12,
    color: "#888",
    textAlign: "center" as const,
  },
};

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await authApi.login(username, password);
      login(res.data);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <form style={styles.card} onSubmit={handleSubmit}>
        <div style={styles.title}>🚗 Plate Scan</div>
        <div style={styles.subtitle}>Case Matching Service — Login</div>
        {error && <div style={styles.error}>{error}</div>}
        <label style={styles.label}>Username</label>
        <input
          style={styles.input}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="e.g. alice"
          autoFocus
        />
        <label style={styles.label}>Password</label>
        <input
          style={styles.input}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
        />
        <button style={styles.button} disabled={loading}>
          {loading ? "Signing in…" : "Sign In"}
        </button>
        <div style={styles.hint}>
          Seed users: <b>alice</b>, <b>adam</b> (Tenant A) &nbsp;|&nbsp;{" "}
          <b>bob</b>, <b>beth</b> (Tenant B)
          <br />
          Password for all: <b>password</b>
        </div>
      </form>
    </div>
  );
}
