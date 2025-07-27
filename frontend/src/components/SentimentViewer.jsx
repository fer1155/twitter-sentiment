import React, { useEffect, useState } from "react";

function SentimentViewer() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/sentiment")
      .then((res) => res.json())
      .then(setData)
      .catch(() => setError("Error al obtener sentimiento"));
  }, []);

  return (
    <div>
      <h2>Datos de Sentimiento</h2>
      {error && <p>{error}</p>}
      <table border="1">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Símbolo</th>
            <th>Likes</th>
            <th>Comentarios</th>
            <th>Engagement Ratio</th>
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 10).map((row, i) => (
            <tr key={i}>
              <td>{row.date}</td>
              <td>{row.symbol}</td>
              <td>{row.twitterLikes}</td>
              <td>{row.twitterComments}</td>
              <td>{Number(row.engagement_ratio).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SentimentViewer;
