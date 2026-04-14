#!/usr/bin/env python3
"""AMOS Extended Knowledge - Hidden/Legacy Engine Catalog.

This catalogs the ADDITIONAL 18+ engines in _AMOS_BRAIN/_LEGACY BRAIN/
that weren't in the main Cognitive directory.

Usage: python amos_extended_knowledge.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def get_legacy_brain_engines():
    """18 Additional engines in _LEGACY BRAIN/Unipower/"""
    return {
        # MASSIVE AI/Operations Engines (3.5 MB + 3 MB!)
        "AMOS_Uni_System_Operations_Engine_v0": {
            "size_kb": 3519,  # 3.5 MB!
            "domain": "System Operations",
            "location": "Unipower/",
            "type": "operations",
            "capabilities": ["system_ops", "infrastructure", "devops", "automation"]
        },
        "AMOS_Uni_Ai_Intelligence_Engine_v0": {
            "size_kb": 2986,  # 3 MB!
            "domain": "AI/Intelligence",
            "location": "Unipower/",
            "type": "ai_core",
            "capabilities": ["ai", "ml", "neural", "intelligence", "learning"]
        },
        
        # Tech Engine (180 KB)
        "AMOS_Tech_Engine_v0": {
            "size_kb": 180,
            "domain": "Technology",
            "location": "Unipower/",
            "type": "technology",
            "capabilities": ["tech_stack", "software", "hardware", "innovation"]
        },
        
        # Risk & Governance (55 KB)
        "AMOS_Risk_Policy_Governance_Ecosystem_Engine_v0": {
            "size_kb": 55,
            "domain": "Risk/Governance",
            "location": "Unipower/",
            "type": "governance",
            "capabilities": ["risk", "policy", "governance", "compliance"]
        },
        
        # Australia Economy (41 KB)
        "AMOS_Australia_Economy_Engine_v0": {
            "size_kb": 41,
            "domain": "Australia Economy",
            "location": "Unipower/",
            "type": "regional_econ",
            "capabilities": ["australia", "economy", "regional_analysis"]
        },
        
        # HSE Engine (391 KB text!)
        "HSE_Engine": {
            "size_kb": 391,
            "domain": "Health/Safety/Environment",
            "location": "Unipower/",
            "type": "hse",
            "file_type": "txt",
            "capabilities": ["health", "safety", "environment", "compliance"]
        },
        
        # Legal Ecosystems
        "AMOS_Chinese_Legal_Ecosystem_Engine_v0": {
            "size_kb": 21,
            "domain": "China Legal",
            "location": "Unipower/",
            "type": "legal_ecosystem",
            "capabilities": ["china", "legal", "ecosystem", "regulation"]
        },
        "AMOS_Vn_Omnistructure_Engine_v0": {
            "size_kb": 24,
            "domain": "Vietnam Omnistructure",
            "location": "Unipower/",
            "type": "legal_structure",
            "capabilities": ["vietnam", "omnistructure", "legal_framework"]
        },
        "AMOS_Chinese_Legal_Engine_v0": {
            "size_kb": 25,
            "domain": "China Legal",
            "location": "Unipower/",
            "type": "legal",
            "capabilities": ["china", "legal", "law"]
        },
        "VN_Legal_MAX": {
            "size_kb": 19,
            "domain": "Vietnam Legal MAX",
            "location": "Unipower/",
            "type": "legal_max",
            "capabilities": ["vietnam", "legal", "max_spec"]
        },
        "AMOS_Global_Legal_Engine_v0": {
            "size_kb": 7,
            "domain": "Global Legal",
            "location": "Unipower/",
            "type": "legal_global",
            "capabilities": ["global", "legal", "international_law"]
        },
        "AMOS_Vn_Legal_Engine_v0": {
            "size_kb": 14,
            "domain": "Vietnam Legal",
            "location": "Unipower/",
            "type": "legal",
            "capabilities": ["vietnam", "legal", "law"]
        },
        
        # Australia Specific
        "AMOS_Australia_Law_Incentives_Funding_Grants_Engine_v0": {
            "size_kb": 17,
            "domain": "Australia Funding",
            "location": "Unipower/",
            "type": "funding",
            "capabilities": ["australia", "funding", "grants", "incentives"]
        },
        "AMOS_Australia_Workforce_Engine_v0": {
            "size_kb": 16,
            "domain": "Australia Workforce",
            "location": "Unipower/",
            "type": "workforce",
            "capabilities": ["australia", "workforce", "labor"]
        },
        
        # Other Specialized
        "AMOS_Scientific_Engine_v0": {
            "size_kb": 24,
            "domain": "Scientific",
            "location": "Unipower/",
            "type": "scientific",
            "capabilities": ["science", "research", "methodology"]
        },
        "AMOS_Strategic_Document_Engine_v0": {
            "size_kb": 13,
            "domain": "Strategic Documents",
            "location": "Unipower/",
            "type": "documentation",
            "capabilities": ["strategy", "documents", "planning"]
        },
        "AMOS_Uni_Market_Engine_v0": {
            "size_kb": 15,
            "domain": "Market Analysis",
            "location": "Unipower/",
            "type": "market",
            "capabilities": ["market", "analysis", "economics"]
        },
        "AMOS_Bod_Engine_v0": {
            "size_kb": 14,
            "domain": "Board of Directors",
            "location": "Unipower/",
            "type": "governance",
            "capabilities": ["board", "directors", "governance"]
        },
        "AMOS_Ev_Kernel_v0": {
            "size_kb": 21,
            "domain": "EV/Electric Vehicles",
            "location": "Unipower/",
            "type": "ev",
            "capabilities": ["electric_vehicles", "mobility", "transport"]
        }
    }


def get_monogram_engines():
    """Monogram engines in Dsc/"""
    return {
        "AMOS_Monogram_Engine_v0": {
            "size_kb": 0,  # Unknown, need to check
            "domain": "Monogram",
            "location": "Dsc/",
            "type": "monogram",
            "capabilities": ["monogram", "identity", "signature"]
        },
        "AMOS_Monogram_Kernal_Engine_v0": {
            "size_kb": 0,
            "domain": "Monogram Kernel",
            "location": "Dsc/",
            "type": "kernel",
            "capabilities": ["kernel", "core", "monogram"]
        }
    }


def print_extended_knowledge():
    """Print the extended knowledge catalog."""
    legacy = get_legacy_brain_engines()
    monogram = get_monogram_engines()
    
    total_size = sum(e["size_kb"] for e in legacy.values())
    
    print("=" * 70)
    print("  🗂️  AMOS EXTENDED KNOWLEDGE")
    print("  Hidden/Legacy Brain Engines")
    print("=" * 70)
    
    print(f"\n  📍 Location: _AMOS_BRAIN/_LEGACY BRAIN/")
    print(f"  📦 Total Additional Engines: {len(legacy) + len(monogram)}")
    print(f"  💾 Total Size: {total_size:,} KB ({total_size/1024:.1f} MB)")
    
    # Group by size (largest first)
    print("\n  🔥 MASSIVE ENGINES (3MB+):")
    for name, info in sorted(legacy.items(), key=lambda x: -x[1]["size_kb"]):
        if info["size_kb"] > 1000:
            short = name.replace("AMOS_", "").replace("_Engine_v0", "").replace("_", " ")
            print(f"     • {short}")
            print(f"       Size: {info['size_kb']} KB | Domain: {info['domain']}")
    
    print("\n  📚 LARGE ENGINES (50-500 KB):")
    for name, info in sorted(legacy.items(), key=lambda x: -x[1]["size_kb"]):
        if 50 <= info["size_kb"] < 1000:
            short = name.replace("AMOS_", "").replace("_Engine_v0", "").replace("_", " ")
            print(f"     • {short} ({info['size_kb']} KB)")
    
    print("\n  📖 SPECIALIZED ENGINES (<50 KB):")
    count = 0
    for name, info in sorted(legacy.items(), key=lambda x: -x[1]["size_kb"]):
        if info["size_kb"] < 50:
            short = name.replace("AMOS_", "").replace("_Engine_v0", "").replace("_", " ")
            print(f"     • {short} ({info['size_kb']} KB)")
            count += 1
            if count >= 10:
                remaining = len([e for e in legacy.values() if e["size_kb"] < 50]) - 10
                if remaining > 0:
                    print(f"     ... and {remaining} more")
                break
    
    print("\n  🎨 MONOGRAM ENGINES:")
    for name, info in monogram.items():
        short = name.replace("AMOS_", "").replace("_Engine_v0", "").replace("_", " ")
        print(f"     • {short} (Dsc/)")
    
    # Categories
    print("\n  🏷️  BY DOMAIN:")
    domains = {}
    for info in legacy.values():
        domain = info["domain"]
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(info)
    
    for domain, engines in sorted(domains.items(), key=lambda x: -len(x[1]))[:8]:
        print(f"     • {domain}: {len(engines)} engines")
    
    print("\n" + "=" * 70)
    print(f"  🎯 TOTAL ADDITIONAL KNOWLEDGE: {len(legacy) + len(monogram)} engines")
    print(f"  💾 Total Size: {total_size:,} KB ({total_size/1024:.1f} MB)")
    print("=" * 70)
    
    # Compare to main cognitive engines
    main_kb = 328
    print(f"\n  📊 COMPARISON:")
    print(f"     Main Cognitive Engines: 13 engines, 328 KB")
    print(f"     Extended Legacy Engines: {len(legacy)} engines, {total_size:,} KB")
    print(f"     Ratio: Extended is {total_size/main_kb:.1f}x larger than main!")


if __name__ == "__main__":
    print_extended_knowledge()
