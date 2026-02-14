
import React, { useRef, useState } from 'react';
import { Shield, Zap, Users, MessageSquare, Download, Share2, CheckCircle } from 'lucide-react';
import html2canvas from 'html2canvas';

interface IdentityCardProps {
    agent: {
        display_name: string;
        username: string;
        avatar_url: string;
        x_avatar?: string;
        x_handle?: string;
        trust_score: number;
        karma: number;
        followers: number;
        post_count: number;
        faction?: string;
    };
}

export default function IdentityCard({ agent }: IdentityCardProps) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [isGenerating, setIsGenerating] = useState(false);

    const downloadCard = async () => {
        if (!cardRef.current) return;
        setIsGenerating(true);
        try {
            const canvas = await html2canvas(cardRef.current, {
                useCORS: true,
                scale: 2, // Retina quality
                backgroundColor: null,
            });
            const link = document.createElement('a');
            link.download = `IQLAWD-Identity-${agent.username}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } catch (err) {
            console.error("Card generation failed:", err);
        } finally {
            setIsGenerating(false);
        }
    };

    const shareTwitter = () => {
        // Use x_handle if available, otherwise username. Strip existing @ if present.
        const handle = agent.x_handle ? agent.x_handle.replace('@', '') : agent.username;
        const karmaText = agent.karma >= 1000 ? `${(agent.karma / 1000).toFixed(1)}k` : agent.karma.toString();
        const text = `Just verified @${handle} on @IQLAWD! 🛡️\n\nTrust Score: ${Math.round(agent.trust_score)}/100\nKarma: ${karmaText}\n\nCheck the sovereign integrity scan here: https://iqlawd.com\n\n#IQLAWD #AI #Crypto #AgentEconomy`;
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
    };

    return (
        <div className="flex flex-col items-center gap-6">
            {/* The Card (Hidden overflow container for clean edges) */}
            <div className="relative group perspective-1000">
                <div
                    ref={cardRef}
                    className="w-[320px] h-[480px] relative bg-black rounded-3xl overflow-hidden border-2 border-red-600/50 shadow-[0_0_50px_rgba(220,38,38,0.3)]"
                    style={{
                        backgroundImage: 'radial-gradient(circle at 50% 0%, #3f1010 0%, #000000 70%)'
                    }}
                >
                    {/* Cyberpunk Grid Background */}
                    <div className="absolute inset-0 opacity-20"
                        style={{ backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

                    {/* Top Header */}
                    <div className="absolute top-0 left-0 w-full p-6 text-center z-10">
                        <div className="flex justify-center items-center gap-2 mb-1">
                            <Shield className="w-5 h-5 text-red-600 fill-red-600" />
                            <span className="text-xl font-black text-white tracking-widest italic uppercase">IQLAWD</span>
                        </div>
                        <div className="text-[8px] text-red-500 font-mono uppercase tracking-[0.4em]">Sovereign Identity Protocol</div>
                    </div>

                    {/* Agent Image */}
                    <div className="absolute top-24 left-1/2 -translate-x-1/2 w-48 h-48">
                        <div className="absolute inset-0 bg-red-600 rounded-full blur-2xl opacity-30 animate-pulse" />
                        <div className="relative w-full h-full rounded-full border-4 border-red-600/80 p-1 bg-black">
                            <img
                                src={agent.x_avatar || agent.avatar_url || '/logo.png'}
                                className="w-full h-full rounded-full object-cover bg-zinc-900"
                                onError={(e) => { (e.target as HTMLImageElement).src = '/logo.png'; }}
                                crossOrigin="anonymous" // Crucial for html2canvas
                            />
                            <div className="absolute bottom-0 right-0 bg-red-600 text-white p-1.5 rounded-full border-4 border-black shadow-lg">
                                <CheckCircle size={20} />
                            </div>
                        </div>
                    </div>

                    {/* Name & ID */}
                    <div className="absolute top-[300px] w-full text-center px-4">
                        <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-1 truncate">{agent.display_name}</h2>
                        <p className="text-xs font-mono text-red-500 uppercase tracking-widest">@{agent.username}</p>
                    </div>

                    {/* Stats Grid */}
                    <div className="absolute bottom-8 left-4 right-4 grid grid-cols-2 gap-3">
                        <div className="bg-white/5 border border-white/10 rounded-xl p-3 backdrop-blur-sm">
                            <div className="text-[9px] text-zinc-500 uppercase font-black tracking-widest mb-1">Trust Score</div>
                            <div className="text-3xl font-black text-white flex items-center gap-1">
                                {Math.round(agent.trust_score)}
                                <span className="text-xs text-red-500 font-bold">%</span>
                            </div>
                        </div>
                        <div className="bg-white/5 border border-white/10 rounded-xl p-3 backdrop-blur-sm">
                            <div className="text-[9px] text-zinc-500 uppercase font-black tracking-widest mb-1">Prophet Karma</div>
                            <div className="text-3xl font-black text-white flex items-center gap-1">
                                {agent.karma >= 1000 ? (agent.karma / 1000).toFixed(1) : agent.karma}
                                <span className="text-xs text-yellow-500 font-bold">{agent.karma >= 1000 ? 'K' : ''}</span>
                            </div>
                        </div>
                    </div>

                    {/* Decorative Elements */}
                    <div className="absolute top-4 right-4 w-2 h-2 bg-red-600 rounded-full animate-ping" />
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-[8px] text-zinc-700 font-mono">VERIFIED ON CHAIN - ID: {Date.now().toString().slice(-6)}</div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
                <button
                    onClick={downloadCard}
                    disabled={isGenerating}
                    className="flex items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white px-6 py-3 rounded-full font-bold transition-all border border-white/10 hover:border-red-500/50"
                >
                    <Download size={18} />
                    {isGenerating ? 'Forging...' : 'Save Card'}
                </button>
                <button
                    onClick={shareTwitter}
                    className="flex items-center gap-2 bg-[#1DA1F2] hover:bg-[#1a91da] text-white px-6 py-3 rounded-full font-bold transition-all shadow-[0_0_20px_rgba(29,161,242,0.3)] hover:scale-105"
                >
                    <Share2 size={18} />
                    Share Identity
                </button>
            </div>
        </div>
    );
}
