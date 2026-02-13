"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
    AlertTriangle, Shield, Search, Zap, BarChart3,
    FileText, Vote, Users, ArrowUp, ArrowDown,
    Activity, Clock, ChevronRight, ExternalLink, Wallet
} from "lucide-react";

/* ================================================================
   NEURON BACKGROUND — Red-themed neural network on canvas
   ================================================================ */
function NeuronBackground() {
    const ref = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = ref.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animId: number;
        let w = (canvas.width = window.innerWidth);
        let h = (canvas.height = window.innerHeight);

        interface N {
            x: number; y: number;
            vx: number; vy: number;
            r: number; p: number; ps: number;
            c: string;
        }

        const palette = [
            "229, 57, 53", // Red
            "183, 28, 28", // Dark Red
            "220, 20, 60", // Crimson
            "255, 111, 97", // Light Red
        ];

        const nodes: N[] = [];
        const count = Math.min(60, Math.floor((w * h) / 22000));

        for (let i = 0; i < count; i++) {
            nodes.push({
                x: Math.random() * w,
                y: Math.random() * h,
                vx: (Math.random() - 0.5) * 0.25,
                vy: (Math.random() - 0.5) * 0.25,
                r: Math.random() * 2 + 0.8,
                p: Math.random() * Math.PI * 2,
                ps: Math.random() * 0.012 + 0.004,
                c: palette[Math.floor(Math.random() * palette.length)],
            });
        }

        const maxDist = 150;

        function draw() {
            ctx!.clearRect(0, 0, w, h);
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[i].x - nodes[j].x;
                    const dy = nodes[i].y - nodes[j].y;
                    const d = Math.sqrt(dx * dx + dy * dy);
                    if (d < maxDist) {
                        ctx!.beginPath();
                        ctx!.strokeStyle = `rgba(${nodes[i].c}, ${(1 - d / maxDist) * 0.07})`;
                        ctx!.lineWidth = 0.5;
                        ctx!.moveTo(nodes[i].x, nodes[i].y);
                        ctx!.lineTo(nodes[j].x, nodes[j].y);
                        ctx!.stroke();
                    }
                }
            }
            for (const n of nodes) {
                n.p += n.ps;
                const ps = Math.sin(n.p) * 0.5;
                const g = ctx!.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 5);
                g.addColorStop(0, `rgba(${n.c}, 0.25)`);
                g.addColorStop(1, `rgba(${n.c}, 0)`);
                ctx!.beginPath();
                ctx!.fillStyle = g;
                ctx!.arc(n.x, n.y, n.r * 5, 0, Math.PI * 2);
                ctx!.fill();
                ctx!.beginPath();
                ctx!.fillStyle = `rgba(${n.c}, 0.6)`;
                ctx!.arc(n.x, n.y, n.r + ps, 0, Math.PI * 2);
                ctx!.fill();
                n.x += n.vx; n.y += n.vy;
                if (n.x < 0 || n.x > w) n.vx *= -1;
                if (n.y < 0 || n.y > h) n.vy *= -1;
            }
            animId = requestAnimationFrame(draw);
        }
        draw();

        const onResize = () => { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; };
        window.addEventListener("resize", onResize);
        return () => { cancelAnimationFrame(animId); window.removeEventListener("resize", onResize); };
    }, []);

    return <canvas ref={ref} className="neuron-canvas" />;
}

/* ================================================================
   TYPES & MOCK DATA
   ================================================================ */
interface Agent {
    id: string;
    symbol: string;
    name: string;
    image_url?: string;
    trust_score: number;
    risk_status?: string;
    price_usd?: number;
    price_change_24h?: number;
    upvotes: number;
    downvotes: number;
}

interface AnalysisResult {
    agent_id: string;
    trust_score: number;
    trust_breakdown: {
        consistency: number;
        transparency: number;
        market_impact: number;
        recovery: number;
    };
    behavior_logs: string[];
    risk_alerts: { type: string; severity: string; message: string }[];
    risk_status: string;
    utility_score: number;
}

/* ================================================================
   MAIN COMPONENT
   ================================================================ */
