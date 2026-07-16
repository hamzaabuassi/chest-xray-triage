import { useState } from "react";
import api from "../api/axios";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setPreview(selected ? URL.createObjectURL(selected) : null);
    setResult(null);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post("/scans/predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const tierClass = {
    Low: "tier-low",
    Medium: "tier-medium",
    High: "tier-high",
  };

  return (
    <div className="page">
      <div className="eyebrow">Chest X-ray · DenseNet121</div>
      <h2>Read a scan</h2>
      <p className="page-sub">
        Upload a chest X-ray to get a prediction, a Grad-CAM explanation, and a triage priority.
      </p>

      <div className="model-notice">
        This model is trained specifically on chest X-rays. Other image types will not
        produce a meaningful result.
      </div>

      <div className="upload-zone">
        <p className="upload-hint">
          {file ? <strong>{file.name}</strong> : "Choose a chest X-ray image (JPEG or PNG) to begin."}
        </p>
        <input type="file" accept="image/*" onChange={handleFileChange} />
      </div>

      {preview && (
        <div className="lightboard">
          <figure>
            <figcaption>Original</figcaption>
            <img src={preview} alt="preview" />
          </figure>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="btn-primary"
        style={{ marginBottom: 24 }}
      >
        {loading && <span className="spinner" />}
        {loading ? "Analyzing…" : "Analyze X-ray"}
      </button>

      {error && <div className="error-banner">{error}</div>}

      {result && (
        <>
          <div className="lightboard">
            <figure>
              <figcaption>Grad-CAM explanation</figcaption>
              <img
                src={`http://127.0.0.1:8000/${result.gradcam_image_path}`}
                alt="gradcam"
              />
            </figure>
          </div>

          <div className="result-card">
            <div className="result-top">
              <div>
                <div className="confidence-label">Prediction</div>
                <h3>{result.prediction}</h3>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className="confidence-label">Confidence</div>
                <div className="confidence-readout">
                  {(result.confidence * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <span className={`tier-tab ${tierClass[result.risk_tier?.split(" ")[0]] || "tier-medium"}`}>
              {result.risk_tier} priority
            </span>

            <p className="disclaimer">
              This tool is a portfolio/educational demo and is not a certified medical
              diagnostic device. Always consult a radiologist or physician for actual diagnosis.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
