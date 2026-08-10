import { useRef, useState } from "react";
import { uploadDocument } from "../api/api";

function AdminPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const fileInputRef = useRef(null);

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

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      
    } catch (error) {
      console.error("Error uploading document:", error);
      setMessage("Failed to upload document.");
    }
    finally {
      setUploading(false);
    }
  }

  return (
    <div className="container">
      <h1>Upload Documents</h1>

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
    </div>  
  );
}

export default AdminPage;