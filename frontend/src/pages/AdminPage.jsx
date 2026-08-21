import { useEffect, useRef, useState } from "react";
import { getDocuments, uploadDocument } from "../api/api";

function AdminPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [documents, setDocuments] = useState([]);
  const [documentsError, setDocumentsError] = useState("");
  const fileInputRef = useRef(null);

  function getErrorMessage(error, fallback) {
    return error.response?.data?.detail || fallback;
  }

  async function loadDocuments() {
    try {
      const response = await getDocuments();
      setDocuments(response.data.documents);
      setDocumentsError("");
    } catch (error) {
      console.error("Error loading documents:", error);
      setDocumentsError(getErrorMessage(error, "Could not load indexed documents."));
    }
  }

  useEffect(() => {
    let active = true;

    getDocuments()
      .then((response) => {
        if (active) {
          setDocuments(response.data.documents);
          setDocumentsError("");
        }
      })
      .catch((error) => {
        console.error("Error loading documents:", error);
 
        if (active) {
          setDocumentsError(getErrorMessage(error, "Could not load indexed documents."));
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleUpload() {
    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await uploadDocument(formData);
      setMessage(response.data.message);
      setFile(null);
      await loadDocuments();

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      
    } catch (error) {
      console.error("Error uploading document:", error);
      setMessage(getErrorMessage(error, "Failed to upload document."));
    }
    finally {
      setUploading(false);
    }
  }

  return (
    <div className="container">
      <h1>Upload Documents</h1>
      <p>
        To re-index a document, upload a changed version using the same filename.
      </p>

      <input
        ref={fileInputRef}
        type="file"
        onChange={(event) => setFile(event.target.files[0])}
      />

      <button 
        onClick={handleUpload}
        disabled={uploading}
      >
        {uploading? "Uploading..." : "Upload"}
      </button>
      {message && <p>{message}</p>}

      <h2>Indexed Documents</h2>

      {documentsError && <p>{documentsError}</p>}

      {!documentsError && documents.length === 0 && (
        <p>No documents have been indexed yet.</p>
      )}

      {documents.length > 0 && (
        <ul>
          {documents.map((document) => (
            <li key={document.filename}>
              {document.filename} ({document.chunk_count} chunks)
            </li>
          ))}
        </ul>
      )}
    </div>  
  );
}

export default AdminPage;
