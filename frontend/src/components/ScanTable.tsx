import { ScanItem } from "../services/api";

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
  link: { color: "#0275d8" },
};

interface Props {
  scans: ScanItem[];
}

export default function ScanTable({ scans }: Props) {
  if (scans.length === 0) {
    return <p style={{ color: "#888", padding: 20 }}>No scans recorded yet.</p>;
  }

  return (
    <table style={styles.table}>
      <thead>
        <tr>
          <th style={styles.th}>#</th>
          <th style={styles.th}>Scanned At</th>
          <th style={styles.th}>Plate</th>
          <th style={styles.th}>Latitude</th>
          <th style={styles.th}>Longitude</th>
          <th style={styles.th}>Image</th>
        </tr>
      </thead>
      <tbody>
        {scans.map((s, i) => (
          <tr key={s.id}>
            <td style={styles.td}>{i + 1}</td>
            <td style={styles.td}>
              {new Date(s.scanned_at).toLocaleString()}
            </td>
            <td style={styles.td}>{s.plate}</td>
            <td style={styles.td}>{s.latitude.toFixed(4)}</td>
            <td style={styles.td}>{s.longitude.toFixed(4)}</td>
            <td style={styles.td}>
              {s.image_url ? (
                <a href={s.image_url} target="_blank" rel="noreferrer" style={styles.link}>
                  View
                </a>
              ) : (
                "—"
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
