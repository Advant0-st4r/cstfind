"""
CustomerFinder MVP - Generate targeted customer lists for market validation
"""

import os
import sys
from datetime import datetime
from utils.api_utils import safe_generate_customer_list

def validate_content_structure(content: str) -> bool:
    """Check if content has expected table structure"""
    if not content:
        return False
    
    # Check for markdown table indicators
    lines = content.strip().split('\n')
    table_lines = [line for line in lines if '|' in line and '---' not in line]
    
    # Should have at least 5 table rows (header + 4 data rows)
    if len(table_lines) < 5:
        return False
    
    return True

def main():
    # Example business description
    business_desc = """
    B2B SaaS PaaS that enables companies to input routine operational data 
    (e.g., maintenance logs, inventory updates, compliance checks) and get 
    AI-powered insights on efficiency, anomalies, and optimization opportunities.
    """
    
    # Additional specifications
    specs = """
    - Target: Mid to large enterprises in Qatar
    - Key features: Automated data ingestion, real-time dashboards, predictive alerts
    - Integration: API-based, mobile-friendly, multi-language support
    - Compliance: GDPR, Qatari data protection regulations
    """
    
    print("Generating customer list...")
    result = safe_generate_customer_list(business_desc, specs, align_qnv2030=True)
    
    if result['success']:
        # === CRITICAL FIX: Double-check content before writing ===
        content = result['content']
        
        if not content:
            print("ERROR: Generated content is empty!")
            sys.exit(1)
        
        if not validate_content_structure(content):
            print("WARNING: Content may not have proper table format")
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"output/customer_list_{timestamp}.md"
        
        # Write to file with comprehensive header
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"# CustomerFinder MVP Results\n")
                f.write(f"## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"## Market Focus: Qatar\n")
                f.write(f"## Business: {business_desc[:100]}...\n\n")
                
                # Content
                f.write("## Generated List\n\n")
                f.write(content)
                
                # Footer with metadata
                f.write(f"\n\n---\n")
                f.write(f"**Metadata:**\n")
                f.write(f"- Tokens used: {result['tokens']}\n")
                f.write(f"- Cost: ${result['cost_usd']} USD ({result['cost_qar']} QAR)\n")
                f.write(f"- Model: {result.get('model', 'N/A')}\n")
                f.write(f"- Qatar Focus: {result.get('qatar_focus', 'N/A')}\n")
            
            print(f"✅ Successfully generated: {filename}")
            print(f"📊 Tokens used: {result['tokens']}, Cost: ${result['cost_usd']} USD ({result['cost_qar']} QAR)")
            
            # Also create a symlink for easy access
            try:
                if os.path.exists("list1.md"):
                    os.remove("list1.md")
                os.symlink(filename, "list1.md")
                print(f"🔗 Symlink created: list1.md → {filename}")
            except:
                print("⚠️  Could not create symlink (Windows may not support)")
                
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            sys.exit(1)
            
    else:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()