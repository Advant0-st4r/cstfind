import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime

# CRITICAL: Load environment variables BEFORE importing api_utils
load_dotenv()

# Quick environment validation
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("sk-your-key-here"):
    st.error("""
    ⚠️ **OPENAI_API_KEY Not Configured**
    
    1. Copy `.env.example` to `.env`
    2. Add your OpenAI API key (get from https://platform.openai.com/api-keys)
    3. Restart the app
    
    Current status: `OPENAI_API_KEY` is `{}`
    """.format("Not set" if not api_key else "Placeholder detected"))
    st.stop()

# Now import the module that depends on environment variables
from utils.api_utils import safe_generate_customer_list

st.set_page_config(page_title="Customer Finder MVP", layout="wide")

# Initialize session state for duplicate prevention and result persistence
if "last_request" not in st.session_state:
    st.session_state.last_request = None
if "result" not in st.session_state:
    st.session_state.result = None

st.title("Market Validation MVP: Find Potential Customers")

with st.expander("⚠️ Critical Notes", expanded=True):
    st.caption("• Each generation costs ~$0.03 • Don't refresh during generation • Save results manually")

business_desc = st.text_area("Business Description", height=100, 
                           placeholder="Example: B2B SaaS platform for supply chain optimization in manufacturing...",
                           help="Describe your startup clearly. Be specific about target industry, value proposition, and unique differentiators.")
tier_options = ["Tier 1: Strategic Corporate Venture Arms",
                "Tier 2: Value-Add Corporations", 
                "Tier 3: Angel Syndicates and Corporate Investors"]
selected_tiers = st.multiselect("Select Relevant Tiers", tier_options, default=tier_options,
                              help="Choose at least one. Tier 1: Legacy-building, Tier 2: Synergies, Tier 3: Growth focus.")
other_specs = st.text_area("Additional Specifications", height=80,
                         placeholder="Example: Manufacturing sector, enterprise focus, integration with SAP/ERP systems...",
                         help="Include industry, company size, geographic focus, technology stack, or specific requirements.")

if st.button("Generate List of 10 Potential Customers", type="primary", use_container_width=True):
    current_input = f"{business_desc}{''.join(selected_tiers)}{other_specs}".strip()
    
    # Robust input validation and duplicate check
    if not current_input:
        st.error("All fields are required for generation.")
    elif not business_desc.strip() or not selected_tiers:
        st.error("Business description and at least one tier are required.")
    elif st.session_state.last_request == current_input:
        st.warning("Identical request already processed. Modify inputs or view previous result below.")
    else:
        specs = f"Selected tiers: {', '.join(selected_tiers)}. Other specs: {other_specs}"
        
        with st.spinner("Generating targeted customer list..."):
            result = safe_generate_customer_list(business_desc, specs)
            
            if result["success"]:
                st.session_state.result = result
                st.session_state.last_request = current_input
                
                st.success(f"✅ Generated successfully! Tokens: {result['tokens']:,} | Cost: ${result['cost']:.4f} | Time: {result['timestamp'][11:19]}")
                st.markdown(result["content"])
                
                # Robust export with timestamp
                st.download_button(
                    label="📥 Download Results as Markdown",
                    data=result["content"],
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            else:
                st.error(f"❌ Generation failed: {result['error']}")
                if "API key" in result["error"]:
                    st.info("Check your .env file and ensure OPENAI_API_KEY is set correctly.")

# Display previous result if available (persists across refreshes)
if st.session_state.result and st.session_state.result["success"]:
    with st.expander("📋 Previous Generation", expanded=False):
        st.markdown(st.session_state.result["content"])
        st.caption(f"Generated at {st.session_state.result['timestamp']}")

st.markdown("---")
st.caption("MVP v1.2 | Robust error handling, cost tracking, and export enabled | Ready for deployment")