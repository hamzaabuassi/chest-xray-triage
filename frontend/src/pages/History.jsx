import { useEffect, useState } from "react";
import api from "../api/axios";

const PAGE_SIZE = 8;

export default function History() {
  const [scans, setScans] = useState([]);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    api
      .get("/scans/history")
      .then((res) => setScans(res.data))
      .catch((err) => setError(err.response?.data?.detail || "Failed to load history"));
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/scans/${id}`);
      setScans((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete scan");
    }
  };

  const tierClass = {
    Low: "tier-low",
    Medium: "tier-medium",
    High: "tier-high",
  };

  const totalPages = Math.ceil(scans.length / PAGE_SIZE) || 1;
  const pageScans = scans.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="page">
      <div className="eyebrow">Archive</div>
      <h2>Scan history</h2>
      <p className="page-sub">Every scan you've analyzed, most recent first.</p>

      {error && <div className="error-banner">{error}</div>}

      {scans.length === 0 && !error && (
        <div className="empty-state">No scans yet — analyze one from the dashboard.</div>
      )}

      <div className="history-grid">
        {pageScans.map((scan) => (
          <div key={scan.id} className="history-card">
            <button
              className="history-delete"
              onClick={() => handleDelete(scan.id)}
              title="Delete scan"
            >
              ×
            </button>
            <img
              src={`http://127.0.0.1:8000/${scan.gradcam_image_path}`}
              alt="scan"
            />
            <div className="history-meta">
              <div className="pred">{scan.prediction}</div>
              <span className={`tier-tab ${tierClass[scan.risk_tier?.split(" ")[0]] || "tier-medium"}`}>
                {scan.risk_tier}
              </span>
              <div className="conf" style={{ marginTop: 8 }}>
                {(scan.confidence * 100).toFixed(1)}% confidence
              </div>
              <time>{new Date(scan.created_at).toLocaleString()}</time>
            </div>
          </div>
        ))}
      </div>

      {scans.length > PAGE_SIZE && (
        <div className="pagination">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ‹
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((n) => (
            <button
              key={n}
              className={n === page ? "active" : ""}
              onClick={() => setPage(n)}
            >
              {n}
            </button>
          ))}
          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            ›
          </button>
        </div>
      )}
    </div>
  );
}
