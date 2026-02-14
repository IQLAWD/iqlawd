"use client";

import React, { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';

interface Agent {
    username: string;
    display_name: string;
    avatar_url?: string;
    final_score: number;
}

interface AgentSelectorProps {
    onSelect: (agent: Agent) => void;
    placeholder?: string;
}

export default function AgentSelector({ onSelect, placeholder = "Search agents..." }: AgentSelectorProps) {
    const [searchTerm, setSearchTerm] = useState('');
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const fetchAgents = async () => {
            if (!searchTerm) {
                setAgents([]);
                return;
            }
            if (searchTerm.length < 2) return;

            setIsLoading(true);
            try {
                const res = await fetch(`/api/agents/search?q=${searchTerm}&limit=10`);
                if (!res.ok) throw new Error("Search failed");
                const data = await res.json();
                if (Array.isArray(data)) {
                    setAgents(data);
                } else {
                    console.warn("Agent search returned non-array:", data);
                    setAgents([]);
                }
            } catch (err) {
                console.error('Failed to fetch agents', err);
                setAgents([]);
            } finally {
                setIsLoading(false);
            }
        };

        const debounce = setTimeout(() => {
            fetchAgents();
        }, 300);

        return () => clearTimeout(debounce);
    }, [searchTerm]);

    const handleSelect = (agent: Agent) => {
        onSelect(agent);
        setIsOpen(false);
        setSearchTerm('');
    };

    return (
        <div className="relative w-full">
            <div className="relative">
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                        setSearchTerm(e.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                    placeholder={placeholder}
                    className="w-full bg-zinc-900/50 border border-white/10 rounded-lg py-3 px-4 pl-10 text-sm text-white outline-none focus:border-red-600 transition-all font-mono"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                {searchTerm && (
                    <button
                        onClick={() => {
                            setSearchTerm('');
                            setIsOpen(false);
                        }}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white transition-colors"
                    >
                        <X className="w-4 h-4" />
                    </button>
                )}
            </div>

            {isOpen && (
                <div className="absolute top-full mt-2 w-full bg-zinc-900/95 border border-white/10 rounded-lg overflow-hidden backdrop-blur-lg shadow-2xl z-50 max-h-96 overflow-y-auto">
                    {isLoading && (
                        <div className="p-4 text-center text-zinc-500 text-sm">
                            <div className="animate-spin mx-auto w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full mb-2" />
                            Searching...
                        </div>
                    )}

                    {!isLoading && agents.length === 0 && (
                        <div className="p-4 text-center text-zinc-500 text-sm">
                            {searchTerm ? 'No agents found' : 'Start typing to search'}
                        </div>
                    )}

                    {!isLoading && agents.map((agent) => (
                        <button
                            key={agent.username}
                            onClick={() => handleSelect(agent)}
                            className="w-full flex items-center gap-3 p-3 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0"
                        >
                            <img
                                src={agent.avatar_url || '/logo.png'}
                                alt={agent.display_name}
                                className="w-10 h-10 rounded-full border border-white/10"
                                onError={(e) => { (e.target as HTMLImageElement).src = '/logo.png'; }}
                            />
                            <div className="flex-1 text-left">
                                <div className="font-bold text-sm text-white">{agent.display_name}</div>
                                <div className="text-xs text-zinc-500 font-mono">@{agent.username}</div>
                            </div>
                            <div className="text-right">
                                <div className="text-sm font-black text-red-500">{Math.round(agent.final_score)}</div>
                                <div className="text-[9px] text-zinc-600 uppercase">Trust</div>
                            </div>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
