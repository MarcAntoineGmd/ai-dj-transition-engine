/**
 * Feature: Waveform audio player
 * Purpose: Display the waveform of a selected audio file and allow
 *          play/pause, using WaveSurfer.js.
 * Main files: src/components/WaveformPlayer.tsx
 * How it works: create a WaveSurfer instance pointed at a container div,
 *               load the audio from a local blob URL, expose a
 *               play/pause button.
 * Concepts learned: integrating a non-React library via useEffect and
 *                    refs, Blob URLs, cleaning up external library
 *                    instances to avoid memory leaks.
 */

import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";

interface WaveformPlayerProps {
  file: File;
}

export function WaveformPlayer({ file }: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "#9ca3af",
      progressColor: "#2563eb",
      height: 80,
    });

    const objectUrl = URL.createObjectURL(file);
    wavesurfer.load(objectUrl);

    wavesurfer.on("play", () => setIsPlaying(true));
    wavesurfer.on("pause", () => setIsPlaying(false));
    wavesurfer.on("finish", () => setIsPlaying(false));

    wavesurferRef.current = wavesurfer;

    return () => {
      wavesurfer.destroy();
      URL.revokeObjectURL(objectUrl);
    };
  }, [file]);

  function togglePlay() {
    wavesurferRef.current?.playPause();
  }

  return (
    <div className="mt-4">
      <div ref={containerRef} />
      <button
        onClick={togglePlay}
        className="mt-2 px-3 py-1 bg-gray-700 text-white rounded"
      >
        {isPlaying ? "Pause" : "Play"}
      </button>
    </div>
  );
}