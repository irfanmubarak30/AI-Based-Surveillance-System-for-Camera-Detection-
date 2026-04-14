import React, { useEffect, useState } from "react";
import "./styles.css";

const App = () => {
  const [logs, setLogs] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const backendURL = "http://localhost:5000";

  // Fetch logs (captured images) from backend
  const fetchLogs = async () => {
    try {
      const response = await fetch(`${backendURL}/logs`);
      const data = await response.json();
      setLogs(data.images.reverse()); // Show latest images first
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000); // Refresh logs every 5 seconds
    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  return (
    <div className="app-container">
      <h1 className="title">📷 AI Phone Detection</h1>

      {/* Live Camera Feed */}
      <div className="live-feed">
        <h2>Live Camera Feed</h2>
        <div className="bounding-box-container">
          <img
            src={`${backendURL}/video_feed`}
            alt="Live Camera"
            className="camera-feed"
          />
          <div className="bounding-box">
            <span className="confidence"></span>
          </div>
        </div>
      </div>

      {/* Logs Section */}
      <div className="screenshot-section">
        <h2>Captured Screenshots</h2>
        <div className="screenshot-grid">
          {logs.length === 0 ? (
            <p>No images captured yet.</p>
          ) : (
            logs.map((img, index) => (
              <div key={index} className="screenshot" onClick={() => setSelectedImage(`${backendURL}/images/${img}`)}>
                <img src={`${backendURL}/images/${img}`} alt={`Capture ${index}`} />
                <div className="bounding-box">
                  <span className="confidence"></span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Enlarged Image Modal */}
      {selectedImage && (
        <div className="modal" onClick={() => setSelectedImage(null)}>
          <div className="modal-content">
            <img src={selectedImage} alt="Enlarged Capture" className="enlarged-image" />
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
