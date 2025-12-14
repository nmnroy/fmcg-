import { useState } from 'react';
import { TrendingDown, PieChart as PieIcon, BarChart as BarChartIcon } from 'lucide-react';
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
    Cell,
} from 'recharts';

interface PricingTabProps {
    data: any;
}

export default function PricingTab({ data }: PricingTabProps) {
    const [margin, setMargin] = useState(20);
    const p_table = data.pricing_table || [];
    const backendSummary = data.summary || {};

    // Calculate Dynamics
    let runningSubtotal = 0;
    let totalBaseCost = 0;

    const processedItems = p_table.map((item: any) => {
        const base = item.net_unit_price || 0;
        const qty = item.qty || 0;

        // Base Cost Total
        totalBaseCost += base * qty;

        // Sell Price Calculation
        // Base / (1 - Margin%)
        let sellPrice = base;
        if (margin < 100) {
            sellPrice = base / (1 - margin / 100);
        }
        const lineTotal = sellPrice * qty;
        runningSubtotal += lineTotal;

        return { ...item, sellPrice, lineTotal };
    });

    const gstRate = 0.18;
    const gstAmount = runningSubtotal * gstRate;
    const grandTotal = runningSubtotal + gstAmount;
    const totalMarginValue = runningSubtotal - totalBaseCost;

    // --- Chart Data Preparation ---
    // 1. Cost Components for Pie Chart
    const costComponentsData = [
        { name: 'Base Cost', value: totalBaseCost },
        { name: 'Margin', value: totalMarginValue },
        { name: 'GST (18%)', value: gstAmount },
    ];

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b']; // Blue, Green, Amber

    // 2. Top Items by Value for Bar Chart
    const topItemsData = [...processedItems]
        .sort((a, b) => b.lineTotal - a.lineTotal)
        .slice(0, 5)
        .map((item) => ({
            name: item.sku_name?.split(' ').slice(0, 2).join(' ') || 'Unknown', // Shorten name
            full_name: item.sku_name,
            value: item.lineTotal,
        }));

    return (
        <div className="space-y-6">
            <div className="bg-surface rounded-lg p-6">
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <h3 className="text-xl font-bold text-primary mb-2">Commercial Pricing</h3>
                        <p className="text-gray-400 text-sm">
                            Adjust margin to update final quote instantly.
                        </p>
                    </div>

                    <div className="bg-background p-4 rounded-lg w-64 border border-gray-700">
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Target Margin: <span className="text-primary font-bold">{margin}%</span>
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="50"
                            value={margin}
                            onChange={(e) => setMargin(parseInt(e.target.value))}
                            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>0%</span>
                            <span>50%</span>
                        </div>
                    </div>
                </div>

                {/* CHARTS SECTION */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    {/* COST BREAKDOWN PIE */}
                    <div className="bg-background/30 p-4 rounded-lg border border-gray-700/50">
                        <div className="flex items-center gap-2 mb-4 text-gray-300">
                            <PieIcon size={18} />
                            <h4 className="font-semibold text-sm">Cost Components</h4>
                        </div>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={costComponentsData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {costComponentsData.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                                        itemStyle={{ color: '#fff' }}
                                        formatter={(value: number) => `₹${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
                                    />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* TOP ITEMS BAR */}
                    <div className="bg-background/30 p-4 rounded-lg border border-gray-700/50">
                        <div className="flex items-center gap-2 mb-4 text-gray-300">
                            <BarChartIcon size={18} />
                            <h4 className="font-semibold text-sm">Top 5 Items (by Value)</h4>
                        </div>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={topItemsData} layout="vertical" margin={{ left: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" horizontal={false} />
                                    <XAxis type="number" stroke="#666" tickFormatter={(val) => `₹${val / 1000}k`} />
                                    <YAxis dataKey="name" type="category" stroke="#999" width={100} tick={{ fontSize: 12 }} />
                                    <Tooltip
                                        cursor={{ fill: '#ffffff10' }}
                                        contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                                        itemStyle={{ color: '#fff' }}
                                        formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Total Value']}
                                        labelStyle={{ color: '#aaa' }}
                                    />
                                    <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* TABLE */}
                <div className="overflow-x-auto mb-8 rounded-lg border border-gray-700">
                    <table className="w-full text-left">
                        <thead className="bg-background/50">
                            <tr className="text-gray-400 text-sm uppercase">
                                <th className="p-4">SKU Name</th>
                                <th className="p-4 text-center">Qty</th>
                                <th className="p-4 text-right">Unit Cost (Base)</th>
                                <th className="p-4 text-right text-primary">Final Price</th>
                                <th className="p-4 text-right">Line Total</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800">
                            {processedItems.map((item: any, idx: number) => (
                                <tr key={idx} className="hover:bg-white/5">
                                    <td className="p-4 font-medium">{item.sku_name}</td>
                                    <td className="p-4 text-center text-gray-400">{item.qty}</td>
                                    <td className="p-4 text-right font-mono text-gray-500">
                                        ₹{item.net_unit_price?.toLocaleString()}
                                    </td>
                                    <td className="p-4 text-right font-mono text-primary font-bold">
                                        ₹
                                        {item.sellPrice.toLocaleString(undefined, {
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="p-4 text-right font-mono">
                                        ₹
                                        {item.lineTotal.toLocaleString(undefined, {
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* SUMMARY */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="p-6 bg-blue-900/10 border border-blue-900/30 rounded-lg">
                        <div className="flex items-center gap-3 text-blue-400 mb-2">
                            <TrendingDown size={20} />
                            <span className="font-bold uppercase tracking-wider text-sm">
                                Savings Applied
                            </span>
                        </div>
                        {backendSummary.total_discount_amount > 0 ? (
                            <div>
                                <p className="text-2xl font-bold text-white">
                                    ₹{backendSummary.total_discount_amount?.toLocaleString()}
                                </p>
                                <p className="text-sm text-blue-300 mt-1">
                                    Volume discount included in base cost.
                                </p>
                            </div>
                        ) : (
                            <p className="text-gray-500">No volume discounts applicable.</p>
                        )}
                    </div>

                    <div className="space-y-3 text-right">
                        <div className="flex justify-between text-gray-400">
                            <span>Subtotal</span>
                            <span>
                                ₹
                                {runningSubtotal.toLocaleString(undefined, {
                                    maximumFractionDigits: 2,
                                })}
                            </span>
                        </div>
                        <div className="flex justify-between text-gray-400">
                            <span>GST (18%)</span>
                            <span>
                                ₹
                                {gstAmount.toLocaleString(undefined, {
                                    maximumFractionDigits: 2,
                                })}
                            </span>
                        </div>
                        <div className="flex justify-between text-gray-400 pt-2">
                            <span className="text-sm">Profit Margin</span>
                            <span className="text-green-500">
                                +₹
                                {totalMarginValue.toLocaleString(undefined, {
                                    maximumFractionDigits: 2,
                                })}
                            </span>
                        </div>
                        <div className="border-t border-gray-700 pt-3 flex justify-between items-center">
                            <span className="text-xl font-bold text-white">Final Quote</span>
                            <span className="text-3xl font-bold text-primary">
                                ₹
                                {grandTotal.toLocaleString(undefined, {
                                    maximumFractionDigits: 0,
                                })}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
