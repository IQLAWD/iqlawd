import { Action, IAgentRuntime, Memory, State, HandlerCallback } from "@elizaos/core";

export const trustAnalysisAction: Action = {
    name: "CHECK_TRUST_SCORE",
    similes: ["ANALYZE_AGENT", "CHECK_AGENT_TRUST", "GET_TRUST_SCORE"],
    description: "Analyzes the trust score of another agent using the IQLAWD Intelligence System.",
    validate: async (runtime: IAgentRuntime, message: Memory) => {
        return true; // Always allow for now
    },
    handler: async (
        runtime: IAgentRuntime,
        message: Memory,
        state: State,
        options: any,
        callback: HandlerCallback
    ) => {
        const content = message.content.text;
        // Extract agent ID from text (simplified regex)
        const agentIdMatch = content.match(/0x[a-fA-F0-9]{40}/) || content.match(/agent\s+(\w+)/i);
        const agentId = agentIdMatch ? agentIdMatch[0] : "unknown_agent";

        try {
            // Call IQLAWD Python API
            const response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    agent_id: agentId,
                    trade_history: [], // Would normally fetch from runtime memory
                    usage_data: { tx_count: 100, unique_callers: 5 } // Mock data
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();

            // Format response for Eliza to say
            const text = `🕵️‍♂️ **IQLAWD Analysis Report**\n` +
                `Target: ${data.agent_id}\n` +
                `Trust Score: ${data.trust_score}/100\n` +
                `Risk Status: ${data.risk_status}`;

            callback({
                text: text,
                content: data
            });

            return true;
        } catch (error) {
            console.error("IQLAWD Analysis Failed:", error);
            callback({
                text: "⚠️ Failed to connect to IQLAWD Intelligence System. Is the Python server running?",
                error: error.message
            });
            return false;
        }
    },
    examples: [
        [
            {
                user: "{{user1}}",
                content: { text: "Check the trust score of agent 0x123...abc" }
            },
            {
                user: "{{agentName}}",
                content: {
                    text: "🕵️‍♂️ **IQLAWD Analysis Report**\nTarget: 0x123...abc\nTrust Score: 85/100\nRisk Status: STABLE",
                    action: "CHECK_TRUST_SCORE"
                }
            }
        ]
    ]
};
