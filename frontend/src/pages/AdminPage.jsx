import { useState } from "react";
import { uploadDocument } from "../api/api";

function AdminPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

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
      await uploadDocument(formData);
      setMessage("Document uploaded successfully!");
    } catch (error) {
      console.error("Error uploading document:", error);
      setMessage("Failed to upload document.");
    }
    finally{
      setUploading(false);
    }
  }

  return (
    <div>
      <h1>Upload Documents</h1>

      <input
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
    </div>  
  );
}

export default AdminPage;