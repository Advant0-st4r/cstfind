"""
Main Streamlit application for CustomerFinder MVP
"""

import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime

# CRITICAL: Load environment variables FIRST to prevent import failures
load_dotenv()

# Initialize session state safely before any operations
if '_session_initialized' not in st.session_state:
    st.session_state._session_initialized = True
    st.session_state.last_request = None
    st.session_state.result = None
    st.session_state.request_count = 0

# Check API key immediately with clear user feedback
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("sk-your-key"):
    st.error("""
    🔴 **CRITICAL: OPENAI_API_KEY NOT CONFIGURED**
    
    **Immediate Actions Required:**
    1. Copy `.env.example` to `.env` in the project root
    2. Add your valid OpenAI API key to `.env`
    3. Restart the application
    
    **Current Status:** `{}`
    
    Get your API key from: https://platform.openai.com/api-keys
    """.format("❌ NOT SET" if not api_key else "⚠️ USING PLACEHOLDER"))
    st.stop()

# Now safely import the API module (environment is ready)
from utils.api_utils import safe_generate_customer_list

# Configure Streamlit page
st.set_page_config(
    page_title="🇶🇦 CustomerFinder MVP",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Header
st.title("🇶🇦 CustomerFinder MVP")
st.subheader("Market Validation & Corporate Lead Generation Tool")

# Critical User Notes
with st.expander("⚠️ **Critical Deployment Notes**", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cost Management**")
        st.caption("• Each generation: ~$0.015 USD (0.055 QAR)")
        st.caption("• Average tokens: 800-1,200 per request")
        st.caption("• Monthly budget: ~$10 for 650+ generations")
    
    with col2:
        st.markdown("**Qatar-Specific Features**")
        st.caption("• Doha timezone (UTC+3)")
        st.caption("• Qatari corporate entities prioritized")
        st.caption("• QNV 2030 alignment indicators")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Tier Selection
    st.subheader("Target Tiers")
    tier_options = [
        "Tier 1: Strategic Corporate Venture Arms",
        "Tier 2: Value-Add Corporations", 
        "Tier 3: Angel Syndicates & Investors"
    ]
    selected_tiers = st.multiselect(
        "Select target tiers:",
        tier_options,
        default=tier_options,
        help="Tier 1: Legacy-building, Tier 2: Synergies, Tier 3: Growth focus"
    )
    
    # Qatar-Specific Settings
    st.subheader("🇶🇦 Qatar Settings")
    align_qnv2030 = st.checkbox(
        "Align with Qatar National Vision 2030", 
        value=True,
        help="Prioritize entities aligned with QNV 2030 pillars"
    )
    
    # Cost Estimation
    st.subheader("💰 Cost Estimation")
    st.metric("Per Generation", "0.055 QAR", "~$0.015 USD")
    st.caption("Based on gpt-4o-mini model")
    
    # Session Info
    st.divider()
    st.caption(f"Session requests: {st.session_state.request_count}")
    if st.session_state.last_request:
        st.caption("Last request: Active")

# Main Input Section
st.header("📝 Business Input")

business_desc = st.text_area(
    "**Business Description**",
    height=120,
    placeholder="Example: B2B SaaS platform for supply chain optimization in manufacturing with AI-powered predictive analytics...",
    help="Be specific about your value proposition, target industry, and unique differentiators."
)

other_specs = st.text_area(
    "**Additional Specifications**",
    height=80,
    placeholder="Example: Manufacturing sector, enterprise focus (500+ employees), requires ERP integration, target Doha market...",
    help="Include industry, company size, geographic focus, technical requirements, or specific constraints."
)

# Validation and Generation
if not business_desc.strip():
    st.warning("Please enter a business description to continue.")
else:
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        generate_btn = st.button(
            "🚀 Generate Customer List",
            type="primary",
            use_container_width=True,
            disabled=not business_desc.strip()
        )
    
    with col2:
        clear_btn = st.button(
            "🔄 Clear Session",
            use_container_width=True,
            help="Reset all session data"
        )
    
    if clear_btn:
        st.session_state.last_request = None
        st.session_state.result = None
        st.session_state.request_count = 0
        st.rerun()
    
    if generate_btn:
        # Build current request signature for duplicate detection
        current_input = f"{business_desc}{''.join(selected_tiers)}{other_specs}{align_qnv2030}".strip()
        
        # Duplicate request check
        if st.session_state.last_request == current_input:
            st.warning("⚠️ Identical request detected. Previous result shown below.")
        else:
            # Build specifications string
            specs = f"Selected tiers: {', '.join(selected_tiers)}. "
            specs += f"Qatar alignment: {align_qnv2030}. "
            specs += f"Additional: {other_specs}"
            
            # Generate with progress indicator
            with st.spinner("🧠 Generating targeted customer list..."):
                result = safe_generate_customer_list(business_desc, specs, align_qnv2030)
                
                if result["success"]:
                    # Update session state
                    st.session_state.result = result
                    st.session_state.last_request = current_input
                    st.session_state.request_count += 1
                    
                    # Success message with metrics
                    qatar_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    st.success(f"✅ **Generation Complete!** | Time: {qatar_time} (UTC+3)")
                    
                    # Display metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Tokens Used", f"{result['tokens']:,}")
                    with metric_col2:
                        st.metric("Cost", f"${result['cost_usd']:.4f} USD")
                    with metric_col3:
                        st.metric("Qatar Focus", "✅" if result.get('qatar_focus') else "🌍")
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📋 Generated Customer List")
                    st.markdown(result["content"])
                    
                    # Export functionality
                    st.download_button(
                        label="📥 Download as Markdown",
                        data=f"# CustomerFinder MVP Results\n## Generated: {qatar_time}\n## Market Focus: Qatar\n\n{result['content']}",
                        file_name=f"qatar_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                else:
                    st.error(f"❌ Generation failed: {result['error']}")
                    if "API key" in result["error"]:
                        st.info("Check your `.env` file and ensure OPENAI_API_KEY is valid and has credits.")

# Display previous results if available
if st.session_state.result and st.session_state.result["success"]:
    with st.expander("📜 View Previous Generation", expanded=False):
        st.markdown(st.session_state.result["content"])
        st.caption(f"Generated at {st.session_state.result.get('timestamp', 'Unknown')}")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("🔍 **CustomerFinder MVP v2.0**")
with footer_col2:
    st.caption("🇶🇦 **Optimized for Qatar Market**")
with footer_col3:
    st.caption(f"🔄 **Requests this session:** {st.session_state.request_count}")