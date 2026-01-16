import yaml
import sys

def validate_prompts_yaml():
    try:
        with open("config/prompts.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        print("✅ YAML loaded successfully")
        
        # Check structure
        if "framework" not in config:
            print("❌ Missing 'framework' key at top level")
            return False
        
        framework = config["framework"]
        
        if "tiers" not in framework:
            print("❌ Missing 'tiers' key in framework")
            return False
        
        if "outreach_principles" not in framework:
            print("❌ Missing 'outreach_principles' key in framework")
            return False
        
        if "prompt_template" not in config:
            print("❌ Missing 'prompt_template' key at top level")
            return False
        
        print(f"✅ Found {len(framework['tiers'])} tiers")
        print(f"✅ Found {len(framework['outreach_principles'])} outreach principles")
        print(f"✅ Prompt template length: {len(config['prompt_template'])} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    if validate_prompts_yaml():
        sys.exit(0)
    else:
        sys.exit(1)