import streamlit as st
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add rfp-automation directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'rfp-automation'))

try:
    from main import process_rfp
    from utils.gemini_wrapper import GeminiLLM
except ImportError:
    # Dummy mock for dev
    def process_rfp(path):
        return {}

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FMCG Agentic AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'theme' not in st.session_state:
    st.session_state.theme = 'Dark'
if 'rfp_input_content' not in st.session_state:
    st.session_state['rfp_input_content'] = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [{"role": "assistant", "content": "Hello! I am your FMCG RFP Assistant. Upload a document or approve SKUs to get started."}]
if 'current_rfp_result' not in st.session_state:
    st.session_state.current_rfp_result = None
if 'sku_decisions' not in st.session_state:
    st.session_state['sku_decisions'] = {}

# --- SIDEBAR & THEME ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.session_state.theme = st.radio("Theme Mode", ["Dark", "Light"], horizontal=True)
    st.markdown("---")

# --- DYNAMIC CSS ---
if st.session_state.theme == 'Dark':
    bg_color = "#0E1117"  # Deep Black
    sidebar_bg = "#262730"
    text_color = "#FFFFFF"
    card_bg = "#1E1E1E"
    input_bg = "#2D2D2D"
    # Red Theme Colors
    primary_color = "#FF4B4B"
    border_color = "#333"
else:
    # Keep light mode as fallback but user likely wants dark matching image
    bg_color = "#F0F2F6"
    sidebar_bg = "#FFFFFF"
    text_color = "#31333F"
    card_bg = "#FFFFFF"
    input_bg = "#FFFFFF"
    primary_color = "#FF4B4B"
    border_color = "#E0E0E0"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    section[data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid {border_color}; }}
    h1, h2, h3, p, div, label, span {{ color: {text_color} !important; }}
    
    /* Custom Red/Black Metric Card */
    .metric-card {{
        background-color: {card_bg};
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border-bottom: 4px solid {primary_color}; /* Red Bottom Border */
        margin-bottom: 10px;
    }}
    .metric-value {{ font-size: 28px; font-weight: bold; color: {primary_color} !important; margin: 5px 0; }}
    .metric-label {{ font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: #BBB !important; }}
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: {input_bg}; color: {text_color}; border: 1px solid {border_color};
    }}
    /* Red Buttons */
    .stButton > button {{
        background-color: {primary_color};
        color: white !important; 
        border: none;
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        background-color: #FF2B2B; /* Darker Red on Hover */
    }}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_rfp_history():
    history_file = "data/rfp_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f: return json.load(f)
        except: return []
    return []

def save_to_history(rfp_id, filename, result, file_path):
    history_file = "data/rfp_history.json"
    history = get_rfp_history()
    entry = {
        "id": rfp_id,
        "filename": filename,
        "date": datetime.now().strftime("%b %d, %Y %H:%M"),
        "value": result.get('pricing', {}).get('summary', {}).get('total_value', 0),
        "file_path": str(file_path)
    }
    history.insert(0, entry)
    os.makedirs("data", exist_ok=True)
    with open(history_file, 'w') as f: json.dump(history[:10], f, indent=2)

# --- MAIN HEADER ---
# 1-4-1 Ratio for Logo - Title - Robot
header_col1, header_col2, header_col3 = st.columns([1, 4, 1])
with header_col1:
    if os.path.exists("header_left.png"):
        st.image("header_left.png", width=120)
    else:
        st.write("🤖") 
with header_col2:
    # Updated Title to match image
    st.markdown("<h1 style='text-align: center; margin-top: 25px; font-size: 42px;'>Intelligent RFP Automation</h1>", unsafe_allow_html=True)
with header_col3:
    if os.path.exists("header_right.png"):
        st.image("header_right.png", width=120)
    else:
        st.write("🤖")

