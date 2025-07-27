import React, { useEffect, useState } from "react";

function PortfolioViewer() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/portfolio")
      .then((res) => res.json())
      .then((res) => {
        const entries = Object.entries(res.portfolio_return || {});
        setData(entries);
      })
      .catch(() => setError("Error al obtener portafolio"));
  }, []);

  return (
    <div>
      <h2>Portafolio</h2>
      {error && <p>{error}</p>}
      <table border="1">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Retorno</th>
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 20).map(([date, value], i) => (
            <tr key={i}>
              <td>{new Date(Number(date)).toISOString().slice(0, 10)}</td>
              <td>{Number(value).toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PortfolioViewer;
