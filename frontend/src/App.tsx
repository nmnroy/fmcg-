import { useState, useEffect } from 'react';
import { uploadRFP } from './lib/api';

// Components
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ProgressBar from './components/ProgressBar';

// Legacy Components (To be integrated properly or accessed via tabs)
import SKUMatchingTab from './components/SKUMatchingTab';
import PricingTab from './components/PricingTab';
import ProposalTab from './components/ProposalTab';
import ChatTab from './components/ChatTab';

const RequirementsTab = ({ data }: { data: any }) => (
  <div className="p-6 bg-surface rounded-lg">
    <h3 className="text-xl font-bold mb-6 text-primary border-b border-gray-700 pb-4">Extracted Requirements</h3>
    {data.line_items?.length ? (
      <div className="grid gap-4">
        {data.line_items.map((item: any, idx: number) => (
          <div key={idx} className="p-5 bg-background border border-gray-800 rounded-lg flex flex-col md:flex-row md:items-center justify-between hover:border-primary/50 transition-colors group">
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 font-mono text-sm group-hover:bg-primary group-hover:text-black transition-colors">
                {idx + 1}
              </div>
              <div>
                <span className="font-bold text-lg text-white block">{item.item_name || item.description}</span>
                <span className="text-gray-400 text-sm">{item.specifications}</span>
              </div>
            </div>
            <div className="mt-3 md:mt-0 px-4 py-1 bg-gray-800 rounded-full text-sm font-medium text-blue-300 border border-gray-700">
              Qty: {item.quantity}
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p className="text-gray-500">No data found.</p>
    )}
  </div>
);

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // State for Job Processing
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('Initializing');

  // Polling Effect
  useEffect(() => {
    let interval: any;

    if (loading && jobId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://localhost:8000/api/status/${jobId}`);
          const data = await res.json();

          if (res.ok) {
            setProgress(data.progress || 0);
            setStage(data.stage || 'Processing');

            if (data.status === 'completed') {
              setResult(data.result);
              setLoading(false);
              setJobId(null);
              setActiveTab('req'); // Auto-switch to results
            } else if (data.status === 'failed') {
              setLoading(false);
              setJobId(null);
              alert(`Processing Failed: ${data.error}`);
            }
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [loading, jobId]);

  // Handle file upload
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const f = e.target.files[0];
      setLoading(true);
      setProgress(0);
      setStage("File received");

      try {
        const res = await uploadRFP(f);
        if (res.job_id) {
          setJobId(res.job_id);
          // Polling effect will kick in
        } else {
          // Check if it returned direct result (legacy fallback)
          setResult(res);
          setLoading(false);
          setActiveTab('req');
        }
      } catch (err) {
        alert("Error uploading file");
        console.error(err);
        setLoading(false);
      }
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'req': // Mapping old IDs to new view for compatibility
      case 'active-rfps':
        if (!result && activeTab === 'req') {
          // If no result, show the Active RFPs / Upload instructions
          // For now, let's reuse the old "Upload" view as the "Active RFPs" detail view for a specific item
          // Or create a simplified "Active RFPs" list. 
          // To stick to the "Image" request, "Active RFPs" might just be a list.
          // But we want to preserve the functionality.
          // Let's return a "Upload New" placeholder if no result.
          return (
            <div className="p-8 flex flex-col items-center justify-center h-full">
              {loading ? (
                <ProgressBar progress={progress} stage={stage} />
              ) : (
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-white mb-4">Active RFPs</h2>
                  <p className="text-gray-400 mb-8">Upload a new RFP to start processing.</p>
                  <div className="relative inline-block">
                    <input
                      type="file"
                      onChange={handleUpload}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                      accept=".txt,.pdf"
                    />
                    <button className="bg-primary hover:bg-yellow-400 text-black px-6 py-3 rounded-lg font-bold transition-colors">
                      Upload New RFP
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        }
        // If result exists, show Requirements (as "Active RFP Detail")
        return result ? <RequirementsTab data={result.rfp_data} /> : null;

      case 'sku': // Access via some other way? Or add to sidebar?
        // The sidebar has 'agents' or 'analytics'.
        // For now, I'll map 'agents' to 'sku' logic if needed, or just hide it until requested.
        // Let's map 'active-rfps' to the result view flow.
        return result ? <SKUMatchingTab data={result.sku_matches} /> : <div className="p-8">No active SKU matching session.</div>;

      case 'price':
        return result ? <PricingTab data={result} /> : <div className="p-8">No active Pricing session.</div>;

      case 'prop':
        return result ? <ProposalTab data={result} /> : <div className="p-8">No active Proposal session.</div>;

      case 'chat':
        return result ? <ChatTab contextData={result} /> : <div className="p-8">AI Assistant ready. Upload RFP to begin context.</div>;

      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-background text-text font-sans overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 ml-64 overflow-auto relative">
        {/* We can put the TopBar here or inside specific pages. Dashboard has its own header in the design. */}
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
