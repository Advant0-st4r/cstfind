"""
Qatar-specific validation utilities
"""

import re
from typing import Dict, List

class QatarMarketValidator:
    """Validate business ideas for Qatar market compatibility"""
    
    QATAR_PRIORITY_SECTORS = [
        "energy", "finance", "real estate", "tourism", "healthcare",
        "education", "technology", "logistics", "sports", "construction"
    ]
    
    QATAR_RESTRICTED_SECTORS = [
        "alcohol", "gambling", "pork", "adult entertainment"
    ]
    
    @staticmethod
    def validate_for_qatar(business_desc: str) -> Dict:
        """Validate business description for Qatar market suitability"""
        
        validation_results = {
            "is_suitable": True,
            "sector_alignment": [],
            "potential_issues": [],
            "recommendations": []
        }
        
        desc_lower = business_desc.lower()
        
        # Check sector alignment with Qatar priorities
        for sector in QatarMarketValidator.QATAR_PRIORITY_SECTORS:
            if sector in desc_lower:
                validation_results["sector_alignment"].append(sector.capitalize())
        
        # Check for restricted sectors
        for restricted in QatarMarketValidator.QATAR_RESTRICTED_SECTORS:
            if restricted in desc_lower:
                validation_results["is_suitable"] = False
                validation_results["potential_issues"].append(
                    f"Business involves {restricted}, which is restricted in Qatar"
                )
        
        # Check for cultural sensitivity
        cultural_keywords = ["blockchain", "crypto", "dating", "social media"]
        cultural_issues = []
        for keyword in cultural_keywords:
            if keyword in desc_lower:
                cultural_issues.append(keyword)
        
        if cultural_issues:
            validation_results["recommendations"].append(
                f"Exercise caution with: {', '.join(cultural_issues)}. "
                f"Ensure compliance with Qatar's cultural norms."
            )
        
        # Check for localization needs
        if not any(word in desc_lower for word in ["qatar", "doha", "gulf", "middle east", "arabic"]):
            validation_results["recommendations"].append(
                "Consider adding Qatar-specific value proposition for better local relevance"
            )
        
        return validation_results
    
    @staticmethod
    def generate_qatar_compliance_checklist(business_desc: str) -> List[str]:
        """Generate Qatar-specific compliance checklist"""
        
        checklist = [
            "✅ Business aligns with Qatar National Vision 2030 pillars",
            "✅ No involvement in restricted sectors (alcohol, gambling, etc.)",
            "✅ Respects Islamic business principles",
            "✅ Considers Qatar's legal framework (QFC, QFZA if applicable)",
            "✅ Plans for local partnership/representation",
            "✅ Arabic language support available",
            "✅ Understands Qatar's weekend (Friday-Saturday)",
            "✅ Considers local sponsorship requirements (if applicable)",
            "✅ Aligns with Qatar's digital transformation initiatives",
            "✅ Considers sustainability and environmental regulations"
        ]
        
        # Customize based on business description
        desc_lower = business_desc.lower()
        
        if "fintech" in desc_lower or "banking" in desc_lower:
            checklist.append("✅ Complies with Qatar Central Bank regulations")
        
        if "health" in desc_lower or "medical" in desc_lower:
            checklist.append("✅ Complies with Ministry of Public Health standards")
        
        return checklist