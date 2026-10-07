import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { casesApi, CaseItem } from "../services/api";
import CaseTable from "../components/CaseTable";

const styles: Record<string, React.CSSProperties> = {
  section: {
    background: "#fff",
    borderRadius: 8,
    padding: 24,
    marginBottom: 24,
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  },
  h2: { fontSize: 18, fontWeight: 700, marginBottom: 16 },
  filterBar: { display: "flex", gap: 8, marginBottom: 16 },
  filterBtn: {
    padding: "6px 16px",
    borderRadius: 20,
    border: "1px solid #ddd",
    background: "#fff",
    cursor: "pointer",
    fontSize: 13,
    fontWeight: 600,
  },
  filterActive: {
    background: "#1a1a2e",
    color: "#fff",
    border: "1px solid #1a1a2e",
  },
  error: {
    background: "#fdecea",
    color: "#c0392b",
    padding: 10,
    borderRadius: 4,
    fontSize: 13,
    marginBottom: 12,
  },
};

type FilterStatus = "all" | "pending_claim" | "active" | "closed";

export default function DashboardPage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [filter, setFilter] = useState<FilterStatus>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [claiming, setClaiming] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchCases = async (status?: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await casesApi.list(status === "all" ? undefined : status);
      setCases(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load cases.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases(filter);
  }, [filter]);

  const handleClaim = async (caseId: string) => {
    setClaiming(caseId);
    try {
      await casesApi.claim(caseId);
      await fetchCases(filter);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Claim failed.");
    } finally {
      setClaiming(null);
    }
  };

  const filters: { label: string; value: FilterStatus }[] = [
    { label: "All", value: "all" },
    { label: "Pending Claim", value: "pending_claim" },
    { label: "Active", value: "active" },
    { label: "Closed", value: "closed" },
  ];

  return (
    <>
      <div style={styles.section}>
        <h2 style={styles.h2}>Cases Dashboard</h2>
        <div style={styles.filterBar}>
          {filters.map((f) => (
            <button
              key={f.value}
              style={{
                ...styles.filterBtn,
                ...(filter === f.value ? styles.filterActive : {}),
              }}
              onClick={() => setFilter(f.value)}
            >
              {f.label}
            </button>
          ))}
        </div>
        {error && <div style={styles.error}>{error}</div>}
        {loading ? (
          <p style={{ padding: 20, color: "#888" }}>Loading…</p>
        ) : (
          <CaseTable
            cases={cases}
            onView={(id) => navigate(`/cases/${id}`)}
            onClaim={handleClaim}
            claiming={claiming}
          />
        )}
      </div>
    </>
  );
}
