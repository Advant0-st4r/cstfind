import openai
import os
import yaml
from typing import Dict
from datetime import datetime
import logging

# Setup logging for robustness (output to console/file in production)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
COST_PER_1K_TOKENS = {"gpt-4o-mini": 0.015, "gpt-4o": 2.50}  # USD per 1K tokens

def load_prompt_template() -> str:
    """Load prompt from YAML for easy maintenance"""
    try:
        with open("config/prompts.yaml", "r") as f:
            config = yaml.safe_load(f)
        framework_summary = "\n".join([f"- {principle}" for principle in config["outreach_principles"]])
        framework_summary += "\nTiers:\n" + "\n".join([f"- {tier['name']}: {tier['description']}" for tier in config["framework"]["tiers"]])
        return config["prompt_template"].format(framework_summary=framework_summary)
    except FileNotFoundError:
        logger.error("prompts.yaml not found.")
        raise
    except Exception as e:
        logger.error(f"Error loading YAML: {str(e)}")
        raise

def safe_generate_customer_list(business_desc: str, specs: str) -> Dict:
    """Safely generate customer list with error handling, cost tracking, and logging"""
    if not business_desc.strip() or not specs.strip():
        logger.warning("Missing inputs for generation.")
        return {"success": False, "error": "Missing required inputs"}
    
    try:
        prompt_template = load_prompt_template()
        prompt = prompt_template.format(business_desc=business_desc, specs=specs)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        
        tokens_used = response.usage.total_tokens
        cost = (tokens_used / 1000) * COST_PER_1K_TOKENS.get(MODEL, 0.015)
        
        logger.info(f"Generation successful: Tokens={tokens_used}, Cost=${cost}")
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "tokens": tokens_used,
            "cost": round(cost, 4),
            "timestamp": datetime.now().isoformat()
        }
    except openai.APIConnectionError as e:
        logger.error(f"Network error: {str(e)}")
        return {"success": False, "error": "Network error. Check connection."}
    except openai.RateLimitError as e:
        logger.error(f"Rate limit: {str(e)}")
        return {"success": False, "error": "Rate limit exceeded. Retry in 20 seconds."}
    except openai.AuthenticationError as e:
        logger.error(f"Auth error: {str(e)}")
        return {"success": False, "error": "Invalid API key. Check .env."}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
    

# Add to imports
import pytz
from typing import List, Optional

# Qatar-specific configurations
QATAR_ENTITIES = {
    "tier1": [
        "Qatar Investment Authority (QIA)",
        "Qatar Foundation",
        "Qatar Development Bank",
        "Qatar Airways Group",
        "Qatar Energy (formerly Qatar Petroleum)",
        "Qatar National Bank (QNB)",
        "Msheireb Properties",
        "Qatar Science & Technology Park (QSTP)"
    ],
    "tier2": [
        "Ooredoo Qatar",
        "Vodafone Qatar", 
        "Milaha (Qatar Navigation)",
        "Baladna",
        "Aamal Company",
        "Qatar Insurance Company",
        "Dukhan Bank",
        "Qatar Islamic Bank"
    ],
    "tier3": [
        "360 Nautilus VC",
        "Qatar Business Angels Association",
        "Al Fardan Group Family Office",
        "Al Attiyah Group Family Office",
        "Al Mannai Group Investment Arm",
        "Qatar VC Fund of Funds"
    ]
}

# Update COST_PER_1K_TOKENS with QAR conversion
COST_PER_1K_TOKENS = {
    "gpt-4o-mini": {"usd": 0.015, "qar": 0.055},
    "gpt-4o": {"usd": 2.50, "qar": 9.10}
}
USD_TO_QAR = 3.64  # Current exchange rate

def enhance_for_qatar_market(prompt: str, qatar_settings: dict) -> str:
    """Enhance prompt with Qatar-specific context"""
    qatar_context = """
    **Qatar Market Context:**
    - Primary Language: Arabic (English widely used in business)
    - Business Culture: Relationship-focused, hierarchical, formal initial meetings
    - Key Sectors: Energy, Finance, Real Estate, Tourism, Technology
    - Regulatory: Qatar Financial Centre (QFC), Qatar Free Zones Authority (QFZA)
    - Innovation Hubs: Qatar Science & Technology Park, Msheireb Downtown Doha
    
    **Qatar National Vision 2030 Alignment:**
    """
    
    if qatar_settings.get("align_qnv2030"):
        for pillar in qatar_settings.get("pillars", []):
            qatar_context += f"\n- {pillar}: " + {
                "Human Development": "Focus on education, healthcare, and workforce development",
                "Social Development": "Social justice, family values, cultural preservation",
                "Economic Development": "Diversification, private sector growth, knowledge economy",
                "Environmental Development": "Sustainable growth, environmental protection"
            }.get(pillar, "")
    
    if qatar_settings.get("include_arabic"):
        qatar_context += "\n\n**Arabic Language Considerations:**"
        qatar_context += "\n- Provide Arabic translation of company names where applicable"
        qatar_context += "\n- Note preferred contact languages (Arabic/English)"
    
    return prompt + qatar_context

def safe_generate_customer_list(business_desc: str, specs: str, qatar_settings: Optional[dict] = None) -> Dict:
    """Enhanced with Qatar market focus"""
    qatar_settings = qatar_settings or {}
    
    # Add Qatar entity validation
    if "Qatar" in business_desc or "Doha" in business_desc or qatar_settings.get("force_qatar_focus"):
        logger.info("Generating Qatar-focused customer list")
        
        # Add Qatar-specific validation
        if not any(keyword in business_desc.lower() for keyword in ["qatar", "doha", "gulf", "middle east"]):
            logger.warning("Business description lacks Qatar context but Qatar focus requested")
    
    # Enhance prompt with Qatar context
    prompt_template = load_prompt_template()
    base_prompt = prompt_template.format(business_desc=business_desc, specs=specs)
    
    if qatar_settings:
        enhanced_prompt = enhance_for_qatar_market(base_prompt, qatar_settings)
    else:
        enhanced_prompt = base_prompt
    
    # API call with enhanced prompt
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an expert in Qatari business markets and startup ecosystems."},
            {"role": "user", "content": enhanced_prompt}
        ],
        max_tokens=2000,  # Increased for detailed Qatar context
        temperature=0.7
    )
    
    # Enhanced cost tracking with QAR
    tokens_used = response.usage.total_tokens
    cost_usd = (tokens_used / 1000) * COST_PER_1K_TOKENS.get(MODEL, {}).get("usd", 0.015)
    cost_qar = cost_usd * USD_TO_QAR
    
    qatar_time = datetime.now(pytz.timezone('Asia/Qatar')).isoformat()
    
    return {
        "success": True,
        "content": response.choices[0].message.content,
        "tokens": tokens_used,
        "cost_usd": round(cost_usd, 4),
        "cost_qar": round(cost_qar, 2),
        "timestamp": qatar_time,
        "market_focus": "Qatar" if qatar_settings else "Global"
    }