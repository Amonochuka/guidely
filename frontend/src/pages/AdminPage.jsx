import { useState } from "react";
import { uploadDocument } from "../api/api";

function AdminPage() {
  const [file, setFile] = useState(null);

  async function handleUpload() {
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await uploadDocument(formData);
      alert("Document uploaded successfully!");
    } catch (error) {
      console.error("Error uploading document:", error);
      alert("Failed to upload document.");
    }
  }

  return (
    <div>
      <h1>Upload Documents</h1>

      <input
        type="file"
        onChange={(event) => setFile(event.target.files[0])}
      />

      <button onClick={handleUpload}>
        Upload
      </button>
    </div>
  );
}

export default AdminPage;