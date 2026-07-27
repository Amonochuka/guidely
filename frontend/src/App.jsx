import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    api
      .get("/")
      .then((response) => {
        setMessage(response.data.message);
      })
      .catch(() => {
        setMessage("Could not connect to backend.");
      });
  }, []);

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial",
      }}
    >
      <h1>Guidely</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;