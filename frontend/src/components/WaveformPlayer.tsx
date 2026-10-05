/**
 * Feature: Waveform audio player with beat markers
 * Purpose: Display the waveform of a selected audio file, allow
 *          play/pause, and overlay vertical markers at each detected
 *          beat position.
 * Main files: src/components/WaveformPlayer.tsx
 * How it works: create a WaveSurfer instance with the Regions plugin,
 *               load audio from a local blob URL, and once ready, add
 *               one zero-width region per beat timestamp.
 * Concepts learned: WaveSurfer plugins (Regions), waiting for the
 *                    "ready" event before adding time-based overlays.
 */

import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import RegionsPlugin from "wavesurfer.js/dist/plugins/regions.esm.js";

interface WaveformPlayerProps {
  file: File;
  beatTimes?: number[];
}

export function WaveformPlayer({ file, beatTimes }: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const regions = RegionsPlugin.create();

    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "#9ca3af",
      progressColor: "#2563eb",
      height: 80,
      plugins: [regions],
    });

    const objectUrl = URL.createObjectURL(file);
    wavesurfer.load(objectUrl);

    wavesurfer.on("play", () => setIsPlaying(true));
    wavesurfer.on("pause", () => setIsPlaying(false));
    wavesurfer.on("finish", () => setIsPlaying(false));

    wavesurfer.on("ready", () => {
      if (!beatTimes) return;
      for (const time of beatTimes) {
        regions.addRegion({
          start: time,
          end: time,
          color: "rgba(239, 68, 68, 0.6)",
          drag: false,
          resize: false,
        });
      }
    });

    wavesurferRef.current = wavesurfer;

    return () => {
      wavesurfer.destroy();
      URL.revokeObjectURL(objectUrl);
    };
  }, [file, beatTimes]);

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