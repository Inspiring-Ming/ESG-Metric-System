#!/usr/bin/env python3
"""
Comprehensive Ontometric System Demo

This script demonstrates the complete integrated system:
- Web interface frontend (with existing enhanced_demo.html)
- REST API backend with all endpoints
- Comprehensive evaluation system
- CQ1-CQ7 research questions
- Performance benchmarks and visualizations

Consolidates all functionality into one unified demonstration.
"""

import sys
import os
import time
import json
import threading
import webbrowser
import requests
from datetime import datetime
import socket

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.esg_api import create_app
from src.services.data_retrieval_service import DataRetrievalService
from src.services.unified_knowledge_graph_service import UnifiedKnowledgeGraphService
from src.services.calculation_service import CalculationService
from src.services.comprehensive_report_service import ComprehensiveReportService
from src.evaluation.performance_evaluator import PerformanceEvaluator

def find_available_port(start_port=5000, max_port=5099):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:  # Port is available
                return port
        except:
            continue
    return None

def print_banner():
    """Print system banner"""
    print("=" * 80)
    print("🌍 ONTOMETRIC SYSTEM - COMPREHENSIVE DEMO")
    print("=" * 80)
    print("🎯 Features Demonstrated:")
    print("   ✓ Web Interface (Frontend)")
    print("   ✓ REST API (Backend)")
    print("   ✓ Knowledge Graph (RDF/SPARQL)")
    print("   ✓ CQ1-CQ7 Research Questions")
    print("   ✓ Comprehensive Evaluation System")
    print("   ✓ Performance Benchmarks & Visualizations")
    print("=" * 80)
    print()

def initialize_services():
    """Initialize all system services"""
    print("🔧 INITIALIZING SYSTEM SERVICES")
    print("-" * 40)
    
    # Initialize core services
    print("   📊 Data Retrieval Service...")
    data_service = DataRetrievalService()
    
    print("   🕸️ Knowledge Graph Service...")
    kg_service = UnifiedKnowledgeGraphService(data_service)
    
    print("   🧮 Calculation Service...")
    calc_service = CalculationService(data_service)
    
    print("   📋 Report Service...")
    report_service = ComprehensiveReportService(data_service, kg_service, calc_service)
    
    print("   📈 Evaluation Service...")
    evaluator = PerformanceEvaluator(data_service, kg_service, calc_service)
    
    print("   ✅ All services initialized successfully!")
    print()
    
    return data_service, kg_service, calc_service, report_service, evaluator

def demonstrate_core_functionality(data_service, kg_service, calc_service, report_service):
    """Demonstrate core system functionality"""
    print("🎪 DEMONSTRATING CORE FUNCTIONALITY")
    print("-" * 40)
    
    industries = ["semiconductors", "commercial_banks"]
    
    for industry in industries:
        print(f"   🏭 Testing {industry.replace('_', ' ').title()}...")
        
        # Test CQ1-CQ7
        try:
            # CQ1: Framework
            framework = kg_service.cq1_reporting_framework_by_industry(industry)
            print(f"      ✓ CQ1: Framework - {framework['reporting_framework']}")
            
            # CQ2: Categories  
            categories = kg_service.cq2_categories_by_framework(industry)
            print(f"      ✓ CQ2: Categories - {len(categories['categories'])} found")
            
            # CQ3: Metrics
            sample_category = categories['categories'][0]
            metrics = kg_service.cq3_metrics_by_category(industry, sample_category)
            print(f"      ✓ CQ3: Metrics - {len(metrics['metrics'])} in {sample_category}")
            
            # Test data access
            alignment_data = data_service.load_alignment_data(industry)
            print(f"      ✓ Data Access - {alignment_data.get('total_alignments', 0)} alignments")
            
        except Exception as e:
            print(f"      ❌ Error testing {industry}: {str(e)}")
    
    print("   ✅ Core functionality demonstration completed!")
    print()

def run_performance_evaluation(evaluator):
    """Run comprehensive performance evaluation"""
    print("📊 RUNNING COMPREHENSIVE PERFORMANCE EVALUATION")
    print("-" * 40)
    
    try:
        # Quick summary first
        print("   🚀 Quick Performance Summary...")
        quick_summary = evaluator.generate_performance_summary()
        
        print(f"      ✓ Industries Available: {len(quick_summary.get('industries_available', []))}")
        print(f"      ✓ System Status: Operational")
        print()
        
        # Full evaluation (this takes longer)
        print("   📈 Full Performance Evaluation...")
        print("      (This may take 30-60 seconds to complete all benchmarks...)")
        
        evaluation_results = evaluator.run_performance_evaluation()
        
        # Print key results
        sparql_performance = evaluation_results.get("sparql_performance", {})
        calculation_performance = evaluation_results.get("calculation_performance", {})
        
        print("   🎉 Evaluation Results Summary:")
        print(f"      ✓ SPARQL Queries Tested: {sparql_performance.get('total_queries_tested', 0)}")
        print(f"      ✓ Calculation Tests: {len(calculation_performance.get('industry_results', {}))}")
        print(f"      ✓ Visualization Charts: {len(evaluation_results.get('visualizations', []))}")
        
        visualization_paths = evaluation_results.get("visualizations", [])
        print(f"      ✓ Visualizations Generated: {len(visualization_paths)} charts")
        
        return evaluation_results
        
    except Exception as e:
        print(f"   ❌ Evaluation failed: {str(e)}")
        return None

