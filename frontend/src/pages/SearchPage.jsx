import { useState } from "react";
import { searchDocuments } from "../api/api";

function SearchPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSearch() {
    if (!question.trim()) {
      setMessage("Please enter a question. ");
      return;
    }

    setLoading(true);
    setMessage("");

    try{
      const response = await searchDocuments(question);

      setAnswer(response.data.answer)
      setSources(response.data.sources)


    } catch (error) {
      console.error(error);
      setMessage("Search failed.");
    } finally {
      setLoading(false);
    }
    
  }
  
  return (
    <div>
      <h1>Ask Guidely</h1>

      <textarea
        placeholder="Ask a question..."
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        rows={4}
        cols={60}
      />

      <br />

      <button
        onClick={handleSearch}
        disabled={loading}
      >
        {loading ? "Searching..." : "Ask"}
      </button>

      {answer && (
        <div>
          <h2>Answer</h2>
          <p>{answer}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div>
          <h2>Sources</h2>

          {sources.map((source, index) =>(
            <div key={index}>
              <strong>{source.filename}</strong>
              <p>{source.snippet}</p>
            </div>
          ))}
        </div>
      )}

      {message && <p>{message}</p>}
    </div>
  );
}

export default SearchPage;