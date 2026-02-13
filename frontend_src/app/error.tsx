'use client';
import { useEffect } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

export default function Error({ error, reset }: { error: Error & { digest?: string }, reset: () => void }) {
    useEffect(() => {
        console.error(error);
    }, [error]);

    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center p-4 text-center">
            <div className="text-red-600 animate-pulse mb-8">
                <AlertTriangle size={64} />
            </div>
            <h2 className="text-4xl font-black text-white uppercase tracking-tighter mb-4">System Malfunction</h2>
            <div className="font-mono text-xs text-red-400 mb-8 max-w-md mx-auto border border-red-900/30 bg-red-900/10 p-4 rounded-lg overflow-hidden break-words">
                <div className="mb-2 uppercase tracking-widest font-black">Diagnostic Output:</div>
                {error.message || "Unknown anomaly detected in neural lattice."}
            </div>
            <button
                onClick={() => reset()}
                className="flex items-center gap-2 bg-white/10 hover:bg-red-600 hover:text-white text-zinc-300 px-8 py-3 rounded-full font-black uppercase tracking-widest transition-all border border-white/10 hover:border-red-500"
            >
                <RefreshCcw size={16} />
                Reinitialize System
            </button>
        </div>
    );
}