# --- SIDEBAR HISTORY ---
with st.sidebar:
    st.markdown("### 🕒 Recent Orders")
    history = get_rfp_history()
    if not history: st.markdown("*No history yet*")
    
    for i, item in enumerate(history):
        st.markdown(f"""
        <div style='padding:10px; background:{input_bg}; border-radius:5px; margin-bottom:10px; border-left: 3px solid #00B4D8;'>
            <div style='font-weight:bold;'>{item.get('filename','ORDER')}</div>
            <div style='font-size:12px;'>{item.get('date')}</div>
            <div style='font-size:12px; color:#00B4D8;'>₹{item.get('value',0)/1000:.1f}k</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reload", key=f"hist_{i}"):
            if os.path.exists(item.get('file_path')):
                with open(item.get('file_path'), 'r', encoding='utf-8', errors='ignore') as f:
                     st.session_state['rfp_input_content'] = f.read()
            st.rerun()

# --- INPUT SECTION ---
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 📥 New Order / RFP Parsing")
    uploaded_file = st.file_uploader("Upload PDF/Text", type=["pdf", "txt"], label_visibility="collapsed")
with col2:
    st.markdown("### 📝 Quick Paste")
    rfp_text_input = st.text_area("Paste text", value=st.session_state['rfp_input_content'], height=100, label_visibility="collapsed")

if st.button("🚀 Process RFP", use_container_width=True):
    if uploaded_file or rfp_text_input:
        with st.spinner("Processing..."):
            # Save file
            os.makedirs("data/rfp_uploads", exist_ok=True)
            path = f"data/rfp_uploads/input_{int(time.time())}.txt"
            if uploaded_file:
                path = f"data/rfp_uploads/{uploaded_file.name}"
                with open(path, "wb") as f: f.write(uploaded_file.read())
                filename = uploaded_file.name
            else:
                with open(path, "w", encoding="utf-8") as f: f.write(rfp_text_input)
                filename = "Manual_Input.txt"
                st.session_state['rfp_input_content'] = rfp_text_input
            
            # Progress Bar for "Game-Style" Loading
            progress_bar = st.progress(0, text="Initializing Agent...")
            
            def update_streamlit_progress(stage, pct):
                # Map stage to percent if needed, or use main.py's percent
                progress_bar.progress(pct, text=f"Processing: {stage}")

            # Process with callback
            result = process_rfp(path, progress_callback=update_streamlit_progress)
            
            # Complete
            progress_bar.progress(100, text="Completed!")
            time.sleep(0.5)
            progress_bar.empty()

            st.session_state.current_rfp_result = result
            save_to_history(result['rfp_id'], filename, result, path)
            st.rerun()

# --- DASHBOARD ---
if st.session_state.current_rfp_result:
    res = st.session_state.current_rfp_result
    
    # METRICS
    st.markdown("---")
    # METRICS
    st.markdown("### Key Metrics")
    m1, m2, m3, m4 = st.columns(4)
    pricing = res.get('pricing', {}).get('summary', {})
    
    # Custom HTML Card Helper
    def metric_card(label, value, sub=""):
        return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div style="font-size:12px; color:#888;">{sub}</div>
        </div>
        """

    with m1: 
        st.markdown(metric_card("WIN PROBABILITY", f"{res.get('insights', {}).get('win_probability_pct', 65)}%"), unsafe_allow_html=True)
    with m2: 
        st.markdown(metric_card("QUOTE VALUE", f"₹{pricing.get('grand_total', 0):,.0f}"), unsafe_allow_html=True)
    with m3: 
        st.markdown(metric_card("MARGIN", f"{pricing.get('overall_margin_pct', 0)}%"), unsafe_allow_html=True)
    with m4:
        st.markdown(metric_card("RISK LEVEL", res.get('insights', {}).get('risk_level', 'Medium')), unsafe_allow_html=True)

    # TABS
    tab_req, tab_sku, tab_price, tab_insights, tab_email, tab_chat = st.tabs([
        "🟩 Requirements Extraction", "🟦 SKU Matching", "💰 Pricing Details", "🧠 Intelligent Insights", "📧 Email Draft", "💬 AI Assistant"
    ])

    with tab_req:
        st.subheader("Requirements Extraction")
        intake = res.get('rfp_data', {})
        items = intake.get('line_items', [])
        
        if items:
            for i, item in enumerate(items, 1):
                # Fallback logic if specific fields aren't found
                name = item.get('item_name') or item.get('description', 'Unknown Item')
                spec = item.get('specifications', '')
                qty = item.get('quantity', 'N/A')
                
                # Format: 1. Mixer Grinder – 500W – Qty 50
                line_str = f"{i}. {name}"
                if spec:
                    line_str += f" – {spec}"
                line_str += f" – Qty {qty}"
                
                st.markdown(f"**{line_str}**")
        elif intake.get('error'):
            st.error(f"⚠️ Extraction Failed: {intake.get('error')}")
            st.info("The system may be busy. Please wait a few seconds and click 'Reload' in the sidebar.")
        else:
            st.warning("No line items extracted.")

    with tab_sku:
        st.subheader("SKU Matching Intelligence")
        sku_data = res.get('sku_matches', {}).get('matches', [])
        
        if sku_data:
            # Table Header
            c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 1, 3])
            c1.markdown("**Requirement**")
            c2.markdown("**Suggested SKU**")
            c3.markdown("**Match %**")
            c4.markdown("**Evidence**")
            c5.markdown("**Action**")
            st.markdown("---")

            for i, item in enumerate(sku_data):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 1, 3])
                
                # 1. Requirement
                with c1: 
                    st.write(item.get('original_desc', ''))
                    if item.get('matched_sku_code'):
                        st.caption(f"Ref: {item.get('matched_sku_code')}")

                # 2. Suggested SKU
                with c2: 
                    st.write(item.get('matched_sku_name', 'No Match'))

                # 3. Match %
                with c3:
                    # Check user decision first
                    key_idx = i
                    user_decision = st.session_state.sku_decisions.get(key_idx, "Pending")
                    
                    if "Accepted" in user_decision:
                        st.markdown(":green[**100%** (Verified)]")
                    else:
                        conf = item.get('match_confidence_score', 0) * 100
                        color = "green" if conf > 80 else "orange" if conf > 50 else "red"
                        st.markdown(f":{color}[{conf:.0f}%]")

                # 4. Evidence Popover
                with c4:
                    with st.popover("📄"):
                        st.markdown(f"**RFP Snippet:**\n> {item.get('original_desc')}")
                        st.markdown(f"**Catalog Info:**\n{item.get('matched_sku_details', 'N/A')}")
                        st.markdown(f"**Match Reason:**\n{item.get('reason')}")

                # 5. Action (Human-in-the-loop)
                with c5:
                    key_base = f"sku_{i}"
                    current_status = st.session_state.sku_decisions.get(i, "Pending")
                    
                    if current_status == "Pending":
                        b1, b2, b3 = st.columns(3)
                        # Accept
                        if b1.button("✓", key=f"{key_base}_acc", help="Accept Match"):
                            st.session_state.sku_decisions[i] = "Accepted"
                            st.rerun()
                        
                        # Adjust (Popover)
                        with b2.popover("✎", help="Adjust SKU"):
                            new_sku_val = st.text_input("Correct SKU Name/Code", key=f"{key_base}_adj_input")
                            if st.button("Save", key=f"{key_base}_save"):
                                st.session_state.sku_decisions[i] = f"Adjusted: {new_sku_val}"
                                st.rerun()

                        # Reject
                        if b3.button("✗", key=f"{key_base}_rej", help="Reject Match"):
                            st.session_state.sku_decisions[i] = "Rejected"
                            st.rerun()
                    else:
                        # Show Status if already decided
                        if "Accepted" in current_status:
                            st.success(f"✅ {current_status}")
                        elif "Adjusted" in current_status:
                            st.warning(f"⚠️ {current_status}")
                        else:
                            st.error(f"❌ {current_status}")
                            
                        if st.button("Undo", key=f"{key_base}_undo"):
                            del st.session_state.sku_decisions[i]
                            st.rerun()
                
                st.markdown("---")

            # Bulk Actions at bottom
            cb1, cb2 = st.columns(2)
            if cb1.button("✅ Approve All High Confidence"):
                for idx, it in enumerate(sku_data):
                    if it.get('match_confidence_score', 0) > 0.8:
                         st.session_state.sku_decisions[idx] = "Accepted"
                st.rerun()
                
        else:
            st.info("No SKUs to match.")

    with tab_price:
        st.subheader("Pricing Details")
        p_table = res.get('pricing', {}).get('pricing_table', [])
        
        if p_table:
            # Margin Control
            st.markdown("### 🎚️ Margin Adjustment")
            margin_pct = st.slider("Target Margin %", min_value=0, max_value=50, value=20, step=1, help="Adjust profit margin to update the final quote.")
            
            # Prepare Dynamic Data
            pricing_data = []
            running_subtotal = 0
            
            for item in p_table:
                # Backend 'net_unit_price' is treated as our Cost/Base Price here
                base_price = item.get('net_unit_price', 0)
                qty = item.get('qty', 0)
                
                # Calculate Sell Price based on Margin: Cost / (1 - Margin%)
                # Avoid division by zero
                if margin_pct >= 100: margin_pct = 99
                
                sell_price = base_price / (1 - (margin_pct/100))
                line_total = sell_price * qty
                running_subtotal += line_total
                
                pricing_data.append({
                    "SKU": item.get('sku_name', 'Unknown'),
                    "Qty": qty,
                    "Unit Cost (est.)": f"₹{base_price:,.2f}",
                    "Final Unit Price": f"₹{sell_price:,.2f}", 
                    "Line Total": f"₹{line_total:,.2f}"
                })
            
            # Display Table
            st.table(pricing_data)
            
            # Calculate Summary
            gst_rate = 0.18
            gst_amount = running_subtotal * gst_rate
            final_total = running_subtotal + gst_amount
            
            # Calculate Savings (simulated based on discount from backend)
            # Backend gives 'total_discount_amount' based on volume. 
            # We can show that as "Volume Savings"
            backend_summ = res.get('pricing', {}).get('summary', {})
            backend_discount = backend_summ.get('total_discount_amount', 0)
            savings_pct = 0
            if final_total > 0:
                savings_pct = (backend_discount / (final_total + backend_discount)) * 100

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Subtotal:** ₹{running_subtotal:,.2f}")
                st.markdown(f"**GST (18%):** ₹{gst_amount:,.2f}")
            with c2:
                st.metric("Final Quote Amount", f"₹{final_total:,.2f}")
                if backend_discount > 0:
                    st.success(f"📉 Includes Volume Savings of ₹{backend_discount:,.2f} ({savings_pct:.1f}%)")

        else:
            st.info("Pricing not generated.")

    with tab_insights:
        st.subheader("Intelligent Insights")
        insights = res.get('insights', {})
        
        # 1. Risks & Mitigation
        risks = insights.get('risks', [])
        if risks:
            st.markdown("##### ⚠️ Risks & Mitigation")
            for r in risks:
                with st.expander(f"{r.get('type', 'Risk').title()}: {r.get('description')}", expanded=True):
                    st.write(f"**Mitigation:** {r.get('mitigation', 'N/A')}")
                    st.caption(f"Severity: {r.get('severity', 'Medium').title()}")
        
        st.markdown("---")
        
        # 2. Competitors & Strengths
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🏢 Competitors")
            comps = insights.get('competitors', [])
            # Fallback for old format
            if not comps: 
                 old_comps = insights.get('competitor_analysis', [])
                 comps = [c.get('competitor_name') for c in old_comps]
            
            if comps:
                for c in comps:
                    st.info(c)
            else:
                st.caption("No competitor data.")

        with c2:
            st.markdown("##### 💪 Key Strengths")
            strengths = insights.get('strengths', [])
            if strengths:
                for s in strengths:
                    st.success(s)
            else:
                st.caption("No strengths listed.")
                
        # 3. Recommendations
        st.markdown("---")
        st.markdown("##### 💡 Strategic Recommendations")
        recs = insights.get('recommendations', [])
        if recs:
            for r in recs:
                st.markdown(f"- {r}")

    with tab_email:
        st.subheader("Email Draft")
        proposal_content = res.get('proposal', {}).get('content', '')
        if proposal_content:
            st.markdown(proposal_content)
        else:
            st.info("No draft generated.")

    with tab_chat:
        st.subheader("💬 Ask the Agent")
        
        # Display existing messages
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat Input
        if prompt := st.chat_input("Ask about SKU matches, pricing, or the proposal..."):
            # 1. User Message
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # 2. Prepare Context for AI
            with st.spinner("Thinking..."):
                try:
                    # Construct Context from Result
                    context_str = f"""
                    RFP ID: {res.get('rfp_id')}
                    
                    Line Items:
                    {json.dumps(res.get('rfp_data', {}).get('line_items', []), indent=1)}
                    
                    SKU Matches (Confidence & Logic):
                    {json.dumps(res.get('sku_matches', {}).get('matches', []), indent=1)}
                    
                    Pricing Summary:
                    {json.dumps(res.get('pricing', {}).get('summary', {}), indent=1)}
                    
                    User Info: You are the FMCG Agent. Explain matches using the 'reason' field/catalog info.
                    """
                    
                    # Call Gemini
                    llm = GeminiLLM()
                    ai_response = llm.generate_content(prompt, system_instruction=context_str)
                except Exception as e:
                    ai_response = f"I encountered an error: {str(e)}"
            
            # 3. AI Message
            with st.chat_message("assistant"):
                st.write(ai_response)
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})

else:
    st.info("👋 Upload a document or text to start the analysis.")

st.markdown("---")
st.markdown("<div style='text-align:center; color:#555;'>FMCG Agentic AI v3.0</div>", unsafe_allow_html=True)