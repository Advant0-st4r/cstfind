import streamlit as st
from dotenv import load_dotenv
from utils.api_utils import safe_generate_customer_list
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Customer Finder MVP", layout="wide")

# Initialize session state for duplicate prevention and result persistence
if "last_request" not in st.session_state:
    st.session_state.last_request = None
if "result" not in st.session_state:
    st.session_state.result = None

st.title("Market Validation MVP: Find Potential Customers")

with st.expander("⚠️ Critical Notes", expanded=True):
    st.caption("• Each generation costs ~$0.03 • Don't refresh during generation • Save results manually • Timezone-aware (Doha +03)")

business_desc = st.text_area("Business Description", height=100, help="Describe your startup clearly.")
tier_options = ["Tier 1: Strategic Corporate Venture Arms",
                "Tier 2: Value-Add Corporations",
                "Tier 3: Angel Syndicates and Corporate Investors"]
selected_tiers = st.multiselect("Select Relevant Tiers", tier_options, help="Choose at least one.")
other_specs = st.text_area("Additional Specifications", height=80, help="E.g., industry, location (like Doha), size.")

if st.button("Generate List of 10 Potential Customers", type="primary"):
    current_input = f"{business_desc}{''.join(selected_tiers)}{other_specs}".strip()
    
    # Robust input validation and duplicate check
    if not current_input:
        st.error("All fields are required for generation.")
    elif not business_desc.strip() or not selected_tiers:
        st.error("Business description and at least one tier required.")
    elif st.session_state.last_request == current_input:
        st.warning("Identical request already processed. Modify inputs or view previous result below.")
    else:
        specs = f"Selected tiers: {', '.join(selected_tiers)}. Other specs: {other_specs}"
        
        with st.spinner("Generating targeted customer list..."):
            result = safe_generate_customer_list(business_desc, specs)
            
            if result["success"]:
                st.session_state.result = result
                st.session_state.last_request = current_input
                
                st.success(f"Generated successfully! Tokens: {result['tokens']} | Cost: ${result['cost']} | Time: {result['timestamp']} (+03 Doha)")
                st.markdown(result["content"])
                
                # Robust export with timestamp
                st.download_button(
                    label="Download Results as Markdown",
                    data=result["content"],
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            else:
                st.error(f"Generation failed: {result['error']}. Please check API key or network.")

# Display previous result if available (persists across refreshes)
if st.session_state.result and st.session_state.result["success"]:
    with st.expander("📋 Previous Generation", expanded=False):
        st.markdown(st.session_state.result["content"])
        st.caption(f"Generated at {st.session_state.result['timestamp']} (+03)")

st.markdown("---")

# Add at the top with other imports
import pytz
from datetime import datetime

# Qatar-specific configuration
QATAR_TIMEZONE = pytz.timezone('Asia/Qatar')

st.set_page_config(
    page_title="Qatar Market Validation MVP", 
    layout="wide",
    page_icon="🇶🇦"
)

# Update the critical notes section
with st.expander("🇶🇦 Qatar Deployment Notes", expanded=True):
    st.caption("• Tailored for Qatari market entities • Aligns with Qatar National Vision 2030 • Each generation costs ~$0.03")
    st.caption("• Timezone: Doha (UTC+3) • Arabic-language support coming soon")
    st.caption("• **Key Entities**: QIA, Qatar Foundation, QDB, Ooredoo, Qatar Airways, Msheireb, QSTP")

# Update the tier selection to Qatar-specific
tier_options = [
    "Tier 1: Qatar Strategic Corporate Arms (QIA, Qatar Foundation, QDB)",
    "Tier 2: Qatar Growth & Innovation Corporations (Ooredoo, Msheireb, QSTP)", 
    "Tier 3: Qatar Angel Investors & Family Offices (Al Fardan, Al Attiyah, 360 Nautilus)"
]

# Add Qatar National Vision 2030 alignment toggle
with st.sidebar:
    st.header("🇶🇦 Qatar Settings")
    align_qnv2030 = st.checkbox("Align with Qatar National Vision 2030", value=True)
    include_arabic = st.checkbox("Include Arabic contact recommendations", value=False)
    
    if align_qnv2030:
        pillars = st.multiselect(
            "QNV 2030 Pillars",
            ["Human Development", "Social Development", "Economic Development", "Environmental Development"],
            default=["Economic Development"]
        )
    
    # Cost display for Qatari Riyal
    st.subheader("Cost Estimation")
    st.metric("Approx. Cost per Generation", f"~0.11 QAR", f"${0.03:.2f} USD")
    
# Update success message with Qatari context
if result["success"]:
    qatar_time = datetime.now(QATAR_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
    st.success(f"✅ Generated successfully for Qatari market! | Cost: {result['cost_qar']:.2f} QAR | Time: {qatar_time} Doha")
    
# Add export with Qatar context
st.download_button(
    label="📥 Download Results (Qatar Focused)",
    data=f"# Qatar Market Analysis\n## Generated for Doha Market\n{result['content']}",
    file_name=f"qatar_customers_{datetime.now(QATAR_TIMEZONE).strftime('%Y%m%d')}.md",
    mime="text/markdown"
)