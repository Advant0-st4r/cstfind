# Customer Finder MVP

A Streamlit application for generating targeted lists of potential corporate customers, partners, and investors using OpenAI's GPT models.

## Features
- **Targeted Generation**: Get 10 specific, actionable leads based on your business description
- **Cost Tracking**: Real-time calculation of API usage costs
- **Export Results**: Download generated lists as markdown files
- **Error Handling**: Robust error handling and user-friendly messages
- **Duplicate Prevention**: Session state prevents duplicate API calls

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/Advant0-st4r/custfind.git
cd custfind

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

