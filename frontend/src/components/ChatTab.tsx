import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { sendChatMessage } from '../lib/api';

interface ChatTabProps {
    contextData: any;
}

export default function ChatTab({ contextData }: ChatTabProps) {
    const [messages, setMessages] = useState<any[]>([
        { role: 'assistant', content: 'Hello! I have analyzed the RFP. Ask me about SKU matches, pricing, or risks.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Add User Message
        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // Build Context
            const contextStr = JSON.stringify({
                rfp_id: contextData.rfp_id,
                matches: contextData.sku_matches?.matches?.map((m: any) => ({
                    req: m.original_desc,
                    match: m.matched_sku_name,
                    reason: m.reason
                })),
                pricing: contextData.pricing?.summary
            });

            const response = await sendChatMessage(userMsg.content, contextStr);
            setMessages(prev => [...prev, { role: 'assistant', content: response }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error connecting to the agent." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-surface rounded-lg flex flex-col h-[600px] border border-gray-700 overflow-hidden">
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'bg-primary text-black' : 'bg-gray-700'}`}>
                            {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
                        </div>
                        <div className={`p-4 rounded-2xl max-w-[80%] ${msg.role === 'assistant' ? 'bg-gray-800 text-gray-200 rounded-tl-none' : 'bg-primary text-black rounded-tr-none'}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 animate-pulse">
                            <Bot size={18} />
                        </div>
                        <div className="bg-gray-800 p-4 rounded-2xl rounded-tl-none text-gray-400 text-sm">
                            Thinking...
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            <div className="p-4 border-t border-gray-700 bg-background">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about specific SKUs or pricing logic..."
                        className="flex-1 bg-surface border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-primary transition-colors"
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="bg-primary hover:bg-secondary disabled:opacity-50 text-black p-3 rounded-lg transition-colors"
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
}
