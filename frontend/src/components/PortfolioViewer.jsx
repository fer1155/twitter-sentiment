import React, { useEffect, useState } from "react";

function PortfolioViewer() {
  const [portfolioData, setPortfolioData] = useState([]);
  const [nasdaqData, setNasdaqData] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/portfolio")
      .then((res) => res.json())
      .then((res) => {
        const portfolioEntries = Object.entries(res.portfolio_return || {});
        setPortfolioData(portfolioEntries);
        setNasdaqData(res.nasdaq_return || {});
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
            <th>Retorno Portafolio</th>
            <th>Retorno NASDAQ</th>
          </tr>
        </thead>
        <tbody>
          {portfolioData.slice(0, 20).map(([date, value], i) => (
            <tr key={i}>
              <td>{new Date(Number(date)).toISOString().slice(0, 10)}</td>
              <td>{Number(value).toFixed(4)}</td>
              <td>{Number(nasdaqData[date] || 0).toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PortfolioViewer;
