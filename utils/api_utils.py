import openai
import os
import yaml
from typing import Dict
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
COST_PER_1K_TOKENS = {"gpt-4o-mini": 0.015, "gpt-4o": 2.50}

def get_openai_client() -> openai.OpenAI:
    """Lazy initialization of OpenAI client with validation"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Check .env file.")
    if api_key.startswith("sk-your-key-here") or len(api_key) < 30:
        raise ValueError("OPENAI_API_KEY appears to be a placeholder or invalid. Update .env with valid key.")
    
    return openai.OpenAI(api_key=api_key)

def get_fallback_template() -> str:
    """Return a guaranteed working fallback template."""
    return (
        "You are an expert in market validation for startups. The user has a business: "
        "'{business_desc}'.\n"
        "Relevant specifications: {specs}.\n\n"
        "Generate a list of 10 potential corporate customers/partners for primary data gathering.\n"
        "For each, include:\n"
        "- Name (real company if possible)\n"
        "- Tier (1: Strategic Corporate Venture, 2: Value‑Add Corporation, 3: Angel Syndicate)\n"
        "- Why they're a fit\n"
        "- Suggested outreach subject line and initial message hook\n\n"
        "Output in markdown table format with columns: Name, Tier, Fit, Outreach, Message Hook."
    )

def load_prompt_template() -> str:
    """Load prompt from YAML for easy maintenance with robust error handling."""
    try:
        # Load the YAML configuration file
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not config:
            logger.error("YAML file is empty")
            return get_fallback_template()

        # Support both current and legacy YAML structures
        if "framework" in config:
            # New structure: principles & tiers are inside `framework`
            framework = config.get("framework", {})
            principles_list = framework.get("outreach_principles", [])
            tiers_list = framework.get("tiers", [])
        elif "outreach_principles" in config:
            # Legacy structure: they are top‑level keys
            principles_list = config.get("outreach_principles", [])
            tiers_list = config.get("tiers", [])
        else:
            logger.warning("YAML structure not recognized, using fallback")
            return get_fallback_template()

        # Build a readable summary of the framework data
        principles = (
            "\n".join(f"- {p}" for p in principles_list)
            if principles_list else "No principles defined"
        )
        tiers = (
            "\n".join(
                f"- {t.get('name', 'Unknown')}: {t.get('description', '')}"
                for t in tiers_list
            )
            if tiers_list else "No tiers defined"
        )
        framework_summary = f"Outreach Principles:\n{principles}\n\nTiers:\n{tiers}"

        # Retrieve the prompt template string
        template = config.get("prompt_template", "")
        if not template:
            logger.warning("No prompt_template found in YAML, using fallback")
            return get_fallback_template()

        # Insert the generated summary into the template
        return template.format(framework_summary=framework_summary)

    # Specific error handling – each returns the fallback template
    except FileNotFoundError:
        logger.error("config/prompts.yaml not found.")
        return get_fallback_template()
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        return get_fallback_template()
    except Exception as e:
        logger.error(f"Unexpected error loading YAML: {e}")
        return get_fallback_template()

def safe_generate_customer_list(business_desc: str, specs: str) -> Dict:
    """Safely generate customer list with error handling, cost tracking, and logging"""
    if not business_desc.strip():
        logger.warning("Empty business description provided.")
        return {"success": False, "error": "Business description cannot be empty."}
    
    try:
        # Lazy client initialization
        client = get_openai_client()
        
        prompt_template = load_prompt_template()
        prompt = prompt_template.format(business_desc=business_desc, specs=specs)
        
        logger.info(f"Generating customer list for business: {business_desc[:50]}...")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        
        tokens_used = response.usage.total_tokens
        cost_per_1k = COST_PER_1K_TOKENS.get(MODEL, 0.015)
        cost = (tokens_used / 1000) * cost_per_1k
        
        logger.info(f"Generation successful. Tokens: {tokens_used}, Cost: ${cost:.4f}")
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "tokens": tokens_used,
            "cost": round(cost, 4),
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return {"success": False, "error": str(e)}
    
    except openai.APIConnectionError as e:
        logger.error(f"Network error: {str(e)}")
        return {"success": False, "error": "Network connection error. Check your internet."}
    
    except openai.RateLimitError as e:
        logger.error(f"Rate limit exceeded: {str(e)}")
        return {"success": False, "error": "Rate limit exceeded. Please wait 20 seconds and try again."}
    
    except openai.AuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        return {"success": False, "error": "Invalid API key. Check your .env file."}
    
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"success": False, "error": f"OpenAI API error: {str(e)}"}
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"success": False, "error": f"Unexpected error: {str(e)}"}