export default function Home() {
    const [page, setPage] = useState<"dashboard" | "landing">("dashboard");
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
    const [profileData, setProfileData] = useState<AnalysisResult | null>(null);

    // Mock data for demonstration
    const mockProfileData: AnalysisResult = {
        agent_id: "0x8ba1f109551bD432803012645Ac136ddd64DBA72",
        trust_score: 87,
        trust_breakdown: {
            consistency: 62,
            transparency: 85,
            market_impact: 78,
            recovery: 90
        },
        behavior_logs: [
            "[13:45 UTC] agent executed trade • Market reaction: neutral • Volatility Impact: low • Trust delta: +0.3",
            "[13:45 UTC] agent executed trade • Market reaction: neutral • Volatility Impact: low • Trust delta: +0.3",
            "[13:45 UTC] agent execution completed successfully"
        ],
        risk_alerts: [
            { type: "optimization", severity: "medium", message: "Over-optimization detected" },
            { type: "drift", severity: "low", message: "Strategy drift" },
            { type: "trust", severity: "medium", message: "Public trust decay" }
        ],
        risk_status: "medium",
        utility_score: 72
    };

    // Mock listings data
    const mockListings: Agent[] = [
        { id: "0x8ba1f109551bD432803012645Ac136ddd64DBA72", symbol: "AGENT1", name: "AgentX", trust_score: 87, price_usd: 0.01465, price_change_24h: 5.2, upvotes: 156, downvotes: 23 },
        { id: "0xBaF6dC2E647aeb6F510f9e318856A1BCd66C5e19", symbol: "AGENT2", name: "AICore", trust_score: 82, price_usd: 0.02465, price_change_24h: -2.4, upvotes: 124, downvotes: 45 },
        { id: "0xab5801a7d398351b8be11c439e05c5b3259aec9b", symbol: "AGENT3", name: "BrainSync", trust_score: 79, price_usd: 0.03465, price_change_24h: 8.7, upvotes: 98, downvotes: 12 },
        { id: "0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b", symbol: "AGENT4", name: "NeuralX", trust_score: 91, price_usd: 0.04465, price_change_24h: -1.3, upvotes: 201, downvotes: 31 },
        { id: "0xA7EfAE728D2936e78BDA97dc267687568dD593f3", symbol: "AGENT5", name: "CogniFlow", trust_score: 76, price_usd: 0.05465, price_change_24h: 3.8, upvotes: 87, downvotes: 19 }
    ];

    useEffect(() => {
        // Initialize with mock data
        setProfileData(mockProfileData);
    }, []);

    // Simulate a scan/loading
    const handleScan = (id: string = input) => {
        if (!id.trim()) return;

        setLoading(true);
        setSelectedAgentId(id);

        setTimeout(() => {
            setProfileData(mockProfileData);
            setLoading(false);
        }, 2000);
    };

    return (
        <>
            <div className="grid-bg" />
            <NeuronBackground />
            <div className="ambient-glow" />
            <div className="ambient-glow-2" />
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="particle" />)}

            <div className="min-h-screen">
                {/* Header */}
                <header className="py-4 px-6 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <img src="/logo.png" alt="IQLAWD" width={36} height={36} className="rounded-full" />
                        <h1 className="text-xl font-bold">IQ<span className="text-red-500">LAWD</span></h1>
                        <div className="ml-2 text-xs bg-red-500/20 border border-red-500/40 text-red-400 px-2 py-0.5 rounded">LIVE</div>
                    </div>
                    <button className="bg-white/10 hover:bg-white/15 border border-white/20 text-white px-4 py-1.5 rounded-md flex items-center justify-center gap-2 text-sm">
                        <Wallet className="w-4 h-4" /> CONNECT WALLET
                    </button>
                </header>

                {/* Description */}
                <div className="px-6 py-3 text-gray-400 text-sm">
                    Agent Trust Intelligence — Evaluates AI agents beyond performance metrics: trust, intent alignment, and real-world utility on-chain.
                </div>

                {/* Search Bar */}
                <div className="px-6 py-2">
                    <div className="flex rounded-md overflow-hidden w-full max-w-3xl">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleScan()}
                                placeholder="Enter agent address or token contract (0x...)"
                                className="w-full pl-10 pr-4 py-3 bg-black/40 border border-red-900/30 text-gray-200"
                            />
                        </div>
                        <button
                            onClick={() => handleScan()}
                            disabled={loading || !input.trim()}
                            className="bg-red-600 hover:bg-red-700 text-white px-6 flex items-center gap-2 font-bold transition-colors"
                        >
                            SCAN AGENT <Zap className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Main Dashboard Grid */}
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
                    {/* TRUST SCORE */}
                    <div className="glass-card" style={{ gridRow: "span 2" }}>
                        <h2 className="section-title"><span>01</span> — Trust Score</h2>
                        <div className="orb-container">
                            <div className="relative">
                                <div className="pulse-ring"></div>
                                <div className="pulse-ring"></div>
                                <div className="trust-orb">
                                    <div className="orb-score">
                                        <div className="orb-label">Trust Score</div>
                                        <div className="orb-number">87</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="space-y-1 mt-4">
                            <div className="metric-row">
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm text-gray-400">Consistency Index</span>
                                    <span className="text-sm text-gray-300">62%</span>
                                </div>
                                <div className="h-1.5 bg-red-900/20 rounded-full overflow-hidden">
                                    <div className="h-full bg-red-600" style={{ width: "62%" }}></div>
                                </div>
                            </div>

                            <div className="metric-row">
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm text-gray-400">Decision Transparency</span>
                                    <span className="text-sm text-gray-300">85%</span>
                                </div>
                                <div className="h-1.5 bg-red-900/20 rounded-full overflow-hidden">
                                    <div className="h-full bg-red-600" style={{ width: "85%" }}></div>
                                </div>
                            </div>

                            <div className="metric-row">
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm text-gray-400">Market Impact</span>
                                    <span className="text-sm text-gray-300">78%</span>
                                </div>
                                <div className="h-1.5 bg-red-900/20 rounded-full overflow-hidden">
                                    <div className="h-full bg-red-600" style={{ width: "78%" }}></div>
                                </div>
                            </div>

                            <div className="metric-row">
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm text-gray-400">Failure Recovery</span>
                                    <span className="text-sm text-gray-300">90%</span>
                                </div>
                                <div className="h-1.5 bg-red-900/20 rounded-full overflow-hidden">
                                    <div className="h-full bg-red-600" style={{ width: "90%" }}></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* BEHAVIOR TRACE */}
                    <div className="glass-card">
                        <h2 className="section-title"><span>02</span> — Behavior Trace</h2>
                        <div className="terminal">
                            {profileData?.behavior_logs?.map((log, i) => (
                                <div key={i} className="terminal-line">{log}</div>
                            ))}
                        </div>
                    </div>

                    {/* UTILITY SCORE */}
                    <div className="glass-card">
                        <h2 className="section-title"><span>03</span> — Utility Score</h2>
                        <div className="flex items-end justify-between h-44 px-4 pt-6">
                            {[
                                { label: "F2", value: 82, class: "bg-red-600" },
                                { label: "DC", value: 65, class: "bg-red-600" },
                                { label: "PP", value: 75, class: "bg-red-600" },
                                { label: "LC", value: 45, class: "bg-red-600" }
                            ].map((bar, i) => (
                                <div key={i} className="flex flex-col items-center w-16">
                                    <div className="h-40 w-full relative">
                                        <div
                                            className={`absolute bottom-0 w-full ${bar.class} opacity-80`}
                                            style={{ height: `${bar.value}%` }}
                                        ></div>
                                    </div>
                                    <div className="text-xs text-center text-gray-500 mt-2">{bar.label}</div>
                                    <div className="text-xs text-gray-300">{bar.value}%</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* RISK & ALERTS */}
                    <div className="glass-card">
                        <h2 className="section-title"><span>04</span> — Risk & Alerts</h2>
                        <div className="space-y-4">
                            {profileData?.risk_alerts?.map((alert, i) => (
                                <div key={i} className="flex items-center gap-3 p-3 bg-red-900/10 rounded-md border border-red-900/20">
                                    <AlertTriangle className="text-red-500 w-5 h-5 flex-shrink-0" />
                                    <div className="text-sm text-gray-300">{alert.message}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* ETHOS-STYLE LEADERBOARD */}
                <div className="mx-6 mb-8 bg-black/30 border border-red-900/20 rounded-md overflow-hidden">
                    <div className="bg-gradient-to-r from-red-900/30 to-black/30 p-4 border-b border-red-900/20">
                        <div className="text-white font-semibold">LIVE AGENT RANKINGS</div>
                    </div>

                    <div>
                        <div className="grid grid-cols-8 p-3 bg-black/50 text-gray-400 text-sm">
                            <div>Rank</div>
                            <div className="col-span-2">Agent</div>
                            <div>Trust Score</div>
                            <div>Utility</div>
                            <div>Price</div>
                            <div>24h</div>
                            <div>Actions</div>
                        </div>

                        {mockListings.map((agent, index) => (
                            <div key={agent.id} className="grid grid-cols-8 p-3 border-b border-red-900/10 hover:bg-red-900/5 cursor-pointer">
                                <div className="flex items-center text-gray-500">#{index + 1}</div>
                                <div className="col-span-2 flex items-center gap-2">
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-600 to-red-800"></div>
                                    <div>
                                        <div className="text-white text-sm">{agent.name}</div>
                                        <div className="text-gray-500 text-xs">{agent.symbol}</div>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <div className="bg-gradient-to-r from-red-600 to-red-800 text-white rounded-md px-2 py-1 text-xs">
                                        {agent.trust_score}
                                    </div>
                                </div>
                                <div className="flex items-center gap-1">
                                    {[1, 2, 3].map(i => (
                                        <div
                                            key={i}
                                            className={`h-1 w-4 rounded-full ${i <= (agent.trust_score / 33) ? 'bg-red-500' : 'bg-gray-700'}`}
                                        ></div>
                                    ))}
                                </div>
                                <div className="flex items-center text-gray-300">${agent.price_usd?.toFixed(6)}</div>
                                <div className="flex items-center">
                                    <span className={agent.price_change_24h! >= 0 ? "text-green-500" : "text-red-500"}>
                                        {agent.price_change_24h! >= 0 ? "+" : ""}{agent.price_change_24h?.toFixed(2)}%
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button className="p-1 bg-green-900/20 rounded border border-green-900/30 text-green-500">
                                        <ArrowUp className="w-3 h-3" />
                                    </button>
                                    <button className="p-1 bg-red-900/20 rounded border border-red-900/30 text-red-500">
                                        <ArrowDown className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Loading Overlay */}
                {loading && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
                        <div className="bg-black border border-red-500/20 p-6 rounded-xl flex flex-col items-center gap-4">
                            <div className="loading-dots"><span /><span /><span /></div>
                            <p className="text-red-500 font-mono text-sm animate-pulse">ANALYZING AGENT...</p>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}