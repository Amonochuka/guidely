import { useState } from "react";
import api from "../services/api";

function UploadForm() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please choose a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.post("/documents/upload", formData);

      setMessage(response.data.message);
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Upload failed."
      );
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => setSelectedFile(e.target.files[0])}
      />

      <br />
      <br />

      <button onClick={handleUpload}>
        Upload
      </button>

      <p>{message}</p>
    </div>
  );
}

export default UploadForm;