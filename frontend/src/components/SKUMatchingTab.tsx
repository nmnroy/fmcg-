import { useState } from 'react';
import { Check, X, Edit2, FileText, Info } from 'lucide-react';

interface SKUTabProps {
    data: any;
}

export default function SKUMatchingTab({ data }: SKUTabProps) {
    const [decisions, setDecisions] = useState<Record<number, string>>({});
    const [activeEvidence, setActiveEvidence] = useState<number | null>(null);

    const matches = data.matches || [];

    const handleDecision = (idx: number, status: string) => {
        setDecisions(prev => ({ ...prev, [idx]: status }));
    };

    return (
        <div className="bg-surface rounded-lg p-6 relative">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-primary">SKU Matching Intelligence</h3>
                <div className="space-x-2">
                    <button
                        onClick={() => {
                            const newDecs = { ...decisions };
                            matches.forEach((m: any, i: number) => {
                                if (m.match_confidence_score > 0.8) newDecs[i] = 'Accepted';
                            });
                            setDecisions(newDecs);
                        }}
                        className="px-4 py-2 bg-green-600/20 text-green-400 hover:bg-green-600/30 rounded text-sm font-medium"
                    >
                        Auto-Approve High Confidence
                    </button>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-gray-700 text-gray-400 text-sm uppercase">
                            <th className="py-3 px-4">Requirement</th>
                            <th className="py-3 px-4">Suggested SKU</th>
                            <th className="py-3 px-4">Match %</th>
                            <th className="py-3 px-4">Evidence</th>
                            <th className="py-3 px-4">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {matches.map((item: any, idx: number) => {
                            const conf = item.match_confidence_score * 100;
                            const color = conf > 80 ? 'text-green-400' : conf > 50 ? 'text-orange-400' : 'text-red-400';
                            const status = decisions[idx];

                            return (
                                <tr key={idx} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                                    <td className="py-4 px-4">
                                        <div className="font-medium">{item.original_desc}</div>
                                        <div className="text-xs text-gray-500 mt-1">{item.line_item_id}</div>
                                    </td>
                                    <td className="py-4 px-4 font-mono text-sm text-blue-300">
                                        {item.matched_sku_name || 'No Match'}
                                    </td>
                                    <td className={`py-4 px-4 font-bold ${color}`}>
                                        {conf.toFixed(0)}%
                                    </td>
                                    <td className="py-4 px-4 relative">
                                        <button
                                            onClick={() => setActiveEvidence(activeEvidence === idx ? null : idx)}
                                            className="p-2 hover:bg-primary/20 rounded-full text-primary transition-colors"
                                            title="View Evidence"
                                        >
                                            <FileText size={18} />
                                        </button>
                                        {/* Popover */}
                                        {activeEvidence === idx && (
                                            <div className="absolute z-10 bottom-full left-0 mb-2 w-80 bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-4 text-sm">
                                                <h4 className="font-bold text-gray-300 mb-2 flex items-center gap-2">
                                                    <Info size={14} /> Match Evidence
                                                </h4>
                                                <div className="space-y-3">
                                                    <div>
                                                        <span className="text-xs text-gray-500 uppercase">RFP Text</span>
                                                        <p className="bg-black/30 p-2 rounded mt-1 italic">"{item.original_desc}"</p>
                                                    </div>
                                                    <div>
                                                        <span className="text-xs text-gray-500 uppercase">Catalog Info</span>
                                                        <p className="bg-black/30 p-2 rounded mt-1">{item.matched_sku_details || 'N/A'}</p>
                                                    </div>
                                                    <div>
                                                        <span className="text-xs text-gray-500 uppercase">Reasoning</span>
                                                        <p className="text-blue-300 mt-1">{item.reason}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </td>
                                    <td className="py-4 px-4">
                                        {status ? (
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${status === 'Accepted' ? 'bg-green-500/20 text-green-400' :
                                                    status === 'Rejected' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                                                }`}>
                                                {status}
                                            </span>
                                        ) : (
                                            <div className="flex gap-2">
                                                <button onClick={() => handleDecision(idx, 'Accepted')} className="p-2 hover:bg-green-500/20 text-green-400 rounded transition-colors" title="Accept">
                                                    <Check size={18} />
                                                </button>
                                                <button onClick={() => handleDecision(idx, 'Adjusting')} className="p-2 hover:bg-yellow-500/20 text-yellow-400 rounded transition-colors" title="Adjust">
                                                    <Edit2 size={18} />
                                                </button>
                                                <button onClick={() => handleDecision(idx, 'Rejected')} className="p-2 hover:bg-red-500/20 text-red-400 rounded transition-colors" title="Reject">
                                                    <X size={18} />
                                                </button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
