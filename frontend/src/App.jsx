import React from "react";
import PortfolioViewer from "./components/PortfolioViewer";
import SentimentViewer from "./components/SentimentViewer";
import PlotViewer from "./components/PlotViewer"; // ⬅️ nuevo

function App() {
  return (
    <div style={{ padding: "1rem" }}>
      <h1>📊 Twitter Sentiment Dashboard</h1>
      <SentimentViewer />
      <PortfolioViewer />
      <PlotViewer /> {/* ⬅️ nuevo */}
    </div>
  );
}

export default App;
