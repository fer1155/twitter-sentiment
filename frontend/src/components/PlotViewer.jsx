// src/components/PlotViewer.jsx
import React, { useState } from "react";

function PlotViewer() {
  const [url, setUrl] = useState(null);

  const handleLoadPlot = () => {
    // Generamos una URL temporal con timestamp para evitar cache
    const timestamp = new Date().getTime();
    setUrl(`/api/plot?t=${timestamp}`);
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>📈 Retorno de Estrategia</h2>
      <button onClick={handleLoadPlot}>Cargar Gráfica</button>
      {url && (
        <div>
          <img src={url} alt="Gráfica del portafolio" style={{ maxWidth: "100%", marginTop: "1rem" }} />
        </div>
      )}
    </div>
  );
}

export default PlotViewer;
