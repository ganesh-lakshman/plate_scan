import { CaseItem } from "../services/api";

const statusColors: Record<string, string> = {
  pending_claim: "#f0ad4e",
  active: "#5cb85c",
  closed: "#999",
};

const styles: Record<string, React.CSSProperties> = {
  table: { width: "100%", borderCollapse: "collapse", fontSize: 14 },
  th: {
    textAlign: "left",
    padding: "10px 12px",
    borderBottom: "2px solid #dee2e6",
    fontWeight: 600,
    color: "#555",
  },
  td: { padding: "10px 12px", borderBottom: "1px solid #eee" },
  badge: {
    display: "inline-block",
    padding: "2px 10px",
    borderRadius: 12,
    color: "#fff",
    fontSize: 12,
    fontWeight: 600,
  },
  actionBtn: {
    padding: "4px 14px",
    borderRadius: 4,
    border: "none",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 13,
  },
  viewBtn: { background: "#0275d8", color: "#fff" },
  claimBtn: { background: "#e94560", color: "#fff", marginLeft: 6 },
};

interface Props {
  cases: CaseItem[];
  onView: (id: string) => void;
  onClaim: (id: string) => void;
  claiming: string | null;
}

export default function CaseTable({ cases, onView, onClaim, claiming }: Props) {
  if (cases.length === 0) {
    return <p style={{ color: "#888", padding: 20 }}>No cases to display.</p>;
  }

  return (
    <table style={styles.table}>
      <thead>
        <tr>
          <th style={styles.th}>VIN</th>
          <th style={styles.th}>Plate</th>
          <th style={styles.th}>Status</th>
          <th style={styles.th}>Tenant</th>
          <th style={styles.th}>Agent</th>
          <th style={styles.th}>Created</th>
          <th style={styles.th}>Actions</th>
        </tr>
      </thead>
      <tbody>
        {cases.map((c) => (
          <tr key={c.id}>
            <td style={styles.td}>
              <code>{c.vin}</code>
            </td>
            <td style={styles.td}>{c.plate || "—"}</td>
            <td style={styles.td}>
              <span
                style={{
                  ...styles.badge,
                  background: statusColors[c.status] || "#aaa",
                }}
              >
                {c.status}
              </span>
            </td>
            <td style={styles.td}>{c.tenant_name || c.tenant_id}</td>
            <td style={styles.td}>{c.agent_name || "—"}</td>
            <td style={styles.td}>
              {new Date(c.created_at).toLocaleDateString()}
            </td>
            <td style={styles.td}>
              <button
                style={{ ...styles.actionBtn, ...styles.viewBtn }}
                onClick={() => onView(c.id)}
              >
                View
              </button>
              {c.status === "pending_claim" && (
                <button
                  style={{ ...styles.actionBtn, ...styles.claimBtn }}
                  disabled={claiming === c.id}
                  onClick={() => onClaim(c.id)}
                >
                  {claiming === c.id ? "Claiming…" : "Claim"}
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
