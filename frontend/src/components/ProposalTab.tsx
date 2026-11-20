import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Download, Copy, Printer, Check, FileSpreadsheet } from 'lucide-react';
import { getExportPdfUrl, getExportExcelUrl } from '../lib/api';

interface ProposalTabProps {
    data: any;
}

export default function ProposalTab({ data }: ProposalTabProps) {
    const [copied, setCopied] = useState(false);
    const content = data?.proposal?.content || '';
    const rfpId = data?.rfp_id || 'ORDER_DEMO';

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            {/* Top Toolbar */}
            <div className="bg-surface p-4 rounded-lg border border-gray-800 flex flex-wrap justify-between items-center gap-4">
                <div>
                    <h3 className="text-lg font-bold text-white">Commercial Proposal Document</h3>
                    <p className="text-gray-400 text-xs">Official quotation draft ready for client signature</p>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded text-xs font-medium transition-colors border border-gray-700"
                    >
                        {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                        {copied ? 'Copied' : 'Copy'}
                    </button>

                    <button
                        onClick={() => window.print()}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded text-xs font-medium transition-colors border border-gray-700"
                    >
                        <Printer size={14} /> Print
                    </button>

                    <a
                        href={getExportExcelUrl(rfpId)}
                        download
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600/20 text-green-400 hover:bg-green-600/30 rounded text-xs font-medium transition-colors border border-green-700/50"
                    >
                        <FileSpreadsheet size={14} /> Export CSV
                    </a>

                    <a
                        href={getExportPdfUrl(rfpId)}
                        download
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-black font-bold rounded text-xs hover:bg-primary/90 transition-colors shadow"
                    >
                        <Download size={14} /> Download PDF
                    </a>
                </div>
            </div>

            {/* Proposal Document Body */}
            <div className="bg-surface p-10 rounded-lg shadow-2xl min-h-[600px] border border-gray-800">
                <article className="prose prose-invert prose-headings:text-blue-300 prose-p:text-gray-300 prose-table:border prose-table:border-gray-800 prose-th:bg-gray-900 prose-th:text-gray-200 prose-td:border-t prose-td:border-gray-800 prose-a:text-primary max-w-none">
                    {content ? (
                        <ReactMarkdown>{content}</ReactMarkdown>
                    ) : (
                        <div className="text-center py-16 text-gray-500">
                            <p>No proposal generated yet. Upload an RFP or select an order from history.</p>
                        </div>
                    )}
                </article>
            </div>
        </div>
    );
}
