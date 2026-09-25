import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState("Connexion...");

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((response) => response.json())
      .then((data) => {
        setStatus(data.status);
      })
      .catch((error) => {
        console.error(error);
        setStatus("Erreur de connexion");
      });
  }, []);

  return (
    <div>
      <h1>AI DJ Transition Engine</h1>
      <p>Backend status: {status}</p>
    </div>
  );
}

export default App;
