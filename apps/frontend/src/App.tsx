import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export function App() {
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => setStatus(r.ok ? "ok" : "error"))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <main>
      <h1>Plataforma de Análise de Dados</h1>
      <p>API: {status}</p>
    </main>
  );
}
