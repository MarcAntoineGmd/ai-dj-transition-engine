import { useState } from "react";

interface UploadResult {
  id: string;
  filename: string;
  duration: number;
  sample_rate: number;
}

export function AudioUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [result, setResult] = useState<UploadResult | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleUpload() {
    if (!file) return;

    setStatus("uploading");
    setErrorMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/audio/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail ?? "Erreur inconnue");
      }

      const data: UploadResult = await response.json();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Erreur réseau");
      setStatus("error");
    }
  }

  return (
    <div className="p-4 border rounded">
      <input
        type="file"
        accept=".mp3,.wav"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading"}
        className="ml-2 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {status === "uploading" ? "Envoi..." : "Upload"}
      </button>

      {status === "done" && result && (
        <pre className="mt-4 bg-gray-100 p-2 rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

      {status === "error" && (
        <p className="mt-4 text-red-600">{errorMessage}</p>
      )}
    </div>
  );
}