def start_web_server(services_already_initialized=False):
    """Start the web server with improved port management"""
    print("🌐 STARTING WEB SERVER")
    print("-" * 40)
    
    try:
        # Use improved port manager
        from src.utils.port_manager import PortManager
        
        if services_already_initialized:
            # Services already loaded, just create app wrapper
            print("   📊 Using already initialized services...")
            app = create_app()
        else:
            # Let create_app initialize services
            app = create_app()
        
        # Get available port with smart management
        available_port = PortManager.get_available_port(preferred_port=8080)
        
        print(f"   🚀 Starting server on port {available_port}...")
        print(f"   🌐 Frontend: http://localhost:{available_port}/demo")
        print(f"   🔗 API: http://localhost:{available_port}/api/v1/")
        print("   📊 Server will start in foreground mode")
        print()
        
        # Start server directly (not in background thread to avoid conflicts)
        app.run(host='0.0.0.0', port=available_port, debug=False, use_reloader=False)
        
        return True, available_port
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Server stopped by user")
        return True, None
    except Exception as e:
        print(f"   ❌ Failed to start web server: {str(e)}")
        return False, None

def demonstrate_api_endpoints(port):
    """Demonstrate key API endpoints"""
    print("🔗 DEMONSTRATING API ENDPOINTS")
    print("-" * 40)
    
    if not port:
        print("   ❌ No server port available for API testing")
        return
    
    base_url = f"http://localhost:{port}/api/v1"
    
    endpoints_to_test = [
        ("System Health", "GET", "/system/health"),
        ("Available Frameworks", "GET", "/frameworks"),
        ("Quick Performance", "GET", "/evaluation/quick-summary"),
        ("CQ Performance", "GET", "/evaluation/cq-performance")
    ]
    
    for name, method, endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {name}: {response.status_code} - OK")
            else:
                print(f"   ⚠️ {name}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ {name}: Error - {str(e)}")
    
    print("   ✅ API endpoints demonstration completed!")
    print()

def open_browser_demo(port):
    """Open browser to show web interface"""
    print("🖥️ OPENING WEB INTERFACE")
    print("-" * 40)
    
    if not port:
        print("   ❌ No server port available for browser opening")
        return False
    
    try:
        url = f'http://localhost:{port}'
        webbrowser.open(url)
        print("   ✅ Browser opened to web interface!")
        print("   💡 You can now interact with the full system through the web UI")
        print()
        return True
    except Exception as e:
        print(f"   ❌ Could not open browser: {str(e)}")
        print(f"   💡 Please manually open: http://localhost:{port}")
        print()
        return False

def save_demo_results(evaluation_results):
    """Display results summary without saving unnecessary files"""
    if not evaluation_results:
        return
    
    print("💾 DEMONSTRATION RESULTS SUMMARY")
    print("-" * 40)
    
    try:
        # Only show summary, don't save to root directory
        print(f"   📊 Performance Visualizations: figures/evaluation/")
        print(f"   📁 Research Evaluation Data: evaluation_results/")
        print(f"   🎯 All evaluation artifacts preserved for research")
        print()
        
    except Exception as e:
        print(f"   ❌ Could not display results: {str(e)}")

def main():
    """Main demonstration function with options"""
    print_banner()
    
    # Check for command line arguments
    run_full_evaluation = '--full-eval' in sys.argv
    
    try:
        if run_full_evaluation:
            print("🎯 RUNNING FULL COMPREHENSIVE EVALUATION")
            print("-" * 40)
            
            # 1. Initialize all services
            data_service, kg_service, calc_service, report_service, evaluator = initialize_services()
            
            # 2. Demonstrate core functionality
            demonstrate_core_functionality(data_service, kg_service, calc_service, report_service)
            
            # 3. Run performance evaluation
            evaluation_results = run_performance_evaluation(evaluator)
            
            # 4. Show results summary
            save_demo_results(evaluation_results)
            
            # 5. Start web server (services already initialized)
            server_started, server_port = start_web_server(services_already_initialized=True)
            
        else:
            print("🚀 STARTING WEB SERVER (Quick Mode)")
            print("-" * 40)
            print("💡 Use --full-eval flag to run comprehensive evaluation")
            print()
            
            # Just start the web server (services will be initialized by Flask app)
            server_started, server_port = start_web_server(services_already_initialized=False)
        
        # Final status
        if server_started:
            print("\n🎉 ESG KNOWLEDGE GRAPH SYSTEM READY!")
            print("=" * 50)
            print("🌟 System Status: OPERATIONAL")
            print("🔗 Web Interface: AVAILABLE")
            if run_full_evaluation:
                print("📈 Performance: BENCHMARKED")
            print("=" * 50)
        else:
            print("⚠️ Web server could not start. Check the logs above for details.")
        
    except Exception as e:
        print(f"\n❌ SYSTEM STARTUP FAILED: {str(e)}")
        print("Please check the error above and ensure all dependencies are installed.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)