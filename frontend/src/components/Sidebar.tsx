import { LayoutDashboard, FileText, Bot, BarChart2, Users, Settings, LogOut } from 'lucide-react';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
}

const Sidebar = ({ activeTab, setActiveTab }: SidebarProps) => {
    const menuItems = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'active-rfps', label: 'Active RFPs', icon: FileText },
        { id: 'agents', label: 'AI Agents', icon: Bot },
        { id: 'analytics', label: 'Analytics', icon: BarChart2 },
        { id: 'team', label: 'Team', icon: Users },
    ];

    return (
        <aside className="w-64 bg-surface border-r border-gray-800 flex flex-col h-screen fixed left-0 top-0">
            {/* Logo Area */}
            <div className="p-6 flex items-center gap-3">
                <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center font-bold text-black text-xl">
                    EY
                </div>
                <div>
                    <h1 className="font-bold text-white text-lg leading-tight">RFP Engine</h1>
                    <p className="text-xs text-text-muted">AI-Powered Response</p>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 py-6 px-4 space-y-2">
                {menuItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-sm font-medium ${activeTab === item.id
                                ? 'bg-gray-800 text-primary'  // Active state: Darker bg, Yellow text
                                : 'text-text-muted hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <item.icon size={20} className={activeTab === item.id ? 'text-primary' : 'text-text-muted'} />
                        {item.label}
                    </button>
                ))}
            </div>

            {/* Bottom Menu */}
            <div className="p-4 border-t border-gray-800 space-y-1">
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-text-muted hover:text-white hover:bg-white/5 transition-colors text-sm font-medium">
                    <Settings size={20} />
                    Settings
                </button>
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-text-muted hover:text-white hover:bg-white/5 transition-colors text-sm font-medium">
                    <LogOut size={20} />
                    Logout
                </button>
            </div>

            {/* User Profile */}
            <div className="p-6 pt-2">
                <div className="flex items-center gap-3 p-3 bg-background/50 rounded-xl border border-gray-800">
                    <div className="w-10 h-10 rounded-full bg-green-400 flex items-center justify-center text-black font-bold">
                        SA
                    </div>
                    <div className="overflow-hidden">
                        <p className="text-sm font-bold text-white truncate">Shourya Agrawal</p>
                        <p className="text-xs text-text-muted truncate">Sales Manager</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
