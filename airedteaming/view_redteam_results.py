#!/usr/bin/env python3
"""
Script to display AI Red Team results in a readable format
"""
import json
import sys
from pathlib import Path
import glob

def find_latest_redteam_scan():
    """Find the latest red team scan directory"""
    redteam_base = Path(__file__).parent.parent / "redteam_outputs"
    
    if not redteam_base.exists():
        return None
    
    # Find all scan directories
    scan_dirs = list(redteam_base.glob(".scan_*"))
    if not scan_dirs:
        return None
    
    # Sort by modification time and return the latest
    latest_scan = sorted(scan_dirs, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    return latest_scan

def display_redteam_results(scan_dir=None):
    """Display red team results in a readable format"""
    
    if scan_dir is None:
        scan_dir = find_latest_redteam_scan()
    
    if scan_dir is None:
        print("❌ No red team scan results found.")
        print("Run the red team scan first with: python airedteaming/ai_redteaming.py")
        return
    
    results_file = scan_dir / "final_results.json"
    scorecard_file = scan_dir / "scorecard.txt"
    
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        return
    
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        print("=" * 80)
        print("🛡️  AI RED TEAM SECURITY SCAN RESULTS")
        print("=" * 80)
        
        # Display scan info
        print(f"\n📂 Scan Directory: {scan_dir.name}")
        print(f"📊 Scan Date: {scan_dir.name.split('_')[-2]}")
        print(f"🕐 Scan Time: {scan_dir.name.split('_')[-1]}")
        
        # Display overall results
        scorecard = data.get('scorecard', {})
        risk_summary = scorecard.get('risk_category_summary', [])
        
        if risk_summary:
            overall_stats = risk_summary[0]
            asr = overall_stats.get('overall_asr', 0) * 100
            total_attacks = overall_stats.get('overall_total', 0)
            successful_attacks = overall_stats.get('overall_attack_successes', 0)
            
            print(f"\n🎯 OVERALL SECURITY ASSESSMENT:")
            print("-" * 40)
            print(f"  • Attack Success Rate (ASR): {asr:.1f}%")
            print(f"  • Total Attacks Attempted: {total_attacks}")
            print(f"  • Successful Attacks: {successful_attacks}")
            print(f"  • Security Status: {'🚨 VULNERABLE' if asr > 0 else '✅ SECURE'}")
        
        # Display attack parameters
        parameters = data.get('parameters', {})
        risk_categories = parameters.get('attack_objective_generated_from', {}).get('risk_categories', [])
        attack_complexity = parameters.get('attack_complexity', [])
        
        print(f"\n🔍 SCAN CONFIGURATION:")
        print("-" * 40)
        print(f"  • Risk Categories Tested: {', '.join(risk_categories).title()}")
        print(f"  • Attack Complexity Levels: {', '.join(attack_complexity).title()}")
        
        # Display attack details
        attack_details = data.get('attack_details', [])
        if attack_details:
            print(f"\n⚔️  ATTACK DETAILS:")
            print("-" * 40)
            
            for i, attack in enumerate(attack_details, 1):
                technique = attack.get('attack_technique', 'Unknown')
                complexity = attack.get('attack_complexity', 'Unknown')
                risk_category = attack.get('risk_category', 'Unknown')
                success = attack.get('attack_success')
                
                print(f"\n🔍 Attack {i}:")
                print(f"  • Technique: {technique.title()}")
                print(f"  • Complexity: {complexity.title()}")
                print(f"  • Risk Category: {risk_category.title()}")
                print(f"  • Success: {'❌ Failed' if success is None or not success else '✅ Succeeded'}")
                
                # Show conversation excerpt
                conversation = attack.get('conversation', [])
                if conversation:
                    user_prompt = conversation[0].get('content', '')[:100] + '...' if len(conversation[0].get('content', '')) > 100 else conversation[0].get('content', '')
                    agent_response = conversation[1].get('content', '') if len(conversation) > 1 else 'No response'
                    
                    print(f"  • Attack Prompt: {user_prompt}")
                    print(f"  • Agent Response: {agent_response}")
        
        # Display assessment summary
        if scorecard_file.exists():
            print(f"\n📈 RISK ASSESSMENT MATRIX:")
            print("-" * 40)
            try:
                with open(scorecard_file, 'r') as f:
                    scorecard_content = f.read().strip()
                    lines = scorecard_content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('-'):
                            print(f"  {line}")
            except Exception as e:
                print(f"  Could not read scorecard: {e}")
        
        # Show Azure AI Foundry link
        studio_url = data.get('studio_url')
        if studio_url:
            print(f"\n🔗 DETAILED ANALYSIS:")
            print("-" * 40)
            print(f"  • Azure AI Foundry: {studio_url}")
        
        print(f"\n📁 LOCAL RESULTS:")
        print("-" * 40)
        print(f"  • Full Results: {results_file}")
        print(f"  • Scan Directory: {scan_dir}")
        
        # Security recommendations
        print(f"\n💡 SECURITY RECOMMENDATIONS:")
        print("-" * 40)
        if asr == 0:
            print("  ✅ Your agent successfully defended against all attack attempts")
            print("  ✅ No harmful content was generated")
            print("  ✅ Safety mechanisms are working effectively")
            print("  💡 Continue monitoring with regular red team scans")
        else:
            print("  🚨 Your agent showed vulnerabilities to adversarial attacks")
            print("  🚨 Review and strengthen safety guardrails")
            print("  🚨 Consider additional content filtering")
            print("  💡 Implement additional safety measures before production")
        
        print("\n" + "=" * 80)
        print("🛡️  Red Team Security Scan Analysis Complete!")
        print("=" * 80)
        
    except FileNotFoundError:
        print(f"❌ Error: Results file '{results_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in results file '{results_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Allow specifying a specific scan directory
    scan_dir = None
    if len(sys.argv) > 1:
        scan_dir = Path(sys.argv[1])
        if not scan_dir.exists():
            print(f"❌ Scan directory not found: {scan_dir}")
            sys.exit(1)
    
    display_redteam_results(scan_dir)
