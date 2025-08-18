#!/usr/bin/env python3
"""
Script to display evaluation results in a readable format
"""
import json
import sys
from pathlib import Path

def display_evaluation_results(results_file):
    """Display evaluation results in a readable format"""
    
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        print("=" * 80)
        print("AGENT EVALUATION RESULTS SUMMARY")
        print("=" * 80)
        
        # Display overall metrics
        if 'metrics' in data:
            print("\n📊 OVERALL METRICS:")
            print("-" * 40)
            metrics = data['metrics']
            
            # Group metrics by category
            operational = {k: v for k, v in metrics.items() if k.startswith('operational_metrics')}
            tool_call = {k: v for k, v in metrics.items() if k.startswith('tool_call_accuracy')}
            intent = {k: v for k, v in metrics.items() if k.startswith('intent_resolution')}
            task = {k: v for k, v in metrics.items() if k.startswith('task_adherence')}
            
            print(f"\n🔧 Operational Metrics:")
            for key, value in operational.items():
                metric_name = key.replace('operational_metrics.', '').replace('-', ' ').title()
                if 'tokens' in key:
                    print(f"  • {metric_name}: {value:.0f}")
                elif 'duration' in key:
                    print(f"  • {metric_name}: {value:.2f}s")
                else:
                    print(f"  • {metric_name}: {value}")
            
            print(f"\n🎯 Tool Call Accuracy:")
            for key, value in tool_call.items():
                metric_name = key.replace('tool_call_accuracy.', '').replace('_', ' ').title()
                if 'binary' in key:
                    print(f"  • Success Rate: {value*100:.0f}%")
                elif 'threshold' in key:
                    print(f"  • Threshold: {value}")
            
            print(f"\n💭 Intent Resolution:")
            for key, value in intent.items():
                metric_name = key.replace('intent_resolution.', '').replace('_', ' ').title()
                if 'binary' in key:
                    print(f"  • Success Rate: {value*100:.0f}%")
                elif key.endswith('intent_resolution'):
                    print(f"  • Average Score: {value}/5")
                elif 'threshold' in key:
                    print(f"  • Threshold: {value}")
            
            print(f"\n✅ Task Adherence:")
            for key, value in task.items():
                metric_name = key.replace('task_adherence.', '').replace('_', ' ').title()
                if 'binary' in key:
                    print(f"  • Success Rate: {value*100:.0f}%")
                elif key.endswith('task_adherence'):
                    print(f"  • Average Score: {value}/5")
                elif 'threshold' in key:
                    print(f"  • Threshold: {value}")
        
        # Display individual test results
        if 'rows' in data:
            print(f"\n📝 INDIVIDUAL TEST RESULTS:")
            print("-" * 40)
            
            for i, row in enumerate(data['rows'], 1):
                # Extract query
                query_content = ""
                if 'inputs.query' in row and row['inputs.query']:
                    for msg in row['inputs.query']:
                        if msg.get('role') == 'user' and 'content' in msg:
                            if isinstance(msg['content'], list):
                                query_content = msg['content'][0].get('text', '')
                            else:
                                query_content = msg['content']
                
                print(f"\n🔍 Test {i}: {query_content}")
                
                # Extract response
                response_content = ""
                if 'inputs.response' in row and row['inputs.response']:
                    for msg in row['inputs.response']:
                        if msg.get('role') == 'assistant' and 'content' in msg:
                            for content_item in msg['content']:
                                if content_item.get('type') == 'text':
                                    response_content = content_item.get('text', '')
                
                print(f"📋 Response: {response_content}")
                
                # Extract evaluation scores
                evaluations = {}
                for key, value in row.items():
                    if key.startswith('outputs.') and not key.endswith('_reason') and not key.endswith('_result') and not key.endswith('_threshold') and not key.endswith('.details'):
                        eval_type = key.split('.')[1]
                        metric = key.split('.')[-1]
                        
                        if eval_type not in evaluations:
                            evaluations[eval_type] = {}
                        evaluations[eval_type][metric] = value
                
                print("📊 Evaluation Scores:")
                for eval_type, metrics in evaluations.items():
                    print(f"  • {eval_type.replace('_', ' ').title()}:")
                    for metric, value in metrics.items():
                        if metric in ['intent_resolution', 'task_adherence'] and isinstance(value, (int, float)):
                            print(f"    - {metric.replace('_', ' ').title()}: {value}/5")
                        elif metric == 'tool_call_accuracy':
                            if value == "not applicable":
                                print(f"    - Tool Call Accuracy: N/A")
                            else:
                                print(f"    - Tool Call Accuracy: {value}")
                        elif not metric.endswith('threshold'):
                            print(f"    - {metric.replace('_', ' ').title()}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ Evaluation completed successfully!")
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
    # Default to the standard output file
    results_file = Path(__file__).parent / "eval-output.json"
    
    if len(sys.argv) > 1:
        results_file = Path(sys.argv[1])
    
    display_evaluation_results(results_file)
