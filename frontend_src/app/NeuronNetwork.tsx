"use client";

import React, { useRef, useMemo, useCallback } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { EffectComposer, Bloom } from "@react-three/postprocessing";

/* ================================================================
   CONFIGURATION
   ================================================================ */
const CONFIG = {
    NODE_COUNT: 500,
    SPREAD: 12,
    CONNECTION_DIST: 2.8,
    PULSE_COUNT: 40,
    PULSE_SPEED: 0.012,
    MOUSE_INFLUENCE: 3.0,
    MOUSE_RADIUS: 4.0,
    DRIFT_SPEED: 0.15,
    ROTATION_SPEED: 0.008,
};

/* ================================================================
   CUSTOM SHADERS — GLOWING NEURON NODES
   ================================================================ */
const neuronVertexShader = `
    attribute float aSize;
    attribute float aPhase;
    attribute float aSpeed;
    varying float vAlpha;
    varying float vSize;
    uniform float uTime;
    uniform vec3 uMouse;
    uniform float uMouseInfluence;

    void main() {
        vec3 pos = position;

        // Organic drift — each node has unique movement
        float drift = sin(uTime * aSpeed + aPhase) * 0.15;
        float drift2 = cos(uTime * aSpeed * 0.7 + aPhase * 1.3) * 0.12;
        float drift3 = sin(uTime * aSpeed * 0.5 + aPhase * 0.8) * 0.1;
        pos.x += drift;
        pos.y += drift2;
        pos.z += drift3;

        // Mouse reactivity — glow brighter near cursor
        float mouseDist = distance(pos, uMouse);
        float mouseEffect = smoothstep(4.0, 0.5, mouseDist) * uMouseInfluence;

        // Size pulse
        float sizePulse = 1.0 + sin(uTime * 2.0 + aPhase) * 0.3;
        float finalSize = aSize * sizePulse * (1.0 + mouseEffect * 2.0);

        vAlpha = 0.4 + mouseEffect * 0.6 + sin(uTime * 1.5 + aPhase) * 0.15;
        vSize = finalSize;

        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = finalSize * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
    }
`;

const neuronFragmentShader = `
    varying float vAlpha;
    varying float vSize;
    uniform vec3 uColor1;
    uniform vec3 uColor2;
    uniform float uTime;

    void main() {
        float dist = length(gl_PointCoord - vec2(0.5));
        if (dist > 0.5) discard;

        // Soft radial gradient — glowing sphere effect
        float glow = 1.0 - smoothstep(0.0, 0.5, dist);
        float core = 1.0 - smoothstep(0.0, 0.15, dist);

        // Mix between two red tones
        vec3 color = mix(uColor1, uColor2, core);

        // Add bright white core for hub neurons (bigger ones)
        if (vSize > 6.0) {
            color = mix(color, vec3(1.0, 0.85, 0.8), core * 0.7);
        }

        float alpha = glow * vAlpha;
        gl_FragColor = vec4(color, alpha);
    }
`;

/* ================================================================
   CUSTOM SHADERS — SYNAPSE CONNECTION LINES
   ================================================================ */
const synapseVertexShader = `
    attribute float aOpacity;
    varying float vOpacity;
    uniform float uTime;

    void main() {
        vOpacity = aOpacity;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
`;

const synapseFragmentShader = `
    varying float vOpacity;
    uniform vec3 uColor;

    void main() {
        gl_FragColor = vec4(uColor, vOpacity * 0.35);
    }
`;

/* ================================================================
   SIGNAL PULSE SHADERS
   ================================================================ */
const pulseVertexShader = `
    attribute float aPulseSize;
    attribute float aPulseAlpha;
    varying float vPulseAlpha;

    void main() {
        vPulseAlpha = aPulseAlpha;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = aPulseSize * (250.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
    }
`;

const pulseFragmentShader = `
    varying float vPulseAlpha;

    void main() {
        float dist = length(gl_PointCoord - vec2(0.5));
        if (dist > 0.5) discard;
        float glow = 1.0 - smoothstep(0.0, 0.5, dist);
        float core = 1.0 - smoothstep(0.0, 0.12, dist);
        vec3 color = mix(vec3(0.9, 0.2, 0.15), vec3(1.0, 0.95, 0.9), core);
        gl_FragColor = vec4(color, glow * vPulseAlpha);
    }
`;

