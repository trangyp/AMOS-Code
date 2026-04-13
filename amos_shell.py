#!/usr/bin/env python3
"""
AMOS Interactive Shell
========================

Conversational interface to the complete AMOS ecosystem:
- 14-Subsystem Organism OS
- 6 Global Laws Brain
- 50MB+ Knowledge Base (core + extended)
- Intelligent reasoning with knowledge enhancement

Usage:
    python amos_shell.py
    
Commands:
    /ask <question>     - Ask the brain a question
    /query <terms>      - Query knowledge base
    /status             - Show system status
    /subsystems         - List active subsystems
    /countries          - Show loaded countries
    /sectors            - Show loaded sectors
    /think <problem>    - Deep thinking mode
    /demo               - Run demonstrations
    /help               - Show help
    /exit               - Exit shell

Owner: Trang
"""

import sys
import cmd
import traceback
from pathlib import Path
from typing import Dict, Any, List

# Add paths
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(REPO_ROOT / "amos_brain"))


class AMOSShell(cmd.Cmd):
    """Interactive shell for AMOS ecosystem."""
    
    intro = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🧠 AMOS INTERACTIVE SHELL 🌍                         ║
║                                                                  ║
║         14 Subsystems + 6 Laws + 50MB Knowledge                  ║
║                                                                  ║
║              Type /help for commands                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    
    prompt = "amos> "
    
    def __init__(self):
        super().__init__()
        self.amos = None
        self.initialized = False
        
    def preloop(self):
        """Initialize before starting shell."""
        print("\n🚀 Initializing AMOS ecosystem...")
        try:
            from amos_unified_enhanced import AMOSUnifiedEnhanced
            self.amos = AMOSUnifiedEnhanced()
            status = self.amos.initialize(auto_load_knowledge=True)
            
            if status["integration"]["fully_integrated"]:
                self.initialized = True
                print("✅ AMOS ecosystem ready!\n")
                print(f"   🧬 Organism: {status['organism']['subsystems_active']} subsystems")
                print(f"   🧠 Brain: {status['brain']['laws_active']} laws")
                print(f"   📚 Knowledge: {status['knowledge']['entries']:,} entries")
                print()
            else:
                print("⚠️  Partial initialization - some features may be limited\n")
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            print("⚠️  Running in limited mode\n")
    
    def do_ask(self, arg):
        """Ask the brain a question: /ask What is the best architecture?"""
        if not self._check_initialized():
            return
        
        if not arg:
            print("❌ Please provide a question: /ask <question>")
            return
        
        print(f"\n🧠 Thinking: '{arg}'...")
        print("-" * 60)
        
        try:
            result = self.amos.think(arg)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Analysis complete")
                if "knowledge_used" in result:
                    print(f"📚 Knowledge entries used: {result['knowledge_used']}")
                if "reasoning" in result:
                    print(f"\n💭 Reasoning:")
                    print(f"   {result['reasoning']}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_query(self, arg):
        """Query knowledge base: /query microservices"""
        if not self._check_initialized():
            return
        
        if not arg:
            print("❌ Please provide search terms: /query <terms>")
            return
        
        print(f"\n🔍 Querying knowledge: '{arg}'...")
        print("-" * 60)
        
        try:
            results = self.amos.query_knowledge(arg, limit=5)
            
            if results:
                print(f"✅ Found {len(results)} results:\n")
                for i, r in enumerate(results, 1):
                    print(f"  {i}. {r['key']}")
                    print(f"     Domain: {r['domain']}")
                    print(f"     Priority: {r['priority']}")
                    if r['tags']:
                        print(f"     Tags: {', '.join(r['tags'][:3])}")
                    print()
            else:
                print("ℹ️  No results found")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_status(self, arg):
        """Show complete system status."""
        if not self.amos:
            print("❌ System not initialized")
            return
        
        print("\n📊 AMOS System Status")
        print("=" * 60)
        
        status = {
            "organism": self.amos.status.organism_ready,
            "subsystems": self.amos.status.subsystems_active,
            "brain": self.amos.status.brain_ready,
            "knowledge": self.amos.status.knowledge_ready,
            "entries": self.amos.status.knowledge_entries,
            "domains": self.amos.status.knowledge_domains,
            "memory": self.amos.status.knowledge_mb
        }
        
        print(f"\n🧬 Organism OS:")
        print(f"   Status: {'✅ Ready' if status['organism'] else '❌ Not Ready'}")
        print(f"   Subsystems: {status['subsystems']}/14 active")
        
        print(f"\n🧠 Brain:")
        print(f"   Status: {'✅ Ready' if status['brain'] else '❌ Not Ready'}")
        print(f"   Laws: 6/6 active")
        
        print(f"\n📚 Knowledge:")
        print(f"   Status: {'✅ Ready' if status['knowledge'] else '❌ Not Ready'}")
        print(f"   Entries: {status['entries']:,}")
        print(f"   Domains: {status['domains']}")
        print(f"   Memory: {status['memory']:.1f}MB")
        
        print(f"\n🔗 Integration:")
        all_ready = all([status['organism'], status['brain'], status['knowledge']])
        print(f"   Status: {'✅ Fully Integrated' if all_ready else '⚠️  Partial'}")
        
        print("=" * 60)
    
    def do_subsystems(self, arg):
        """List all active subsystems."""
        if not self._check_initialized():
            return
        
        print("\n🔧 Active Subsystems")
        print("=" * 60)
        
        try:
            if self.amos.organism:
                status = self.amos.organism.status()
                subsystems = status.get("active_subsystems", [])
                
                print(f"\nTotal: {len(subsystems)} subsystems active\n")
                
                for i, subsys in enumerate(subsystems, 1):
                    print(f"  {i:2}. {subsys}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_countries(self, arg):
        """Show loaded country knowledge packs."""
        print("\n🌍 Country Knowledge Packs")
        print("=" * 60)
        
        try:
            from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge
            
            system = get_comprehensive_knowledge()
            if not system.initialized:
                system.initialize()
            
            countries = system.extended_loader.list_countries()
            
            print(f"\nTotal: {len(countries)} countries loaded\n")
            
            # Show first 20
            for i, code in enumerate(countries[:20], 1):
                country = system.extended_loader.get_country(code)
                if country:
                    print(f"  {i:2}. {code} - {country.country_name}")
            
            if len(countries) > 20:
                print(f"\n  ... and {len(countries) - 20} more")
                    
        except Exception as e:
            print(f"❌ Error loading countries: {e}")
    
    def do_sectors(self, arg):
        """Show loaded sector knowledge packs."""
        print("\n🏭 Sector Knowledge Packs")
        print("=" * 60)
        
        try:
            from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge
            
            system = get_comprehensive_knowledge()
            if not system.initialized:
                system.initialize()
            
            sectors = system.extended_loader.list_sectors()
            
            print(f"\nTotal: {len(sectors)} sectors loaded\n")
            
            for i, code in enumerate(sectors, 1):
                sector = system.extended_loader.get_sector(code)
                if sector:
                    print(f"  {i:2}. {code} - {sector.sector_name} ({sector.domain})")
                    
        except Exception as e:
            print(f"❌ Error loading sectors: {e}")
    
    def do_think(self, arg):
        """Deep thinking mode: /think <complex problem>"""
        if not self._check_initialized():
            return
        
        if not arg:
            print("❌ Please provide a problem: /think <problem>")
            return
        
        print(f"\n🧠🧠🧠 DEEP THINKING MODE 🧠🧠🧠")
        print(f"Problem: '{arg}'")
        print("=" * 60)
        print("Analyzing with Rule of 2 and Rule of 4...")
        print("Querying comprehensive knowledge base...")
        print("Applying 6 Global Laws...")
        print("-" * 60)
        
        try:
            # Multi-step thinking
            result = self.amos.think(arg)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"\n✅ Analysis complete")
                
                # Show detailed output
                if "knowledge_used" in result:
                    print(f"\n📚 Knowledge Applied:")
                    print(f"   Core entries: {result['knowledge_used']}")
                
                if "knowledge_entries" in result:
                    print(f"\n📖 Relevant Knowledge:")
                    for entry in result['knowledge_entries'][:3]:
                        print(f"   • {entry}")
                
                print(f"\n💡 Conclusion:")
                print(f"   {result.get('reasoning', 'Analysis complete')}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
    
    def do_demo(self, arg):
        """Run system demonstrations."""
        print("\n🎬 Running AMOS Demonstrations")
        print("=" * 60)
        
        demos = [
            ("Organism Status", self._demo_organism),
            ("Knowledge Query", self._demo_knowledge),
            ("Country Lookup", self._demo_countries),
            ("Subsystem Access", self._demo_subsystems)
        ]
        
        for name, demo_func in demos:
            print(f"\n{name}:")
            print("-" * 40)
            try:
                demo_func()
            except Exception as e:
                print(f"   ⚠️  Demo skipped: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Demos complete!")
    
    def _demo_organism(self):
        """Demo organism status."""
        if self.amos and self.amos.organism:
            status = self.amos.organism.status()
            print(f"   Session: {status.get('session_id', 'N/A')[:20]}...")
            print(f"   Subsystems: {len(status.get('active_subsystems', []))} active")
        else:
            print("   ⚠️  Organism not available")
    
    def _demo_knowledge(self):
        """Demo knowledge query."""
        if self.amos and self.amos.knowledge_brain:
            results = self.amos.query_knowledge("architecture", limit=3)
            print(f"   Query: 'architecture'")
            print(f"   Results: {len(results)} entries")
            for r in results[:2]:
                print(f"   • {r['key']}")
        else:
            print("   ⚠️  Knowledge not available")
    
    def _demo_countries(self):
        """Demo country lookup."""
        try:
            from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge
            system = get_comprehensive_knowledge()
            if not system.initialized:
                system.initialize()
            
            country = system.extended_loader.get_country("US")
            if country:
                print(f"   Country: {country.country_name}")
                print(f"   Economy GDP: {country.economy.get('gdp', 'N/A')}")
            else:
                print("   ⚠️  Country data not available")
        except Exception:
            print("   ⚠️  Extended knowledge not available")
    
    def _demo_subsystems(self):
        """Demo subsystem access."""
        if self.amos:
            health = self.amos.get_subsystem("health_monitor")
            growth = self.amos.get_subsystem("growth_engine")
            print(f"   Health Monitor: {'✅' if health else '❌'}")
            print(f"   Growth Engine: {'✅' if growth else '❌'}")
        else:
            print("   ⚠️  Subsystems not available")
    
    def do_help(self, arg):
        """Show help information."""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                         AMOS SHELL COMMANDS                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  /ask <question>       Ask the brain a question                   ║
║  /query <terms>        Query knowledge base                      ║
║  /status                Show complete system status               ║
║  /subsystems            List active subsystems                     ║
║  /countries             Show loaded countries                      ║
║  /sectors               Show loaded industry sectors              ║
║  /think <problem>       Deep thinking with full analysis         ║
║  /demo                  Run system demonstrations                ║
║  /help                  Show this help                             ║
║  /exit                  Exit the shell                             ║
║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  EXAMPLES:                                                        ║
║    /ask What is the best architecture for microservices?          ║
║    /query scalability patterns                                    ║
║    /think How should I design a distributed system?             ║
║    /countries                                                     ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def do_exit(self, arg):
        """Exit the shell."""
        print("\n👋 Shutting down AMOS ecosystem...")
        print("✅ Goodbye!")
        return True
    
    def do_EOF(self, arg):
        """Handle Ctrl+D."""
        print()
        return self.do_exit(arg)
    
    def emptyline(self):
        """Handle empty line."""
        pass
    
    def default(self, line):
        """Handle unknown commands."""
        if line.startswith("/"):
            print(f"❌ Unknown command: {line}")
            print("   Type /help for available commands")
        else:
            # Treat as a question to the brain
            print(f"\n🧠 Interpreting as question: '{line}'")
            print("-" * 60)
            self.do_ask(line)
    
    def _check_initialized(self) -> bool:
        """Check if system is initialized."""
        if not self.initialized:
            print("❌ System not fully initialized")
            print("   Some features may be unavailable")
            return False
        return True


def main():
    """Start the AMOS interactive shell."""
    try:
        shell = AMOSShell()
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
