import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Loader2 } from 'lucide-react';

interface ProgressBarProps {
    progress: number;
    stage: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, stage }) => {
    // Define stages for visual milestones
    const stages = [
        { name: "File Received", threshold: 5 },
        { name: "Parsing RFP", threshold: 20 },
        { name: "Extracting Requirements", threshold: 40 },
        { name: "Matching SKUs", threshold: 65 },
        { name: "Pricing Calculation", threshold: 80 },
        { name: "Generating Proposal", threshold: 95 },
        { name: "Completed", threshold: 100 }
    ];

    return (
        <div className="w-full max-w-2xl mx-auto p-6 bg-card border border-border rounded-xl shadow-lg">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    {progress < 100 ? (
                        <Loader2 className="animate-spin text-primary" />
                    ) : (
                        <CheckCircle2 className="text-green-500" />
                    )}
                    Processing RFP...
                </h3>
                <span className="text-2xl font-mono text-primary">{progress}%</span>
            </div>

            {/* Main Progress Bar */}
            <div className="h-4 bg-gray-800 rounded-full overflow-hidden mb-6 relative">
                <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 via-primary to-purple-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ type: "spring", stiffness: 50 }}
                />

                {/* Glitch Overlay effect (optional sweetness) */}
                <div className="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
            </div>

            {/* Stage Indicators */}
            <div className="space-y-3">
                <div className="flex justify-between text-sm text-gray-400 border-b border-gray-800 pb-2 mb-2">
                    <span>Current Stage:</span>
                    <span className="text-white font-medium animate-pulse">{stage}</span>
                </div>

                <div className="grid grid-cols-1 gap-2">
                    {stages.map((s, idx) => {
                        const isCompleted = progress >= s.threshold;
                        const isCurrent = progress < s.threshold && (idx === 0 || progress >= stages[idx - 1].threshold);

                        return (
                            <div key={idx} className={`flex items-center gap-3 text-sm ${isCompleted ? 'text-green-400' : isCurrent ? 'text-white' : 'text-gray-600'}`}>
                                <div className={`w-2 h-2 rounded-full ${isCompleted ? 'bg-green-500' : isCurrent ? 'bg-white animate-pulse' : 'bg-gray-700'}`}></div>
                                <span>{s.name}</span>
                                {isCompleted && <CheckCircle2 size={14} className="ml-auto" />}
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    );
};

export default ProgressBar;