/* ================================================================
   NEURON FIELD — Main 3D scene with nodes + synapses + pulses
   ================================================================ */
function NeuronField() {
    const { mouse, viewport } = useThree();

    // Refs
    const nodesRef = useRef<THREE.Points>(null);
    const synapsesRef = useRef<THREE.LineSegments>(null);
    const pulsesRef = useRef<THREE.Points>(null);
    const groupRef = useRef<THREE.Group>(null);
    const mouseWorld = useRef(new THREE.Vector3(0, 0, 0));

    // Generate neuron positions + attributes
    const { positions, sizes, phases, speeds } = useMemo(() => {
        const count = CONFIG.NODE_COUNT;
        const positions = new Float32Array(count * 3);
        const sizes = new Float32Array(count);
        const phases = new Float32Array(count);
        const speeds = new Float32Array(count);

        for (let i = 0; i < count; i++) {
            // Clustered distribution — more organic than uniform random
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            const r = Math.pow(Math.random(), 0.6) * CONFIG.SPREAD;

            positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            positions[i * 3 + 2] = r * Math.cos(phi);

            // Varying sizes — some hub neurons are larger
            const isHub = Math.random() < 0.08;
            sizes[i] = isHub ? 4.0 + Math.random() * 4.0 : 1.0 + Math.random() * 2.5;
            phases[i] = Math.random() * Math.PI * 2;
            speeds[i] = 0.2 + Math.random() * 0.8;
        }
        return { positions, sizes, phases, speeds };
    }, []);

    // Synapse geometry (pre-allocated, updated each frame)
    const maxConnections = 3000;
    const synapsePositions = useMemo(() => new Float32Array(maxConnections * 6), []);
    const synapseOpacities = useMemo(() => new Float32Array(maxConnections * 2), []);

    // Pulse data
    const pulseData = useMemo(() => {
        const count = CONFIG.PULSE_COUNT;
        const pos = new Float32Array(count * 3);
        const pulseSizes = new Float32Array(count);
        const pulseAlphas = new Float32Array(count);
        const meta: Array<{
            fromIdx: number; toIdx: number;
            progress: number; speed: number; active: boolean;
        }> = [];

        for (let i = 0; i < count; i++) {
            pulseSizes[i] = 3.0 + Math.random() * 3.0;
            pulseAlphas[i] = 0;
            meta.push({
                fromIdx: 0, toIdx: 0,
                progress: 0, speed: CONFIG.PULSE_SPEED + Math.random() * 0.008,
                active: false
            });
        }
        return { pos, pulseSizes, pulseAlphas, meta };
    }, []);

    // Shader uniforms
    const nodeUniforms = useMemo(() => ({
        uTime: { value: 0 },
        uColor1: { value: new THREE.Color(0.85, 0.12, 0.1) },   // Deep crimson
        uColor2: { value: new THREE.Color(1.0, 0.25, 0.15) },    // Bright red
        uMouse: { value: new THREE.Vector3(0, 0, 0) },
        uMouseInfluence: { value: CONFIG.MOUSE_INFLUENCE },
    }), []);

    const synapseUniforms = useMemo(() => ({
        uTime: { value: 0 },
        uColor: { value: new THREE.Color(0.7, 0.1, 0.08) },
    }), []);

    // Find connections between nearby neurons
    const findConnections = useCallback((currentPositions: Float32Array, time: number) => {
        let connIdx = 0;
        const maxDist = CONFIG.CONNECTION_DIST;
        const maxDistSq = maxDist * maxDist;
        const n = CONFIG.NODE_COUNT;

        // Only check subset for performance
        const step = Math.max(1, Math.floor(n / 200));

        for (let i = 0; i < n && connIdx < maxConnections; i += step) {
            const ix = currentPositions[i * 3];
            const iy = currentPositions[i * 3 + 1];
            const iz = currentPositions[i * 3 + 2];

            for (let j = i + 1; j < n && connIdx < maxConnections; j++) {
                const dx = ix - currentPositions[j * 3];
                const dy = iy - currentPositions[j * 3 + 1];
                const dz = iz - currentPositions[j * 3 + 2];
                const distSq = dx * dx + dy * dy + dz * dz;

                if (distSq < maxDistSq) {
                    const dist = Math.sqrt(distSq);
                    const opacity = 1.0 - dist / maxDist;

                    const ci = connIdx * 6;
                    synapsePositions[ci] = ix;
                    synapsePositions[ci + 1] = iy;
                    synapsePositions[ci + 2] = iz;
                    synapsePositions[ci + 3] = currentPositions[j * 3];
                    synapsePositions[ci + 4] = currentPositions[j * 3 + 1];
                    synapsePositions[ci + 5] = currentPositions[j * 3 + 2];

                    const oi = connIdx * 2;
                    synapseOpacities[oi] = opacity;
                    synapseOpacities[oi + 1] = opacity;

                    connIdx++;
                }
            }
        }
        return connIdx;
    }, [synapsePositions, synapseOpacities]);

    // Animation loop
    useFrame((state) => {
        const time = state.clock.getElapsedTime();

        // Update mouse world position
        mouseWorld.current.set(
            (mouse.x * viewport.width) / 2,
            (mouse.y * viewport.height) / 2,
            0
        );

        // Update node uniforms
        nodeUniforms.uTime.value = time;
        nodeUniforms.uMouse.value.copy(mouseWorld.current);
        synapseUniforms.uTime.value = time;

        // Slow rotation
        if (groupRef.current) {
            groupRef.current.rotation.y = time * CONFIG.ROTATION_SPEED;
            groupRef.current.rotation.x = Math.sin(time * 0.05) * 0.1;
        }

        // Calculate current node positions (after drift)
        const currentPositions = new Float32Array(CONFIG.NODE_COUNT * 3);
        for (let i = 0; i < CONFIG.NODE_COUNT; i++) {
            const phase = phases[i];
            const speed = speeds[i];
            currentPositions[i * 3] = positions[i * 3] + Math.sin(time * speed + phase) * 0.15;
            currentPositions[i * 3 + 1] = positions[i * 3 + 1] + Math.cos(time * speed * 0.7 + phase * 1.3) * 0.12;
            currentPositions[i * 3 + 2] = positions[i * 3 + 2] + Math.sin(time * speed * 0.5 + phase * 0.8) * 0.1;
        }

        // Update synapses
        const connCount = findConnections(currentPositions, time);
        if (synapsesRef.current) {
            const geom = synapsesRef.current.geometry;
            geom.setAttribute("position", new THREE.BufferAttribute(synapsePositions, 3));
            geom.setAttribute("aOpacity", new THREE.BufferAttribute(synapseOpacities, 1));
            geom.setDrawRange(0, connCount * 2);
            geom.attributes.position.needsUpdate = true;
            geom.attributes.aOpacity.needsUpdate = true;
        }

        // Update signal pulses
        if (pulsesRef.current) {
            for (let p = 0; p < CONFIG.PULSE_COUNT; p++) {
                const meta = pulseData.meta[p];

                if (!meta.active) {
                    // Randomly activate pulse
                    if (Math.random() < 0.02) {
                        meta.fromIdx = Math.floor(Math.random() * CONFIG.NODE_COUNT);
                        // Find a nearby neighbor
                        let bestDist = Infinity;
                        let bestIdx = -1;
                        for (let j = 0; j < CONFIG.NODE_COUNT; j++) {
                            if (j === meta.fromIdx) continue;
                            const dx = currentPositions[meta.fromIdx * 3] - currentPositions[j * 3];
                            const dy = currentPositions[meta.fromIdx * 3 + 1] - currentPositions[j * 3 + 1];
                            const dz = currentPositions[meta.fromIdx * 3 + 2] - currentPositions[j * 3 + 2];
                            const d = dx * dx + dy * dy + dz * dz;
                            if (d < bestDist && d < CONFIG.CONNECTION_DIST * CONFIG.CONNECTION_DIST) {
                                bestDist = d;
                                bestIdx = j;
                            }
                        }
                        if (bestIdx >= 0) {
                            meta.toIdx = bestIdx;
                            meta.progress = 0;
                            meta.active = true;
                        }
                    }
                }

                if (meta.active) {
                    meta.progress += meta.speed;
                    if (meta.progress >= 1.0) {
                        meta.active = false;
                        pulseData.pulseAlphas[p] = 0;
                    } else {
                        const t = meta.progress;
                        const fi = meta.fromIdx * 3;
                        const ti = meta.toIdx * 3;
                        pulseData.pos[p * 3] = currentPositions[fi] + (currentPositions[ti] - currentPositions[fi]) * t;
                        pulseData.pos[p * 3 + 1] = currentPositions[fi + 1] + (currentPositions[ti + 1] - currentPositions[fi + 1]) * t;
                        pulseData.pos[p * 3 + 2] = currentPositions[fi + 2] + (currentPositions[ti + 2] - currentPositions[fi + 2]) * t;

                        // Fade in/out
                        const fadeIn = Math.min(t * 5, 1.0);
                        const fadeOut = Math.min((1 - t) * 5, 1.0);
                        pulseData.pulseAlphas[p] = fadeIn * fadeOut * 0.9;
                    }
                }
            }

            const pg = pulsesRef.current.geometry;
            pg.setAttribute("position", new THREE.BufferAttribute(pulseData.pos, 3));
            pg.setAttribute("aPulseAlpha", new THREE.BufferAttribute(pulseData.pulseAlphas, 1));
            pg.attributes.position.needsUpdate = true;
            pg.attributes.aPulseAlpha.needsUpdate = true;
        }
    });

    return (
        <group ref={groupRef}>
            {/* NEURON NODES */}
            <points ref={nodesRef} frustumCulled={false}>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[positions, 3]} />
                    <bufferAttribute attach="attributes-aSize" args={[sizes, 1]} />
                    <bufferAttribute attach="attributes-aPhase" args={[phases, 1]} />
                    <bufferAttribute attach="attributes-aSpeed" args={[speeds, 1]} />
                </bufferGeometry>
                <shaderMaterial
                    vertexShader={neuronVertexShader}
                    fragmentShader={neuronFragmentShader}
                    uniforms={nodeUniforms}
                    transparent
                    depthWrite={false}
                    blending={THREE.AdditiveBlending}
                />
            </points>

            {/* SYNAPSE CONNECTIONS */}
            <lineSegments ref={synapsesRef} frustumCulled={false}>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[synapsePositions, 3]} />
                    <bufferAttribute attach="attributes-aOpacity" args={[synapseOpacities, 1]} />
                </bufferGeometry>
                <shaderMaterial
                    vertexShader={synapseVertexShader}
                    fragmentShader={synapseFragmentShader}
                    uniforms={synapseUniforms}
                    transparent
                    depthWrite={false}
                    blending={THREE.AdditiveBlending}
                />
            </lineSegments>

            {/* SIGNAL PULSES */}
            <points ref={pulsesRef} frustumCulled={false}>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[pulseData.pos, 3]} />
                    <bufferAttribute attach="attributes-aPulseSize" args={[pulseData.pulseSizes, 1]} />
                    <bufferAttribute attach="attributes-aPulseAlpha" args={[pulseData.pulseAlphas, 1]} />
                </bufferGeometry>
                <shaderMaterial
                    vertexShader={pulseVertexShader}
                    fragmentShader={pulseFragmentShader}
                    transparent
                    depthWrite={false}
                    blending={THREE.AdditiveBlending}
                />
            </points>
        </group>
    );
}

/* ================================================================
   MAIN EXPORT — Canvas with Bloom Post-Processing
   ================================================================ */
export default function NeuronNetwork() {
    return (
        <div className="fixed inset-0 z-[-9999] pointer-events-none select-none" style={{ opacity: 0.5 }}>
            <Canvas
                style={{ pointerEvents: 'none' }}
                camera={{ position: [0, 0, 8], fov: 75, near: 0.1, far: 100 }}
                dpr={[1, 1.5]}
                gl={{
                    antialias: false,
                    alpha: true,
                    powerPreference: "high-performance",
                }}
            >
                <color attach="background" args={["#000000"]} />
                <NeuronField />
                <EffectComposer>
                    <Bloom
                        intensity={1.2}
                        luminanceThreshold={0.2}
                        luminanceSmoothing={0.9}
                        mipmapBlur
                    />
                </EffectComposer>
            </Canvas>
        </div>
    );
}
