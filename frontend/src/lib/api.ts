import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface CatalogItem {
    sku_id: string;
    name: string;
    category: string;
    specs: string;
    base_cost: number;
    unit: string;
    gst_pct: number;
    pack_size?: string;
}

export interface AnalyticsData {
    total_rfps_processed: number;
    pipeline_value_inr: number;
    avg_win_rate_pct: number;
    active_rfps_count: number;
    category_distribution: Record<string, number>;
    top_demanded_skus: Array<{
        sku_code: string;
        name: string;
        orders_count: number;
        revenue: number;
    }>;
}

export const uploadRFP = async (file: File, simulationMode = false) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_URL}/process?simulation_mode=${simulationMode}`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const processRFPText = async (text: string, clientName = "Retail Partner", simulationMode = false) => {
    const response = await axios.post(`${API_URL}/process-text`, {
        text,
        client_name: clientName,
        simulation_mode: simulationMode
    });
    return response.data;
};

export const fetchJobStatus = async (jobId: string) => {
    const response = await axios.get(`${API_URL}/status/${jobId}`);
    return response.data;
};

export const sendChatMessage = async (message: string, context: string) => {
    const response = await axios.post(`${API_URL}/chat`, {
        message,
        context,
    });
    return response.data.response;
};

export const fetchCatalog = async (category?: string, query?: string) => {
    const params = new URLSearchParams();
    if (category && category !== 'All') params.append('category', category);
    if (query) params.append('q', query);

    const response = await axios.get(`${API_URL}/catalog?${params.toString()}`);
    return response.data;
};

export const simulatePricing = async (items: Array<any>, marginPct: number) => {
    const response = await axios.post(`${API_URL}/pricing/simulate`, {
        margin_pct: marginPct,
        items,
    });
    return response.data;
};

export const validateCompliance = async (orderData: {
    client_name?: string;
    deadline?: string;
    pricing_table?: Array<any>;
    grand_total?: number;
}) => {
    const response = await axios.post(`${API_URL}/compliance/validate`, orderData);
    return response.data;
};

export const fetchAnalytics = async (): Promise<AnalyticsData> => {
    const response = await axios.get(`${API_URL}/analytics`);
    return response.data;
};

export const fetchHistory = async (limit = 20, query?: string) => {
    const params = new URLSearchParams();
    params.append('limit', String(limit));
    if (query) params.append('q', query);

    const response = await axios.get(`${API_URL}/history?${params.toString()}`);
    return response.data;
};

export const getExportPdfUrl = (jobOrRfpId: string) => `${API_URL}/rfp/${jobOrRfpId}/export/pdf`;
export const getExportExcelUrl = (jobOrRfpId: string) => `${API_URL}/rfp/${jobOrRfpId}/export/excel`;
