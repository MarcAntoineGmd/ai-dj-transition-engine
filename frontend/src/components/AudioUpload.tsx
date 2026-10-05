/**
 * Feature: Audio upload and analysis UI
 * Purpose: Let the user pick an audio file, upload it, then automatically
 *          trigger analysis and display BPM, key and average energy.
 * Main files: src/components/AudioUpload.tsx
 * How it works: file input -> upload via FormData/fetch -> on success,
 *               call /analyze/{id} -> display both results or errors.
 * Concepts learned: chaining two dependent async requests, FormData for
 *                    multipart uploads, multi-value React state,
 *                    propagating backend HTTP errors to the UI.
 */

import { useState } from "react";
import { WaveformPlayer } from "./WaveformPlayer";

interface UploadResult {
  id: string;
  filename: string;
  duration: number;
  sample_rate: number;
}

interface SpectralFeatures {
  spectral_centroid_mean: number;
  spectral_bandwidth_mean: number;
  chroma_mean: number[];
  mfcc_mean: number[];
}

interface AnalysisResult {
  id: string;
  bpm: number;
  key: string;
  beat_times: number[];
  energy: number[];
  spectral_features: SpectralFeatures;
}

type Status = "idle" | "uploading" | "analyzing" | "done" | "error";

export function AudioUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleUpload() {
    if (!file) return;

    setStatus("uploading");
    setErrorMessage("");
    setAnalysis(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadResponse = await fetch("http://localhost:8000/api/audio/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.detail ?? "Erreur d'upload");
      }

      const uploadData: UploadResult = await uploadResponse.json();
      setUploadResult(uploadData);
      setStatus("analyzing");

      const analyzeResponse = await fetch(
        `http://localhost:8000/api/audio/analyze/${uploadData.id}`,
        { method: "POST" }
      );

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json();
        throw new Error(errorData.detail ?? "Erreur d'analyse");
      }

      const analysisData: AnalysisResult = await analyzeResponse.json();
      setAnalysis(analysisData);
      setStatus("done");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Erreur réseau");
      setStatus("error");
    }
  }

  const averageEnergy =
    analysis && analysis.energy.length > 0
      ? analysis.energy.reduce((sum, v) => sum + v, 0) / analysis.energy.length
      : null;

  return (
    <div className="p-4 border rounded">
      <input
        type="file"
        accept=".mp3,.wav"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading" || status === "analyzing"}
        className="ml-2 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {status === "uploading" && "Envoi..."}
        {status === "analyzing" && "Analyse..."}
        {(status === "idle" || status === "done" || status === "error") && "Upload"}
      </button>

      {uploadResult && (
        <p className="mt-4 text-sm text-gray-600">
          {uploadResult.filename} — {uploadResult.duration.toFixed(1)}s
        </p>
      )}

      {file && <WaveformPlayer file={file} beatTimes={analysis?.beat_times} />}

      {status === "done" && analysis && (
        <div className="mt-4 p-3 bg-gray-100 rounded">
          <p>BPM : {analysis.bpm.toFixed(2)}</p>
          <p>Clé : {analysis.key}</p>
          <p>Énergie moyenne : {averageEnergy?.toFixed(4)}</p>
        </div>
      )}

      {status === "error" && (
        <p className="mt-4 text-red-600">{errorMessage}</p>
      )}
    </div>
  );
}