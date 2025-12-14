import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Now the rest of your imports
import streamlit as st
from main import process_rfp
import json
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Asian Paints RFP Automation",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for Asian Paints theme
st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #C1272D 0%, #E31E24 50%, #FF4757 100%);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 8px 16px rgba(227, 30, 36, 0.3);
        animation: fadeIn 0.6s ease-in;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        margin: 15px 0 0 0;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Upload section styling */
    .stFileUploader {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        padding: 30px;
        border-radius: 12px;
        border: 2px dashed #E31E24;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #FF4757;
        box-shadow: 0 0 20px rgba(227, 30, 36, 0.2);
        transform: translateY(-2px);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: #2a2a2a !important;
        border: 2px solid #444 !important;
        border-radius: 10px !important;
        color: white !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #E31E24 !important;
        box-shadow: 0 0 15px rgba(227, 30, 36, 0.3) !important;
    }
    
    /* Section headers */
    h3 {
        color: white !important;
        font-weight: 600 !important;
        margin-bottom: 20px !important;
        padding-bottom: 10px !important;
        border-bottom: 3px solid #E31E24 !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #E31E24 0%, #C1272D 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem 2.5rem;
        border-radius: 50px;
        transition: all 0.3s ease;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF4757 0%, #E31E24 100%);
        box-shadow: 0 6px 20px rgba(227, 30, 36, 0.6);
        transform: translateY(-3px);
    }
    .stButton>button:active {
        transform: translateY(-1px);
    }
    .metric-card {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #E31E24;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(227, 30, 36, 0.3);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #E31E24 0%, #FF4757 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .sidebar-rfp-item {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 4px solid #E31E24;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .sidebar-rfp-item:hover {
        background: linear-gradient(135deg, #E31E24 0%, #C1272D 100%);
        transform: translateX(8px);
        box-shadow: 0 4px 12px rgba(227, 30, 36, 0.4);
    }
    .rfp-title {
        font-weight: 700;
        color: white;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    .rfp-date {
        font-size: 0.8rem;
        color: #aaa;
    }
    .rfp-metric-small {
        display: inline-block;
        background: linear-gradient(135deg, #E31E24 0%, #FF4757 100%);
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-right: 6px;
        margin-top: 8px;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(227, 30, 36, 0.3);
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        color: white !important;
        border: 2px solid #E31E24 !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #E31E24 0%, #C1272D 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4) !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        border-left: 4px solid #E31E24 !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for RFP history
if 'rfp_history' not in st.session_state:
    st.session_state.rfp_history = []
    # Load existing history from file if exists
    history_file = Path("data/rfp_history.json")
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                st.session_state.rfp_history = json.load(f)
        except:
            st.session_state.rfp_history = []

def save_history():
    """Save RFP history to file"""
    history_file = Path("data/rfp_history.json")
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.rfp_history, f, indent=2)

def add_to_history(rfp_data):
    """Add processed RFP to history"""
    history_item = {
        'rfp_id': rfp_data['rfp_id'],
        'timestamp': datetime.now().isoformat(),
        'filename': rfp_data.get('filename', 'Unknown'),
        'win_probability': rfp_data['insights'].get('win_probability_pct', 0),
        'quote_value': rfp_data['pricing'].get('summary', {}).get('total_value', 0),
        'margin': rfp_data['pricing'].get('summary', {}).get('overall_margin_pct', 0)
    }
    st.session_state.rfp_history.insert(0, history_item)
    if len(st.session_state.rfp_history) > 20:
        st.session_state.rfp_history = st.session_state.rfp_history[:20]
    save_history()

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Previously Processed RFPs")
    st.markdown("---")
    
    if st.session_state.rfp_history:
        for idx, item in enumerate(st.session_state.rfp_history[:10]):
            with st.container():
                st.markdown(f"""
                <div class="sidebar-rfp-item">
                    <div class="rfp-title">{item.get('filename', 'RFP')}</div>
                    <div class="rfp-date">{datetime.fromisoformat(item['timestamp']).strftime('%b %d, %Y %H:%M')}</div>
                    <div>
                        <span class="rfp-metric-small">Win: {item['win_probability']}%</span>
                        <span class="rfp-metric-small">₹{item['quote_value']:,.0f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View #{idx+1}", key=f"view_{idx}"):
                    output_dir = Path(f"output/{item['rfp_id']}")
                    if output_dir.exists():
                        st.info(f"RFP ID: {item['rfp_id']}")
    else:
        st.info("No RFPs processed yet. Upload your first RFP to get started!")
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    show_debug = st.checkbox("Show Debug Info", value=False)
    
    if st.button("🗑️ Clear History"):
        st.session_state.rfp_history = []
        save_history()
        st.rerun()

# Main content
st.markdown("""
<div class="main-header">
    <h1>🎨 Asian Paints RFP Automation</h1>
    <p>Intelligent Proposal Generation System</p>
</div>
""", unsafe_allow_html=True)

# Create two columns for better layout
col_upload, col_text = st.columns([1, 1])

with col_upload:
    st.markdown("### 📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose RFP file",
        type=["pdf", "txt", "docx"],
        help="Upload PDF, TXT, or DOCX files"
    )

with col_text:
    st.markdown("### ✍️ Or Paste Text")
    rfp_text = st.text_area(
        "RFP Content",
        height=150,
        placeholder="Paste your RFP text here..."
    )

# Process button with better styling
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    process_button = st.button("🚀 Process RFP", use_container_width=True)

if process_button:
    if uploaded_file or rfp_text:
        with st.spinner("🎨 Processing your RFP... Please wait..."):
            # Create necessary directories
            Path("data/rfp_uploads").mkdir(parents=True, exist_ok=True)
            
            # Save file
            filename = None
            if uploaded_file:
                filename = uploaded_file.name
                temp_path = f"data/rfp_uploads/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
            else:
                filename = f"text_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                temp_path = f"data/rfp_uploads/{filename}"
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(rfp_text)
            
            # Process RFP
            try:
                result = process_rfp(temp_path)
                result['filename'] = filename
                
                # Add to history
                add_to_history(result)
                
                st.success("✅ RFP Processing Complete!")
                
                # Enhanced metrics display
                st.markdown("### 📊 Key Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    win_prob = result['insights'].get('win_probability_pct', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Win Probability</div>
                        <div class="metric-value">{win_prob}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    quote_value = result['pricing'].get('summary', {}).get('total_value', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Quote Value</div>
                        <div class="metric-value">₹{quote_value:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    margin = result['pricing'].get('summary', {}).get('overall_margin_pct', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Margin</div>
                        <div class="metric-value">{margin:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    risk_level = result['insights'].get('risk_level', 'Medium')
                    risk_color = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#dc3545'}.get(risk_level, '#ffc107')
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Risk Level</div>
                        <div class="metric-value" style="color: {risk_color};">{risk_level}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download section
                st.markdown("---")
                st.markdown("### 📥 Download Documents")
                
                output_dir = Path(f"output/{result['rfp_id']}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if (output_dir / "proposal.md").exists():
                        with open(output_dir / "proposal.md", "r", encoding="utf-8") as f:
                            proposal_content = f.read()
                        
                        st.download_button(
                            "📄 Proposal",
                            proposal_content,
                            file_name=f"Asian_Paints_Proposal_{result['rfp_id']}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                
                with col2:
                    if (output_dir / "pricing.json").exists():
                        with open(output_dir / "pricing.json", "r", encoding="utf-8") as f:
                            pricing_content = f.read()
                        
                        st.download_button(
                            "💰 Pricing",
                            pricing_content,
                            file_name=f"Pricing_{result['rfp_id']}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                with col3:
                    if (output_dir / "insights.json").exists():
                        with open(output_dir / "insights.json", "r", encoding="utf-8") as f:
                            insights_content = f.read()
                        
                        st.download_button(
                            "🔍 Insights",
                            insights_content,
                            file_name=f"Insights_{result['rfp_id']}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                # Detailed information in expanders
                st.markdown("---")
                st.markdown("### 📋 Detailed Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("🔍 View Insights", expanded=False):
                        st.json(result['insights'])
                
                with col2:
                    with st.expander("💰 View Pricing Details", expanded=False):
                        st.json(result['pricing'])
                
                # Debug info
                if show_debug:
                    with st.expander("🐛 Debug Information"):
                        st.write("**RFP ID:**", result['rfp_id'])
                        st.write("**Output Directory:**", str(output_dir))
                        st.write("**Files Created:**")
                        if output_dir.exists():
                            for file in output_dir.iterdir():
                                st.write(f"- {file.name}")
                    
            except Exception as e:
                st.error(f"❌ Error processing RFP: {str(e)}")
                if show_debug:
                    st.exception(e)
                st.info("💡 Please check that all agents are configured correctly and try again.")
    else:
        st.warning("⚠️ Please upload a file or paste RFP text first!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎨 Powered by Asian Paints | AI-Driven RFP Automation | © 2025</p>
    <p style='font-size: 0.8rem;'>Transforming the way we respond to RFPs with intelligent automation</p>
</div>
""", unsafe_allow_html=True)