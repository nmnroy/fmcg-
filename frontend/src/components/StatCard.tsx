import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
    title: string;
    value: string | number;
    subtext?: string;
    subtextType?: 'positive' | 'negative' | 'neutral';
    icon?: LucideIcon;
    iconColor?: string; // class name for color
    accentColor?: 'yellow' | 'green' | 'blue' | 'none'; // Defines the icon background highlight
}

const StatCard = ({ title, value, subtext, subtextType = 'neutral', icon: Icon, accentColor = 'none' }: StatCardProps) => {
    return (
        <div className="bg-card p-6 rounded-2xl border border-gray-800 flex flex-col justify-between h-40 relative overflow-hidden group hover:border-gray-700 transition-colors">
            <div className="flex justify-between items-start z-10">
                <div>
                    <p className="text-text-muted text-sm font-medium mb-1">{title}</p>
                    <h3 className="text-3xl font-bold text-white mt-2">{value}</h3>
                    {subtext && (
                        <p className={`text-xs font-medium mt-2 flex items-center gap-1 ${subtextType === 'positive' ? 'text-green-400' :
                                subtextType === 'negative' ? 'text-green-400' : // Image uses green for "faster" which is positive
                                    'text-text-muted'
                            }`}>
                            {subtext}
                        </p>
                    )}
                </div>

                {Icon && (
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center border border-white/5 ${accentColor === 'yellow' ? 'bg-primary text-black' :
                            accentColor === 'green' ? 'bg-success text-white' :
                                accentColor === 'blue' ? 'bg-secondary text-white' :
                                    'bg-gray-800 text-text-muted'
                        }`}>
                        <Icon size={24} />
                    </div>
                )}
            </div>

            {/* Optional decorative gradient glow */}
            {accentColor === 'green' && <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-success/10 blur-3xl rounded-full"></div>}
            {accentColor === 'yellow' && <div className="absolute -top-10 -right-10 w-32 h-32 bg-primary/10 blur-3xl rounded-full"></div>}
        </div>
    );
};

export default StatCard;
