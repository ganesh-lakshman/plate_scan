import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { casesApi, CaseItem, ScanItem } from "../services/api";
import ScanTable from "../components/ScanTable";

const styles: Record<string, React.CSSProperties> = {
  backBtn: {
    background: "transparent",
    border: "none",
    color: "#0275d8",
    cursor: "pointer",
    fontSize: 14,
    marginBottom: 16,
    padding: 0,
  },
  card: {
    background: "#fff",
    borderRadius: 8,
    padding: 24,
    marginBottom: 24,
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  },
  h2: { fontSize: 18, fontWeight: 700, marginBottom: 16 },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    gap: 12,
    marginBottom: 16,
  },
  field: { fontSize: 13 },
  label: { fontWeight: 600, color: "#555", display: "block", marginBottom: 2 },
  badge: {
    display: "inline-block",
    padding: "2px 10px",
    borderRadius: 12,
    color: "#fff",
    fontSize: 12,
    fontWeight: 600,
  },
  claimBtn: {
    padding: "8px 20px",
    background: "#e94560",
    color: "#fff",
    border: "none",
    borderRadius: 4,
    fontWeight: 700,
    cursor: "pointer",
    fontSize: 14,
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

const statusColors: Record<string, string> = {
  pending_claim: "#f0ad4e",
  active: "#5cb85c",
  closed: "#999",
};

export default function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<CaseItem | null>(null);
  const [scans, setScans] = useState<ScanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [claiming, setClaiming] = useState(false);

  useEffect(() => {
    if (!caseId) return;

    const load = async () => {
      setLoading(true);
      try {
        const [casesRes, scansRes] = await Promise.all([
          casesApi.list(),
          casesApi.scans(caseId),
        ]);
        const found = casesRes.data.find((c) => c.id === caseId) || null;
        setCaseData(found);
        setScans(scansRes.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load case details.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [caseId]);

  const handleClaim = async () => {
    if (!caseId) return;
    setClaiming(true);
    try {
      await casesApi.claim(caseId);
      const [casesRes, scansRes] = await Promise.all([
        casesApi.list(),
        casesApi.scans(caseId),
      ]);
      setCaseData(casesRes.data.find((c) => c.id === caseId) || null);
      setScans(scansRes.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Claim failed.");
    } finally {
      setClaiming(false);
    }
  };

  if (loading) return <p style={{ padding: 20, color: "#888" }}>Loading…</p>;
  if (error) return <div style={styles.error}>{error}</div>;
  if (!caseData) return <p>Case not found.</p>;

  return (
    <>
      <button style={styles.backBtn} onClick={() => navigate("/")}>
        ← Back to Dashboard
      </button>

      <div style={styles.card}>
        <h2 style={styles.h2}>Case Details</h2>
        <div style={styles.grid}>
          <div style={styles.field}>
            <span style={styles.label}>VIN</span>
            <code>{caseData.vin}</code>
          </div>
          <div style={styles.field}>
            <span style={styles.label}>Plate</span>
            {caseData.plate || "—"}
          </div>
          <div style={styles.field}>
            <span style={styles.label}>Status</span>
            <span
              style={{
                ...styles.badge,
                background: statusColors[caseData.status] || "#aaa",
              }}
            >
              {caseData.status}
            </span>
          </div>
          <div style={styles.field}>
            <span style={styles.label}>Tenant</span>
            {caseData.tenant_name || caseData.tenant_id}
          </div>
          <div style={styles.field}>
            <span style={styles.label}>Agent</span>
            {caseData.agent_name || "—"}
          </div>
          <div style={styles.field}>
            <span style={styles.label}>Created</span>
            {new Date(caseData.created_at).toLocaleString()}
          </div>
          {caseData.claimed_at && (
            <div style={styles.field}>
              <span style={styles.label}>Claimed</span>
              {new Date(caseData.claimed_at).toLocaleString()}
            </div>
          )}
        </div>
        {caseData.status === "pending_claim" && (
          <button
            style={styles.claimBtn}
            onClick={handleClaim}
            disabled={claiming}
          >
            {claiming ? "Claiming…" : "Claim This Case"}
          </button>
        )}
      </div>

      <div style={styles.card}>
        <h2 style={styles.h2}>
          Location Trail ({scans.length} scan{scans.length !== 1 ? "s" : ""})
        </h2>
        <ScanTable scans={scans} />
      </div>
    </>
  );
}
