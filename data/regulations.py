from typing import Dict

REGULATIONS: Dict[str, Dict] = {
    "REG_2026_PR_COMPLIANCE": {
        "id": "REG_2026_PR_COMPLIANCE",
        "title": "PR Compliance Pre-Approval",
        "mandate": "To mitigate insider trading and reputational risk, all external public communications, social media updates, or technical publications regarding active company projects must receive explicit, documented pre-approval from the PR Compliance Committee prior to publication."
    },
    "REG_2026_SEC_VENDOR": {
            "id": "REG_2026_SEC_VENDOR",
            "title": "Vendor Security Scanning",
            "mandate": "All external software vendors, micro-services, and digital tools interacting with company data—regardless of contract value or tier—must undergo a mandatory automated security scanning and static analysis review by the central InfoSec team."
    }
}