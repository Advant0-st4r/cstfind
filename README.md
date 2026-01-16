\# Customer Finder MVP



Streamlit app for generating potential customers using OpenAI, robust for market validation.



\## Setup

1\. Clone: `git clone <repo-url>`

2\. Install: `pip install -r requirements.txt`

3\. Create .env from .env.example and add OPENAI\_API\_KEY.

4\. Run: `streamlit run app.py`



\## Deployment (Doha-Specific)

\- Use `streamlit run app.py --server.port 8501 --server.address 0.0.0.0`

\- Timezone: App uses UTC but displays +03 for Doha (Jan 15, 2026 deployments).

\- Test: Input business desc, select tiers, generate. Check logs for errors.



\## Robustness Notes

\- Error handling: API, input, network.

\- Cost tracking: Per generation.

\- Persistence: Session state for results.



## Qatar-Specific Deployment Guide

### Prerequisites for Doha Deployment
1. **Timezone Configuration**: Server timezone should be set to Asia/Qatar
2. **Arabic Support**: Ensure system fonts support Arabic characters
3. **Qatari Business Hours**: Consider Doha business hours (Sunday-Thursday, 8 AM-5 PM)

### Qatar Entity Integration
The system is pre-configured with:
- **Tier 1**: Qatar sovereign wealth funds and strategic entities
- **Tier 2**: Qatari corporations with innovation arms
- **Tier 3**: Qatari family offices and angel networks

### Localization Features
- ✅ Qatar National Vision 2030 alignment
- ✅ Arabic language contact recommendations
- ✅ Qatari Riyal (QAR) cost tracking
- ✅ Doha timezone display
- ✅ Cultural and regulatory compliance checks

### Deployment in Doha
```bash
# Set Qatar timezone
export TZ=Asia/Qatar

# Run with Qatar optimization
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Access at: http://localhost:8501


MVP v1 - Ready for instant deploy.

