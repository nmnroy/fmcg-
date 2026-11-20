import { useState, useEffect } from 'react';
import { Search, Tag, CheckCircle2, PackageCheck, Layers } from 'lucide-react';
import { fetchCatalog, type CatalogItem } from '../lib/api';

const DEFAULT_CATEGORIES = [
    'All',
    'Personal Care',
    'Home Care',
    'Packaged Foods',
    'Beverages',
    'Dairy & Staples',
    'Oral Care'
];

export default function CatalogTab() {
    const [items, setItems] = useState<CatalogItem[]>([]);
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const res = await fetchCatalog(selectedCategory, searchQuery);
                if (res && res.items) {
                    setItems(res.items);
                }
            } catch (err) {
                console.error('Failed to load catalog via API:', err);
                // Fallback items
                setItems([
                    { sku_id: 'HUL_SURF_001', name: 'Surf Excel Matic Top Load 2kg', category: 'Home Care', specs: 'weight:2kg, brand:Surf Excel', base_cost: 480, unit: 'pack', gst_pct: 18, pack_size: '2kg' },
                    { sku_id: 'HUL_DOVE_001', name: 'Dove Hair Fall Rescue Shampoo 340ml', category: 'Personal Care', specs: 'volume:340ml, brand:Dove', base_cost: 250, unit: 'bottle', gst_pct: 18, pack_size: '340ml' },
                    { sku_id: 'HUL_VIM_001', name: 'Vim Dishwash Gel 750ml', category: 'Home Care', specs: 'volume:750ml, brand:Vim', base_cost: 155, unit: 'bottle', gst_pct: 18, pack_size: '750ml' },
                    { sku_id: 'NES_MAG_001', name: 'Maggi 2-Minute Masala Noodles 560g (8-Pack)', category: 'Packaged Foods', specs: 'weight:560g, brand:Maggi', base_cost: 112, unit: 'pack', gst_pct: 12, pack_size: '560g' },
                    { sku_id: 'NES_NES_001', name: 'Nescafe Classic Instant Coffee Jar 100g', category: 'Beverages', specs: 'weight:100g, brand:Nescafe', base_cost: 330, unit: 'jar', gst_pct: 18, pack_size: '100g' },
                    { sku_id: 'ITC_ASH_003', name: 'Aashirvaad Svasti Pure Cow Ghee 1L', category: 'Dairy & Staples', specs: 'volume:1L, brand:Aashirvaad', base_cost: 650, unit: 'tin', gst_pct: 5, pack_size: '1L' },
                ]);
            } finally {
                setLoading(false);
            }
        };

        const timer = setTimeout(load, 250);
        return () => clearTimeout(timer);
    }, [selectedCategory, searchQuery]);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-surface p-6 rounded-lg border border-gray-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Layers className="text-primary" /> Master FMCG SKU Catalog
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">
                        Active wholesale repository with verified distributor base prices and GST rates.
                    </p>
                </div>
                <div className="flex items-center gap-2 bg-background border border-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-300">
                    <CheckCircle2 size={14} className="text-green-400" />
                    <span>{items.length} SKUs Listed</span>
                </div>
            </div>

            {/* Filter Bar */}
            <div className="bg-surface p-4 rounded-lg border border-gray-800 space-y-4">
                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search SKU by brand, product name, or specification..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-background border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                    />
                </div>

                {/* Category Pills */}
                <div className="flex flex-wrap gap-2">
                    {DEFAULT_CATEGORIES.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setSelectedCategory(cat)}
                            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                                selectedCategory === cat
                                    ? 'bg-primary text-black font-bold'
                                    : 'bg-background text-gray-400 hover:text-white hover:bg-gray-800 border border-gray-700'
                            }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            {/* Products Grid */}
            {loading ? (
                <div className="py-12 text-center text-gray-400">Loading catalog items...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {items.map((sku) => (
                    <div
                        key={sku.sku_id}
                        className="bg-surface p-5 rounded-lg border border-gray-800 hover:border-gray-700 transition-all flex flex-col justify-between"
                    >
                        <div>
                            <div className="flex justify-between items-start mb-2">
                                <span className="font-mono text-xs text-blue-400 bg-blue-900/30 px-2 py-0.5 rounded border border-blue-800/50">
                                    {sku.sku_id}
                                </span>
                                <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded-full">
                                    GST {sku.gst_pct}%
                                </span>
                            </div>

                            <h4 className="font-bold text-white text-base leading-snug mb-1">
                                {sku.name}
                            </h4>

                            <div className="flex items-center gap-2 text-xs text-text-muted mb-3">
                                <Tag size={12} className="text-gray-500" />
                                <span>{sku.category}</span>
                                <span>•</span>
                                <PackageCheck size={12} className="text-gray-500" />
                                <span>{sku.pack_size || sku.unit}</span>
                            </div>

                            <p className="text-xs text-gray-400 bg-background/50 p-2 rounded mb-4 font-mono truncate">
                                {sku.specs}
                            </p>
                        </div>

                        <div className="pt-3 border-t border-gray-800/80 flex justify-between items-center">
                            <div>
                                <span className="text-xs text-gray-500 block">Distributor Cost</span>
                                <span className="text-lg font-bold text-green-400">
                                    ₹{sku.base_cost.toFixed(2)}
                                </span>
                                <span className="text-xs text-gray-500 ml-1">/ {sku.unit}</span>
                            </div>
                            <span className="text-xs text-green-400 bg-green-950/40 border border-green-800/40 px-2 py-1 rounded">
                                Ready to Stock
                            </span>
                        </div>
                    </div>
                ))}
                </div>
            )}
        </div>
    );
}
