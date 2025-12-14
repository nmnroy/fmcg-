import { FileText, Zap, Trophy, Clock, TrendingUp, DollarSign, Bell, Search, MessageSquare } from 'lucide-react';
import StatCard from './StatCard';

const Dashboard = () => {
    return (
        <div className="p-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-4">
                    <img src="/logo_left.png" alt="Logo Left" className="h-12 w-auto object-contain" />
                    <div>
                        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                        <p className="text-text-muted mt-1">AI-powered RFP response management</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <img src="/logo_right.png" alt="Logo Right" className="h-12 w-auto object-contain mr-4" />

                    {/* Search Bar */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                        <input
                            type="text"
                            placeholder="Search RFPs..."
                            className="bg-card border border-gray-800 rounded-lg pl-10 pr-4 py-2.5 w-64 text-sm text-white focus:outline-none focus:border-gray-600"
                        />
                    </div>

                    {/* Icons */}
                    <button className="items-center justify-center w-10 h-10 rounded-lg border border-gray-800 text-gray-400 hover:text-white hover:bg-gray-800 transition-colors relative hidden md:flex">
                        <Bell size={20} />
                        <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-surface"></span>
                    </button>
                    <button className="items-center justify-center w-10 h-10 rounded-lg border border-gray-800 text-gray-400 hover:text-white hover:bg-gray-800 transition-colors relative hidden md:flex">
                        <MessageSquare size={20} />
                        <span className="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full border border-surface"></span>
                    </button>
                </div>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <StatCard
                    title="Total RFPs"
                    value="48"
                    subtext="↑ +12 this month"
                    subtextType="positive"
                    icon={FileText}
                    accentColor="none"
                />
                <StatCard
                    title="Active RFPs"
                    value="12"
                    icon={Zap}
                    accentColor="yellow"
                />
                <StatCard
                    title="Won This Month"
                    value="5"
                    icon={Trophy}
                    accentColor="green"
                />
                <StatCard
                    title="Avg Response Time"
                    value="2.3 days"
                    subtext="↑ -40% faster"
                    subtextType="positive"
                    icon={Clock}
                    accentColor="none"
                />
                <StatCard
                    title="Win Rate"
                    value="68%"
                    icon={TrendingUp}
                    accentColor="none" // Image has gradient or blue icon? The image has a blue/green gradient icon background or icon itself.
                // Let's use blue for Win Rate icon bg in StatCard if needed, or just let it be default dark.
                // Image shows "Win Rate" with a cyan/teal icon button.
                />
                <StatCard
                    title="Pipeline Value"
                    value="$24.8M"
                    icon={DollarSign}
                    accentColor="none"
                />
            </div>

            {/* Active RFPs Section (Placeholder) */}
            <div>
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-white">Active RFPs</h2>
                    <button className="text-primary text-sm font-medium hover:underline">View all →</button>
                </div>
                {/* List would go here */}
            </div>
        </div>
    );
};

export default Dashboard;
