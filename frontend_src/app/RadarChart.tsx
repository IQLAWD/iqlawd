import React from 'react';
import { motion } from 'framer-motion';

// Accept size prop or default to responsive behavior
interface RadarChartProps {
    data: {
        label: string;
        value: number; // 0-100
        fullMark: number;
    }[];
    color?: string;
    size?: number;
}

export default function RadarChart({ data, color = '#ef4444', size = 200 }: RadarChartProps) {
    // If size is provided, use it. Otherwise we might need a wrapper ref for true responsiveness, 
    // but for now letting the parent control size via prop is safest.
    const center = size / 2;
    const radius = (size / 2) - 40; // Padding for labels
    const angleStep = (Math.PI * 2) / data.length;

    // Helper to calculate points
    const getPoint = (index: number, value: number) => {
        const angle = index * angleStep - Math.PI / 2; // Start at top
        const r = (value / 100) * radius;
        const x = center + r * Math.cos(angle);
        const y = center + r * Math.sin(angle);
        return { x, y };
    };

    // Calculate polygon points for the data
    const pointsString = data.map((d, i) => {
        const { x, y } = getPoint(i, d.value);
        return `${x},${y}`;
    }).join(' ');

    // Calculate background webs (25%, 50%, 75%, 100%)
    const webs = [25, 50, 75, 100].map(level => {
        return data.map((_, i) => {
            const { x, y } = getPoint(i, level);
            return `${x},${y}`;
        }).join(' ');
    });

    return (
        <div className="relative flex items-center justify-center w-full h-full aspect-square max-w-[200px] md:max-w-[240px]">
            <svg viewBox={`0 0 ${size} ${size}`} className="overflow-visible w-full h-full">
                {/* Background Web */}
                {webs.map((points, i) => (
                    <polygon
                        key={i}
                        points={points}
                        fill="none"
                        stroke="rgba(255, 255, 255, 0.1)"
                        strokeWidth="1"
                        strokeDasharray={i === 3 ? "0" : "4 2"}
                    />
                ))}

                {/* Axes */}
                {data.map((_, i) => {
                    const { x, y } = getPoint(i, 100);
                    return (
                        <line
                            key={i}
                            x1={center}
                            y1={center}
                            x2={x}
                            y2={y}
                            stroke="rgba(255, 255, 255, 0.1)"
                            strokeWidth="1"
                        />
                    );
                })}

                {/* Data Polygon */}
                <motion.polygon
                    points={pointsString}
                    fill={color}
                    fillOpacity="0.2"
                    stroke={color}
                    strokeWidth="2"
                    initial={{ scale: 0, opacity: 0, originX: "50%", originY: "50%" }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                />

                {/* Data Points */}
                {data.map((d, i) => {
                    const { x, y } = getPoint(i, d.value);
                    return (
                        <motion.circle
                            key={i}
                            cx={x}
                            cy={y}
                            r="3"
                            fill={color}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.5 + i * 0.1 }}
                        />
                    );
                })}

                {/* Labels */}
                {data.map((d, i) => {
                    const { x, y } = getPoint(i, 115); // Push labels out a bit
                    return (
                        <text
                            key={i}
                            x={x}
                            y={y}
                            textAnchor="middle"
                            dominantBaseline="middle"
                            fill="#a1a1aa"
                            className="text-[10px] uppercase font-bold tracking-wider"
                            style={{ fontSize: 8 }}
                        >
                            {d.label}
                        </text>
                    );
                })}
            </svg>

            {/* Center Glow */}
            <div className="absolute inset-0 bg-red-500/10 blur-3xl rounded-full -z-10" />
        </div>
    );
}
