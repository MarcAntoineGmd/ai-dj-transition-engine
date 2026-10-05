/**
 * Feature: Energy curve chart
 * Purpose: Display the RMS energy values over time as a simple line
 *          chart, using raw SVG (no charting library needed for a
 *          single static curve).
 * Main files: src/components/EnergyChart.tsx
 * How it works: normalize the energy array to fit a fixed SVG viewbox,
 *               build a polyline from the normalized points.
 * Concepts learned: manual data normalization for visualization,
 *                    SVG polyline coordinates, viewBox scaling.
 */

interface EnergyChartProps {
  energy: number[];
}

const WIDTH = 800;
const HEIGHT = 100;

export function EnergyChart({ energy }: EnergyChartProps) {
  if (energy.length === 0) return null;

  const maxEnergy = Math.max(...energy);

  const points = energy
    .map((value, index) => {
      const x = (index / (energy.length - 1)) * WIDTH;
      const y = HEIGHT - (value / maxEnergy) * HEIGHT;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="mt-4">
      <p className="text-sm text-gray-500 mb-1">Énergie (RMS)</p>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        width="100%"
        height={HEIGHT}
        preserveAspectRatio="none"
      >
        <polyline
          points={points}
          fill="none"
          stroke="#2563eb"
          strokeWidth={1.5}
        />
      </svg>
    </div>
  );
}