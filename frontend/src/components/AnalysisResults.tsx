/**
 * Feature: Analysis results display
 * Purpose: Present the full analysis of an uploaded song (waveform with
 *          beat markers, BPM/key/energy summary, energy curve) as one
 *          organized block.
 * Main files: src/components/AnalysisResults.tsx
 * How it works: receives the selected file and its analysis result as
 *               props, lays out WaveformPlayer, a summary block, and
 *               EnergyChart.
 * Concepts learned: separating presentation components from the
 *                    component that owns data-fetching logic.
 */

import { WaveformPlayer } from "./WaveformPlayer";
import { EnergyChart } from "./EnergyChart";

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

interface AnalysisResultsProps {
  file: File;
  analysis: AnalysisResult;
}

export function AnalysisResults({ file, analysis }: AnalysisResultsProps) {
  const averageEnergy =
    analysis.energy.length > 0
      ? analysis.energy.reduce((sum, v) => sum + v, 0) / analysis.energy.length
      : 0;

  return (
    <div className="mt-6">
      <section>
        <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
          Forme d'onde
        </h2>
        <WaveformPlayer file={file} beatTimes={analysis.beat_times} />
      </section>

      <section className="mt-6">
        <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
          Résumé
        </h2>
        <div className="p-3 bg-gray-100 rounded">
          <p>BPM : {analysis.bpm.toFixed(2)}</p>
          <p>Clé : {analysis.key}</p>
          <p>Énergie moyenne : {averageEnergy.toFixed(4)}</p>
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
          Énergie dans le temps
        </h2>
        <EnergyChart energy={analysis.energy} />
      </section>
    </div>
  );
}