#!/usr/bin/env python3
"""
COMPREHENSIVE ESG SYSTEM DEMONSTRATION

This script starts the complete ESG Knowledge Graph system with:
✅ Web Interface (Frontend) - Available at http://localhost:5000/
✅ REST API (Backend) - Available at http://localhost:5000/api/...
✅ 422K+ ESG records from real companies
✅ All calculation services and knowledge graph queries

System Architecture:
- Web Interface (HTML) -> API Gateway (Flask) -> Knowledge Graph Service (RDF/SPARQL)
- Data Retrieval Service (CSV) -> Calculation Service (Python) -> Report Service (JSON)
"""

import sys
import os
import argparse
sys.path.append('src')

from src.services.data_retrieval_service import DataRetrievalService
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.calculation_service import CalculationService
from src.api.esg_api import create_app
from src.utils.port_manager import PortManager

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ESG Knowledge Graph System - Web Service Demo")
    parser.add_argument('--eval-only', action='store_true', 
                       help='Run evaluation only (no web server)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run the web server on (default: 5000)')
    args = parser.parse_args()
    
    print("🌟 ESG KNOWLEDGE GRAPH SYSTEM - WEB SERVICE DEMO")
    print("=" * 80)
    print("🌐 Frontend: http://localhost:{}/".format(args.port))
    print("🔧 Backend API: http://localhost:{}/api/...".format(args.port))
    print("📈 Coverage: 422K+ ESG records, Knowledge Graph + Real Data")
    print("🏗️ Architecture: Flask Web Server + Knowledge Graph + Calculation Models")
    print()
    
    try:
        # Initialize core services to verify everything works
        print("🔧 INITIALIZING CORE SERVICES...")
        data_service = DataRetrievalService()
        kg_service = KnowledgeGraphService(data_service)
        calc_service = CalculationService(data_service, kg_service)
        
        print("   ✅ Data Retrieval Service initialized")
        print("   ✅ Knowledge Graph Service initialized") 
        print("   ✅ Calculation Service initialized")
        print()
        
        # Quick verification test
        print("🔍 RUNNING QUICK SYSTEM VERIFICATION...")
        try:
            # Test data loading
            companies = data_service.get_companies_by_sector("Technology")[:2]
            print(f"   ✅ Data Service: Found {len(companies)} tech companies")
            
            # Test knowledge graph
            query_result = kg_service.execute_sparql_query("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
            if query_result and len(query_result) > 0:
                triple_count = query_result[0].get('count', 0)
                print(f"   ✅ Knowledge Graph: {triple_count} RDF triples loaded")
            else:
                print("   ⚠️ Knowledge Graph: No triples found")
                
        except Exception as e:
            print(f"   ⚠️ Verification warning: {str(e)}")
        print()
        
        if args.eval_only:
            print("📊 RUNNING EVALUATION ONLY (--eval-only flag detected)")
            from src.evaluation.performance_evaluator import ComprehensivePerformanceEvaluator
            
            evaluator = ComprehensivePerformanceEvaluator(data_service, kg_service, calc_service)
            print("   ✅ Comprehensive Performance Evaluator ready")
            print()
            
            results = evaluator.run_comprehensive_evaluation(use_two_part_evaluation=False)
            
            if 'error' in results:
                print(f"❌ Evaluation failed: {results['error']}")
                return
            
            print("\n🎯 EVALUATION COMPLETED SUCCESSFULLY!")
            print(f"📁 Results saved to: evaluation_results/")
            print(f"📊 Visualizations: {len(results.get('visualizations', []))} charts generated")
            print(f"⏱️ Total time: {results.get('evaluation_time_seconds', 0):.2f}s")
            return
        
        # Start web server
        print("🚀 STARTING WEB SERVER...")
        print("   🌐 Frontend will be available at: http://localhost:{}/".format(args.port))
        print("   🔧 API endpoints available at: http://localhost:{}/api/...".format(args.port))
        print("   ⏹️ Press Ctrl+C to stop the server")
        print()
        
        # Create Flask app and start with port management
        app = create_app()
        PortManager.run_flask_app_with_port_management(
            app, 
            host='0.0.0.0', 
            preferred_port=args.port, 
            debug=False  # Set to False for production-like behavior
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ ESG System stopped by user")
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()