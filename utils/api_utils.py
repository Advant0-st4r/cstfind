"""
OpenAI API utilities with robust error handling and Qatar-specific enhancements
"""

import openai
import os
import yaml
from typing import Dict, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('customer_finder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
COST_PER_1K_TOKENS = {
    "gpt-4o-mini": {"usd": 0.015, "qar": 0.055},
    "gpt-4o": {"usd": 2.50, "qar": 9.10}
}
USD_TO_QAR = 3.64  # Current exchange rate

def get_openai_client() -> openai.OpenAI:
    """
    Lazy initialization of OpenAI client with comprehensive validation
    
    Returns:
        openai.OpenAI: Configured client instance
        
    Raises:
        ValueError: If API key is missing or invalid
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Check .env file.")
    
    if api_key.startswith("sk-your-key") or len(api_key) < 30:
        raise ValueError("OPENAI_API_KEY appears to be a placeholder or invalid. Update .env with a valid key.")
    
    # Configure client with timeout settings
    return openai.OpenAI(
        api_key=api_key,
        timeout=30.0,  # 30 second timeout
        max_retries=3
    )

def get_fallback_template() -> str:
    """
    Guaranteed working fallback template for when YAML loading fails
    
    Returns:
        str: Complete prompt template
    """
    return """You are an expert in market validation for startups, specifically in the Qatari and Gulf region markets.

The user has a business: '{business_desc}'
Relevant specifications: {specs}

Generate a list of 10 potential corporate customers, partners, or investors for market validation.
For each entity, provide:
1. **Name**: Real company, corporate venture arm, or investment entity
2. **Tier**: 1 (Strategic), 2 (Value-Add), or 3 (Angel/Investor)
3. **Fit**: Specific reasons why this entity would be interested
4. **Outreach Subject**: Professional, attention-grabbing subject line
5. **Message Hook**: First 1-2 sentences to open dialogue

Output in a clean markdown table format with clear columns.

Prioritize entities with active innovation programs or startup engagement history."""

def load_prompt_template() -> Tuple[str, str]:
    """
    Load prompt template from YAML with robust error handling
    
    Returns:
        Tuple[str, str]: (template_string, framework_summary)
    """
    try:
        # Load YAML configuration
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        if not config:
            logger.warning("YAML configuration file is empty")
            return get_fallback_template(), ""
        
        # Extract framework data with defensive access
        framework = config.get("framework", {})
        
        # Extract principles
        principles_list = framework.get("outreach_principles", [])
        principles = "\n".join([f"- {p}" for p in principles_list]) if principles_list else ""
        
        # Extract tiers
        tiers_list = framework.get("tiers", [])
        tiers = "\n".join([f"- {t.get('name', '')}: {t.get('description', '')}" 
                          for t in tiers_list]) if tiers_list else ""
        
        # Build framework summary
        framework_summary = ""
        if principles:
            framework_summary += f"Outreach Principles:\n{principles}\n\n"
        if tiers:
            framework_summary += f"Target Tiers:\n{tiers}"
        
        # Extract template
        template = config.get("prompt_template", "").strip()
        if not template:
            logger.warning("prompt_template is empty in YAML")
            return get_fallback_template(), framework_summary
        
        # Validate template has required placeholders
        required_placeholders = {"{business_desc}", "{specs}", "{framework_summary}"}
        if not all(ph in template for ph in required_placeholders):
            logger.warning("Template missing required placeholders")
            return get_fallback_template(), framework_summary
        
        return template, framework_summary
        
    except FileNotFoundError:
        logger.error("prompts.yaml not found in config/ directory")
        return get_fallback_template(), ""
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {str(e)}")
        return get_fallback_template(), ""
    except Exception as e:
        logger.error(f"Unexpected error loading YAML: {str(e)}")
        return get_fallback_template(), ""

def enhance_for_qatar_context(prompt: str, align_qnv2030: bool) -> str:
    """
    Enhance the prompt with Qatar-specific context
    
    Args:
        prompt: Original prompt
        align_qnv2030: Whether to align with Qatar National Vision 2030
        
    Returns:
        Enhanced prompt with Qatar context
    """
    qatar_context = "\n\n**Qatar Market Context:**\n"
    
    # Add QNV 2030 alignment if requested
    if align_qnv2030:
        qatar_context += """- **Qatar National Vision 2030 Alignment Required**
- Focus on entities contributing to Qatar's economic diversification
- Prioritize companies involved in Qatar's knowledge economy development
- Consider organizations participating in Qatar Foundation, QSTP, or Msheireb initiatives
- Include references to sustainability and environmental development where applicable

"""
    
    # Always include basic Qatar context
    qatar_context += """- **Market Specifics**: Doha-based or active in Qatar market
- **Business Culture**: Relationship-focused, hierarchical, formal initial contact preferred
- **Key Sectors**: Energy, Finance, Real Estate, Tourism, Technology, Logistics
- **Language**: English for international business, Arabic for local relationships
- **Regulatory**: Consider QFC, QFZA, or Ministry of Commerce requirements
- **Timing**: Business week is Sunday-Thursday, consider Ramadan timing
"""
    
    return prompt + qatar_context

def safe_generate_customer_list(business_desc: str, specs: str, align_qnv2030: bool = True) -> Dict:
    """
    Main function to generate customer list with comprehensive error handling
    
    Args:
        business_desc: Business description from user
        specs: Additional specifications
        align_qnv2030: Whether to align with Qatar National Vision 2030
        
    Returns:
        Dict with success status, content, and metadata
    """
    # Input validation
    if not business_desc.strip():
        logger.warning("Empty business description provided")
        return {
            "success": False, 
            "error": "Business description cannot be empty. Please describe your business.",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Initialize OpenAI client
        client = get_openai_client()
        
        # Load and prepare prompt
        template, framework_summary = load_prompt_template()
        
        # Format the base prompt
        base_prompt = template.format(
            business_desc=business_desc,
            specs=specs,
            framework_summary=framework_summary
        )
        
        # Enhance with Qatar context if requested
        if align_qnv2030 or "Qatar" in business_desc or "Doha" in business_desc:
            final_prompt = enhance_for_qatar_context(base_prompt, align_qnv2030)
            qatar_focus = True
        else:
            final_prompt = base_prompt
            qatar_focus = False
        
        logger.info(f"Generating list for: {business_desc[:60]}...")
        logger.debug(f"Prompt length: {len(final_prompt)} characters")
        
        # Make API call with model-appropriate parameters
        # Note: Using max_completion_tokens instead of max_tokens for newer models
        # Note: temperature removed as some newer models only support default (1)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a market validation expert specializing in corporate partnerships and startup ecosystems."
                },
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            max_completion_tokens=1500
        )
        
        # Calculate costs
        tokens_used = response.usage.total_tokens
        model_costs = COST_PER_1K_TOKENS.get(MODEL, {"usd": 0.015, "qar": 0.055})
        cost_usd = (tokens_used / 1000) * model_costs["usd"]
        cost_qar = cost_usd * USD_TO_QAR
        
        logger.info(f"Success! Tokens: {tokens_used}, Cost: ${cost_usd:.4f} USD ({cost_qar:.2f} QAR)")
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "tokens": tokens_used,
            "cost_usd": round(cost_usd, 4),
            "cost_qar": round(cost_qar, 2),
            "timestamp": datetime.now().isoformat(),
            "qatar_focus": qatar_focus,
            "model": MODEL
        }
        
    except ValueError as e:
        # Configuration errors
        logger.error(f"Configuration error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {str(e)}",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    except openai.AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": "Authentication failed. Check your OpenAI API key in the .env file.",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    except openai.RateLimitError as e:
        logger.error(f"Rate limit exceeded: {str(e)}")
        return {
            "success": False,
            "error": "Rate limit exceeded. Please wait 20-30 seconds and try again.",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    except openai.APIConnectionError as e:
        logger.error(f"Network connection error: {str(e)}")
        return {
            "success": False,
            "error": "Network connection failed. Check your internet connection.",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {
            "success": False,
            "error": f"OpenAI API error: {str(e)}",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "tokens": 0,
            "cost_usd": 0.0,
            "cost_qar": 0.0,
            "timestamp": datetime.now().isoformat()
        }