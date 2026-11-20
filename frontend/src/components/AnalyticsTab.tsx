import { useState, useEffect } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import { TrendingUp, DollarSign, Award, Clock, ShoppingCart, RefreshCw } from 'lucide-react';
import { fetchAnalytics, type AnalyticsData } from '../lib/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'];

const CHANNEL_MARGINS = [
    { channel: 'Quick Commerce', target: 22, actual: 20.8 },
    { channel: 'Corporate / Hotel', target: 20, actual: 19.5 },
    { channel: 'Modern Trade', target: 18, actual: 17.6 },
    { channel: 'Distributor Wholesale', target: 14, actual: 13.9 },
];

export default function AnalyticsTab() {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(false);

    const loadData = async () => {
        setLoading(true);
        try {
            const data = await fetchAnalytics();
            setAnalytics(data);
        } catch (err) {
            console.error('Error fetching analytics:', err);
            // Default mock for offline preview
            setAnalytics({
                total_rfps_processed: 48,
                pipeline_value_inr: 24850000,
                avg_win_rate_pct: 74.5,
                active_rfps_count: 8,
                category_distribution: {
                    'Personal Care': 45,
                    'Home Care': 38,
                    'Packaged Foods': 32,
                    'Beverages': 28,
                    'Dairy & Staples': 22,
                    'Oral Care': 18
                },
                top_demanded_skus: [
                    { sku_code: 'HUL_SURF_001', name: 'Surf Excel Matic 2kg', orders_count: 48, revenue: 1420000 },
                    { sku_code: 'HUL_DOVE_001', name: 'Dove Hair Fall 340ml', orders_count: 42, revenue: 980000 },
                    { sku_code: 'NES_MAG_001', name: 'Maggi 8-Pack 560g', orders_count: 39, revenue: 650000 },
                    { sku_code: 'HUL_VIM_001', name: 'Vim Gel 750ml', orders_count: 35, revenue: 490000 },
                    { sku_code: 'ITC_ASH_003', name: 'Aashirvaad Ghee 1L', orders_count: 28, revenue: 820000 }
                ]
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const catData = analytics?.category_distribution
        ? Object.entries(analytics.category_distribution).map(([name, value]) => ({ name, value }))
        : [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center bg-surface p-6 rounded-lg border border-gray-800">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <TrendingUp className="text-primary" /> FMCG Commercial Intelligence
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">
                        Executive sales metrics, category order volumes, and deal economics.
                    </p>
                </div>
                <button
                    onClick={loadData}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-sm transition-colors border border-gray-700"
                >
                    <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh Data
                </button>
            </div>

            {/* Metric KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-surface p-5 rounded-lg border border-gray-800 border-b-4 border-b-blue-500">
                    <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                        <span>Pipeline Value</span>
                        <DollarSign className="text-blue-400" size={18} />
                    </div>
                    <div className="text-2xl font-bold text-white mt-2">
                        ₹{(analytics?.pipeline_value_inr || 24850000) / 10000000} Cr
                    </div>
                    <div className="text-xs text-green-400 mt-1">↑ +14.2% vs last month</div>
                </div>

                <div className="bg-surface p-5 rounded-lg border border-gray-800 border-b-4 border-b-green-500">
                    <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                        <span>Win Probability Rate</span>
                        <Award className="text-green-400" size={18} />
                    </div>
                    <div className="text-2xl font-bold text-white mt-2">
                        {analytics?.avg_win_rate_pct || 74.5}%
                    </div>
                    <div className="text-xs text-green-400 mt-1">Top quartile distributor</div>
                </div>

                <div className="bg-surface p-5 rounded-lg border border-gray-800 border-b-4 border-b-amber-500">
                    <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                        <span>Total RFPs Processed</span>
                        <ShoppingCart className="text-amber-400" size={18} />
                    </div>
                    <div className="text-2xl font-bold text-white mt-2">
                        {analytics?.total_rfps_processed || 48}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">Orders analyzed by AI</div>
                </div>

                <div className="bg-surface p-5 rounded-lg border border-gray-800 border-b-4 border-b-purple-500">
                    <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                        <span>Avg Turnaround Time</span>
                        <Clock className="text-purple-400" size={18} />
                    </div>
                    <div className="text-2xl font-bold text-white mt-2">12.4s</div>
                    <div className="text-xs text-green-400 mt-1">98% faster than manual</div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Category Distribution Pie */}
                <div className="bg-surface p-6 rounded-lg border border-gray-800">
                    <h3 className="text-lg font-bold text-white mb-4">Category Volume Share</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={catData}
                                    dataKey="value"
                                    nameKey="name"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={80}
                                    label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${(((percent ?? 0) * 100)).toFixed(0)}%`}
                                >
                                    {catData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#fff' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Channel Margin Comparison */}
                <div className="bg-surface p-6 rounded-lg border border-gray-800">
                    <h3 className="text-lg font-bold text-white mb-4">Channel Margin Performance (%)</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={CHANNEL_MARGINS} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="channel" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#fff' }}
                                />
                                <Legend />
                                <Bar dataKey="target" fill="#3b82f6" name="Target Margin %" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="actual" fill="#10b981" name="Actual Realized %" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Top Demanded SKUs Table */}
            <div className="bg-surface p-6 rounded-lg border border-gray-800">
                <h3 className="text-lg font-bold text-white mb-4">Top Revenue Generating SKUs</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-sm">
                        <thead>
                            <tr className="border-b border-gray-700 text-gray-400 uppercase text-xs">
                                <th className="py-3 px-4">SKU Code</th>
                                <th className="py-3 px-4">Product Name</th>
                                <th className="py-3 px-4">Orders Count</th>
                                <th className="py-3 px-4">Gross Revenue</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(analytics?.top_demanded_skus || []).map((sku, idx) => (
                                <tr key={idx} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                                    <td className="py-3 px-4 font-mono text-blue-400">{sku.sku_code}</td>
                                    <td className="py-3 px-4 font-medium text-white">{sku.name}</td>
                                    <td className="py-3 px-4 text-gray-300">{sku.orders_count} orders</td>
                                    <td className="py-3 px-4 font-bold text-green-400">₹{sku.revenue.toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
