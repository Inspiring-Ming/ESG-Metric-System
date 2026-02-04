# src/api/esg_api.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from typing import Dict, List, Any, Optional
import time
import json
import os
from datetime import datetime
import sys

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.calculation_service import CalculationService
from src.services.report_service import ReportService
from src.services.data_retrieval_service import DataRetrievalService
from src.evaluation.performance_evaluator import create_comprehensive_performance_diagram

class ESGKnowledgeGraphAPI:
    """Comprehensive REST API for Ontometric System"""
    
    def __init__(self):
        # Configure template folder to use web_interface directory
        import os
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_folder = os.path.join(current_dir, "web_interface", "templates")
        
        self.app = Flask(__name__, template_folder=template_folder)
        CORS(self.app)
        
        # Initialize services
        self.data_service = DataRetrievalService()
        self.kg_service = KnowledgeGraphService(self.data_service)
        self.calc_service = CalculationService(self.data_service)  # Pass data service for external data access
        # Wire up services - connect knowledge graph to calculation service
        self.calc_service.kg_service = self.kg_service
        self.report_service = ReportService()  # New consolidated report service
        self.create_performance_diagram = create_comprehensive_performance_diagram
        
        # Track API usage for performance metrics
        self.api_metrics = {
            "total_requests": 0,
            "request_history": [],
            "error_count": 0,
            "avg_response_time": 0
        }
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up all API routes"""
        
        # Health check
        self.app.route('/api/v1/system/health', methods=['GET'])(self.health_check)
        
        # ==================== SERVICE-BASED CORE ENDPOINTS ====================
        # Knowledge Graph Service endpoints (KGservice)
        self.app.route('/api/KGservice/industries', methods=['GET'])(self.get_available_industries)
        self.app.route('/api/KGservice/industries/<industry>/frameworks', methods=['GET'])(self.get_reporting_frameworks_by_industry)
        self.app.route('/api/KGservice/frameworks/<framework>/categories', methods=['GET'])(self.get_categories_by_framework)
        self.app.route('/api/KGservice/categories/<category>/metrics', methods=['GET'])(self.get_detailed_metrics_by_category)
        
        # Data Retrieval Service endpoints (DRservice)
        self.app.route('/api/DRservice/industries/<industry>/companies', methods=['GET'])(self.get_companies_by_industry)
        self.app.route('/api/DRservice/companies/<company_name>/years', methods=['GET'])(self.get_company_years_api)
        self.app.route('/api/DRservice/companies/<company_name>/industry', methods=['GET'])(self.get_company_industry_api)
        self.app.route('/api/DRservice/companies/all', methods=['GET'])(self.get_all_companies_api)
        self.app.route('/api/DRservice/data-availability/<company_name>/<year>', methods=['GET'])(self.check_data_availability)
        self.app.route('/api/DRservice/data-availability/bulk', methods=['POST'])(self.check_multiple_data_availability)

        # Calculation Service endpoints (CSservice)
        self.app.route('/api/CSservice/calculate', methods=['POST'])(self.calculate_metrics)

        # Knowledge Graph Service endpoints for models
        self.app.route('/api/KGservice/metrics/<metric_name>/models', methods=['GET'])(self.get_metric_models)
        
        # Report Service endpoints (RSservice)
        self.app.route('/api/RSservice/reports/generate', methods=['POST'])(self.generate_report)
        self.app.route('/api/RSservice/reports/generate-word', methods=['POST'])(self.generate_word_report)
        self.app.route('/api/RSservice/reports/generate-pdf', methods=['POST'])(self.generate_pdf_report)
        self.app.route('/api/RSservice/reports/download/<filename>', methods=['GET'])(self.download_report)
        
        # ==================== SYSservice — System & Analytics ====================
        self.app.route('/api/SYSservice/health', methods=['GET'])(self.health_check)
        self.app.route('/api/SYSservice/info', methods=['GET'])(self.get_system_info)
        self.app.route('/api/SYSservice/openapi', methods=['GET'])(self.get_openapi_spec)
        self.app.route('/api/SYSservice/analytics/performance', methods=['GET'])(self.get_performance_metrics)
        self.app.route('/api/SYSservice/analytics/data-coverage', methods=['GET'])(self.get_data_coverage_analytics)
        self.app.route('/api/SYSservice/analytics/api-usage', methods=['GET'])(self.get_api_usage_analytics)

        # ==================== EVALservice — Evaluation ====================
        self.app.route('/api/EVALservice/comprehensive', methods=['GET'])(self.run_comprehensive_evaluation)
        self.app.route('/api/EVALservice/cq-performance', methods=['GET'])(self.get_cq_performance)
        self.app.route('/api/EVALservice/quick-summary', methods=['GET'])(self.get_quick_summary)

        # ==================== LEGACY v1 ENDPOINTS (for backward compatibility) ====================
        # Industry and framework endpoints
        self.app.route('/api/v1/industries', methods=['GET'])(self.get_available_industries)
        self.app.route('/api/v1/industries/<industry>/companies', methods=['GET'])(self.get_companies_by_industry)
        self.app.route('/api/v1/industries/<industry>/reporting-frameworks', methods=['GET'])(self.get_reporting_frameworks_by_industry)
        self.app.route('/api/v1/industries/<industry>/frameworks', methods=['GET'])(self.get_frameworks_by_industry)
        
        # Framework and category endpoints
        self.app.route('/api/v1/frameworks', methods=['GET'])(self.get_frameworks)
        self.app.route('/api/v1/reporting-frameworks/<framework>/categories', methods=['GET'])(self.get_categories_by_framework)
        self.app.route('/api/v1/frameworks/<framework>/industries', methods=['GET'])(self.get_industries_by_framework)
        
        # Category and metrics endpoints
        self.app.route('/api/v1/categories/<category>/metrics', methods=['GET'])(self.get_metrics_by_category)
        self.app.route('/api/v1/categories/<category>/metrics-detailed', methods=['GET'])(self.get_detailed_metrics_by_category)
        self.app.route('/api/v1/metrics/<metric_id>/details', methods=['GET'])(self.get_metric_details)
        self.app.route('/api/v1/models/<model_id>/requirements', methods=['GET'])(self.get_model_input_requirements)
        
        # Calculation endpoints
        self.app.route('/api/v1/calculate', methods=['POST'])(self.calculate_metrics)
        self.app.route('/api/v1/industries/<industry>/calculable-metrics', methods=['GET'])(self.get_calculable_metrics)
        
        # Memory and caching endpoints
        self.app.route('/api/v1/memory/summary', methods=['GET'])(self.get_memory_summary)
        self.app.route('/api/v1/memory/company-calculations/<company_name>/<year>', methods=['GET'])(self.get_company_calculations)
        self.app.route('/api/v1/memory/session-calculations/<session_id>', methods=['GET'])(self.get_session_calculations)
        
        # Report generation endpoints
        self.app.route('/api/v1/reports/generate', methods=['POST'])(self.generate_report)
        self.app.route('/api/v1/reports/<report_id>', methods=['GET'])(self.get_report)
        self.app.route('/api/v1/reports/<report_id>/lineage', methods=['GET'])(self.get_report_lineage)
        self.app.route('/api/v1/reports', methods=['GET'])(self.list_reports)
        self.app.route('/api/v1/reports/cross-industry', methods=['POST'])(self.generate_cross_industry_report)
        
        # SPARQL query endpoints
        self.app.route('/api/v1/sparql', methods=['POST'])(self.execute_sparql_query)
        self.app.route('/api/v1/queries/<query_id>', methods=['GET'])(self.execute_predefined_query)
        
        # Analytics and monitoring endpoints
        self.app.route('/api/v1/analytics/performance', methods=['GET'])(self.get_performance_metrics)
        self.app.route('/api/v1/analytics/data-coverage', methods=['GET'])(self.get_data_coverage_analytics)
        self.app.route('/api/v1/analytics/api-usage', methods=['GET'])(self.get_api_usage_analytics)
        
        # System information endpoints
        self.app.route('/api/v1/system/info', methods=['GET'])(self.get_system_info)
        self.app.route('/api/v1/system/openapi', methods=['GET'])(self.get_openapi_spec)
        
        # Data availability endpoints
        self.app.route('/api/v1/data-availability/<company_name>/<year>', methods=['GET'])(self.check_data_availability)
        self.app.route('/api/v1/data-availability/bulk', methods=['POST'])(self.check_multiple_data_availability)
        
        # Evaluation endpoints
        self.app.route('/api/v1/evaluation/comprehensive', methods=['GET'])(self.run_comprehensive_evaluation)
        self.app.route('/api/v1/evaluation/cq-performance', methods=['GET'])(self.get_cq_performance)
        self.app.route('/api/v1/evaluation/quick-summary', methods=['GET'])(self.get_quick_summary)
        
        # Web interface
        self.app.route('/', methods=['GET'])(self.serve_web_interface)
        
        # Error handlers
        self.app.register_error_handler(400, self.handle_bad_request)
        self.app.register_error_handler(404, self.handle_not_found)
        self.app.register_error_handler(500, self.handle_internal_error)
    
    def before_request(self):
        """Track request metrics"""
        request.start_time = time.time()
        self.api_metrics["total_requests"] += 1
    
    def after_request(self, response):
        """Track response metrics"""
        request_time = time.time() - request.start_time
        
        self.api_metrics["request_history"].append({
            "endpoint": request.endpoint,
            "method": request.method,
            "response_time": request_time,
            "status_code": response.status_code,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 1000 requests
        if len(self.api_metrics["request_history"]) > 1000:
            self.api_metrics["request_history"] = self.api_metrics["request_history"][-1000:]
        
        # Update average response time
        recent_times = [r["response_time"] for r in self.api_metrics["request_history"]]
        self.api_metrics["avg_response_time"] = sum(recent_times) / len(recent_times)
        
        if response.status_code >= 400:
            self.api_metrics["error_count"] += 1
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{request_time:.3f}s"
        response.headers['X-Request-ID'] = str(self.api_metrics["total_requests"])
        
        return response
    
    # ==================== NEW INDUSTRY-FIRST WORKFLOW APIs ====================
    
    def get_available_industries(self):
        """Step 1: Get available industries from RDF through Knowledge Graph Service"""
        try:
            print("📊 Step 1: Getting available industries from Knowledge Graph Service")
            industries = []
            available_industries = self.data_service.get_available_industries()
            
            for industry in available_industries:
                # Step 1: Get framework using CQ1 from Knowledge Graph Service
                cq1_result = self.kg_service.cq1_reporting_framework_by_industry(industry)
                
                # Get categories using CQ2 from Knowledge Graph Service
                cq2_result = self.kg_service.cq2_categories_by_framework(industry)
                categories_count = len(cq2_result.get("categories", []))
                
                # Don't get company count here - keep Step 1 fast and simple
                industries.append({
                    "industry_id": industry,
                    "industry_name": industry.replace("_", " ").title(),
                    "reporting_framework": cq1_result["reporting_framework"],
                    "categories_count": categories_count,
                    "total_companies_available": "Available in Step 2",
                    "description": f"ESG reporting for {industry.replace('_', ' ')} industry using {cq1_result['reporting_framework']} framework",
                    "data_source": "knowledge_graph_service_cq1_cq2"
                })
            
            print(f"📊 Step 1 Complete: Found {len(industries)} industries from RDF Knowledge Graph")
            return jsonify({
                "status": "success",
                "data": industries,
                "count": len(industries),
                "service_used": "knowledge_graph_service",
                "cq_queries_used": ["CQ1: Reporting Framework", "CQ2: Categories"],
                "message": "Industries retrieved from RDF Knowledge Graph - Select an industry to proceed"
            })
        except Exception as e:
            print(f"❌ Step 1 Error: {str(e)}")
            return jsonify({
                "status": "error", 
                "error_category": "KNOWLEDGE_GRAPH_ACCESS_ERROR",
                "user_message": "Error accessing industry data from knowledge graph",
                "suggestion": "Please check knowledge graph availability and try again",
                "technical_message": str(e)
            }), 500
    
    def get_companies_by_industry(self, industry):
        """Step 2: Get 20 companies with available years using enhanced Data Retrieval Service"""
        try:
            print(f"📊 Step 2: Getting companies for industry: {industry}")
            
            # Use enhanced Data Retrieval Service to get companies
            companies = self.data_service.get_companies_by_industry(industry)
            
            # Handle error responses from enhanced service
            if isinstance(companies, dict) and companies.get("error"):
                return jsonify({
                    "status": "error",
                    "error_category": companies.get("error_category"),
                    "user_message": companies.get("user_message"),
                    "suggestion": companies.get("suggestion"),
                    "technical_message": companies.get("technical_message")
                }), 400
            
            # Get company details including years available using enhanced service
            detailed_companies = []
            for company in companies[:20]:  # Limit to 20 for performance
                try:
                    # Use enhanced Data Retrieval Service for year availability
                    years = self.data_service.get_available_years(company)
                    
                    # Handle error responses from enhanced service
                    if isinstance(years, dict) and years.get("error"):
                        print(f"⚠️ Year data error for {company}: {years.get('user_message')}")
                        continue
                    
                    detailed_companies.append({
                        "company_name": company,
                        "years_available": years,
                        "year_count": len(years),
                        "latest_year": max(years) if years else None,
                        "earliest_year": min(years) if years else None,
                        "data_source": "enhanced_data_retrieval_service"
                    })
                except Exception as e:
                    print(f"⚠️ Skipping company {company}: {str(e)}")
                    continue
            
            print(f"📊 Found {len(detailed_companies)} companies with data for {industry}")
            return jsonify({
                "status": "success",
                "industry_id": industry,
                "industry_name": industry.replace("_", " ").title(),
                "data": detailed_companies,
                "count": len(detailed_companies),
                "total_available": len(companies),
                "service_used": "enhanced_data_retrieval_service",
                "message": f"Companies with available years for {industry.replace('_', ' ')} industry"
            })
        except Exception as e:
            print(f"❌ Error getting companies for {industry}: {str(e)}")
            return jsonify({
                "status": "error", 
                "error_category": "EXTERNAL_DATA_ACCESS_ERROR",
                "user_message": "Error accessing company data",
                "suggestion": "Please try again or contact support",
                "technical_message": str(e)
            }), 500

    def get_company_years_api(self, company_name):
        """Get available years for a specific company using Data Retrieval Service"""
        try:
            print(f"📊 Getting available years for company: {company_name}")
            
            # Use Data Retrieval Service to get available years
            years = self.data_service.get_available_years(company_name)
            
            # Handle error responses from enhanced service
            if isinstance(years, dict) and years.get("error"):
                return jsonify({
                    "status": "error",
                    "error_category": years.get("error_category"),
                    "user_message": years.get("user_message"),
                    "suggestion": years.get("suggestion"),
                    "technical_message": years.get("technical_message")
                }), 400
            
            # Sort years in descending order (most recent first)
            sorted_years = sorted(years, reverse=True) if years else []
            
            print(f"📊 Found {len(sorted_years)} years for {company_name}: {sorted_years}")
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "years": sorted_years,
                "count": len(sorted_years),
                "latest_year": sorted_years[0] if sorted_years else None,
                "earliest_year": sorted_years[-1] if sorted_years else None,
                "service_used": "data_retrieval_service",
                "message": f"Available years for {company_name}"
            })
        except Exception as e:
            print(f"❌ Error getting years for {company_name}: {str(e)}")
            return jsonify({
                "status": "error",
                "error_category": "EXTERNAL_DATA_ACCESS_ERROR",
                "user_message": "Error accessing year data for company",
                "suggestion": "Please try again or select a different company",
                "technical_message": str(e)
            }), 500

    def get_company_industry_api(self, company_name):
        """Get the industry for a specific company"""
        try:
            print(f"📊 Getting industry for company: {company_name}")

            # Use Data Retrieval Service to find company's industry
            industry = self.data_service.get_company_industry(company_name)

            if industry is None:
                return jsonify({
                    "status": "error",
                    "error_category": "COMPANY_NOT_FOUND",
                    "user_message": f"Company '{company_name}' not found in any industry",
                    "suggestion": "Please check the company name or select from the available companies list",
                    "technical_message": "Company not found in industry datasets"
                }), 404

            print(f"📊 Found industry: {industry} for {company_name}")
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "industry": industry,
                "industry_display": industry.replace('_', ' ').title(),
                "service_used": "data_retrieval_service",
                "message": f"Industry found for {company_name}"
            })
        except Exception as e:
            print(f"❌ Error getting industry for {company_name}: {str(e)}")
            return jsonify({
                "status": "error",
                "error_category": "EXTERNAL_DATA_ACCESS_ERROR",
                "user_message": "Error finding company industry",
                "suggestion": "Please try again or select a different company",
                "technical_message": str(e)
            }), 500

    def get_all_companies_api(self):
        """Get all companies organized by industry"""
        try:
            print(f"📊 Getting all companies from all industries")

            # Use Data Retrieval Service to get all companies
            companies_by_industry = self.data_service.get_all_companies()

            total_companies = sum(len(companies) for companies in companies_by_industry.values())

            print(f"📊 Found {total_companies} companies across {len(companies_by_industry)} industries")
            return jsonify({
                "status": "success",
                "companies_by_industry": companies_by_industry,
                "total_companies": total_companies,
                "industries": list(companies_by_industry.keys()),
                "service_used": "data_retrieval_service",
                "message": f"Retrieved {total_companies} companies from all industries"
            })
        except Exception as e:
            print(f"❌ Error getting all companies: {str(e)}")
            return jsonify({
                "status": "error",
                "error_category": "EXTERNAL_DATA_ACCESS_ERROR",
                "user_message": "Error retrieving companies list",
                "suggestion": "Please try again",
                "technical_message": str(e)
            }), 500

    def get_metric_models(self, metric_name):
        """Get available models for a specific metric"""
        try:
            industry = request.args.get('industry', 'semiconductors')
            print(f"📊 Getting models for metric: {metric_name} in industry: {industry}")

            # Use CQ4 to get metric calculation method and model info
            cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric_name)

            measurement_method = cq4_result.get("measurement_method", "unknown")

            if measurement_method == "direct_measurement":
                # For direct measurements, get the dataset variable using CQ7
                try:
                    cq7_result = self.kg_service.cq7_get_dataset_variable(industry, metric_name)
                    dataset_variable = cq7_result.get("dataset_variable", "N/A")
                except:
                    dataset_variable = "N/A"

                return jsonify({
                    "status": "success",
                    "metric_name": metric_name,
                    "measurement_method": "direct_measurement",
                    "dataset_variable": dataset_variable,
                    "models": [],
                    "message": "Direct measurement - no models required"
                })

            elif measurement_method == "calculation_model":
                # For calculated metrics, get model details
                model_name = cq4_result.get("model_name", "Unknown Model")

                # Get model equation/formula using CQ5
                try:
                    cq5_result = self.kg_service.cq5_model_input_datapoints(industry, model_name, self.calc_service)
                    model_equation = cq5_result.get("model_equation", cq5_result.get("formula", "N/A"))
                    input_metrics = cq5_result.get("required_inputs", [])
                except:
                    model_equation = cq4_result.get("model_description", "N/A")
                    input_metrics = []

                models = [{
                    "model_name": model_name,
                    "model_equation": model_equation,
                    "model_description": cq4_result.get("model_description", ""),
                    "input_metrics": input_metrics
                }]

                return jsonify({
                    "status": "success",
                    "metric_name": metric_name,
                    "measurement_method": "calculation_model",
                    "models": models,
                    "message": f"Found {len(models)} model(s) for {metric_name}"
                })

            else:
                return jsonify({
                    "status": "error",
                    "message": f"Unknown measurement method: {measurement_method}"
                }), 400

        except Exception as e:
            print(f"❌ Error getting models for {metric_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def get_reporting_frameworks_by_industry(self, industry):
        """Step 3: Get reporting frameworks for selected industry using Knowledge Graph Service (CQ1)"""
        try:
            print(f"📊 Step 3: Getting reporting frameworks for {industry} using Knowledge Graph Service")
            
            # Use CQ1 to get framework information from RDF knowledge graph
            cq1_result = self.kg_service.cq1_reporting_framework_by_industry(industry)
            
            # Get categories using CQ2 for additional context
            cq2_result = self.kg_service.cq2_categories_by_framework(industry)
            categories = cq2_result.get("categories", [])
            
            framework_info = {
                "id": cq1_result["reporting_framework"].replace(" ", "_").lower(),
                "name": cq1_result["reporting_framework"],
                "industry": industry,
                "categories_count": len(categories),
                "description": f"SASB framework for {industry.replace('_', ' ')} industry",
                "cq1_source": "Retrieved via CQ1: What reporting framework is used for this industry?",
                "categories_preview": categories[:3] if categories else [],
                "service_used": "knowledge_graph_service",
                "cq_query": "CQ1"
            }
            
            print(f"📊 Step 3 Complete: Found framework '{cq1_result['reporting_framework']}' via CQ1")
            return jsonify({
                "status": "success",
                "data": [framework_info],
                "service_used": "knowledge_graph_service",
                "cq_query_used": "CQ1: Reporting Framework by Industry",
                "message": f"Reporting framework retrieved from RDF Knowledge Graph for {industry}"
            })
        except Exception as e:
            print(f"❌ Error getting frameworks for {industry}: {str(e)}")
            return jsonify({
                "status": "error",
                "error_category": "KNOWLEDGE_GRAPH_ACCESS_ERROR", 
                "user_message": "Error accessing reporting framework data",
                "suggestion": "Please check knowledge graph availability and try again",
                "technical_message": str(e)
            }), 500
    
    def get_frameworks_by_industry(self, industry_id):
        """Get reporting frameworks available for a specific industry (CQ1)"""
        try:
            # Use CQ1 to get framework information
            cq1_result = self.kg_service.cq1_reporting_framework_by_industry(industry_id)
            
            # Get categories using CQ2
            cq2_result = self.kg_service.cq2_categories_by_framework(industry_id)
            categories = cq2_result.get("categories", [])
            
            framework_data = {
                "framework_id": cq1_result["reporting_framework"].replace(" ", "_").lower(),
                "framework_name": cq1_result["reporting_framework"],
                "industry": industry_id,
                "categories": categories,
                "categories_count": len(categories),
                "description": f"SASB framework specifically designed for {industry_id.replace('_', ' ')} industry",
                "cq1_query": "What reporting framework is used for this industry?",
                "cq2_preview": f"Framework contains {len(categories)} ESG categories"
            }
            
            return jsonify({
                "status": "success",
                "industry_id": industry_id,
                "data": [framework_data],  # Return as list for consistency
                "count": 1,
                "message": f"Reporting framework for {industry_id.replace('_', ' ')} determined using CQ1"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_categories_by_framework(self, framework):
        """Step 4: Get ESG categories for selected reporting framework using Knowledge Graph Service (CQ2)"""
        try:
            print(f"📊 Step 4: Getting categories for framework {framework} using Knowledge Graph Service")
            
            # Map framework_id back to industry
            industry_mapping = {
                "sasb_semiconductors": "semiconductors",
                "sasb_commercial_banks": "commercial_banks"
            }
            
            industry = industry_mapping.get(framework)
            if not industry:
                return jsonify({
                    "status": "error", 
                    "error_category": "FRAMEWORK_NOT_FOUND",
                    "user_message": "Framework not found",
                    "suggestion": "Please select a valid framework",
                    "technical_message": f"Framework {framework} not supported"
                }), 404
            
            # Use CQ2 to get categories from Knowledge Graph Service
            cq2_result = self.kg_service.cq2_categories_by_framework(industry)
            categories = cq2_result.get("categories", [])
            
            # Enhance categories with metric counts using CQ3
            enhanced_categories = []
            for category in categories:
                try:
                    cq3_result = self.kg_service.cq3_metrics_by_category(industry, category)
                    metrics = cq3_result.get("metrics", [])
                    
                    enhanced_categories.append({
                        "category_id": category.replace(" ", "_").lower(),
                        "category_name": category,
                        "metrics_count": len(metrics),
                        "sample_metrics": [m.get("metric_name") for m in metrics[:3]],  # Show first 3 metric names
                        "description": f"ESG metrics related to {category.lower()} in {industry.replace('_', ' ')} industry",
                        "service_used": "knowledge_graph_service",
                        "cq_queries": ["CQ2", "CQ3"]
                    })
                except Exception:
                    enhanced_categories.append({
                        "category_id": category.replace(" ", "_").lower(),
                        "category_name": category,
                        "metrics_count": 0,
                        "sample_metrics": [],
                        "description": f"ESG metrics related to {category.lower()}",
                        "service_used": "knowledge_graph_service",
                        "cq_queries": ["CQ2"]
                    })
            
            print(f"📊 Step 4 Complete: Found {len(enhanced_categories)} categories via CQ2")
            return jsonify({
                "status": "success",
                "framework_id": framework,
                "industry": industry,
                "data": enhanced_categories,
                "count": len(enhanced_categories),
                "service_used": "knowledge_graph_service",
                "cq_queries_used": ["CQ2: Categories by Framework", "CQ3: Metrics by Category"],
                "message": f"ESG categories retrieved from RDF Knowledge Graph for {industry.replace('_', ' ')} framework"
            })
        except Exception as e:
            print(f"❌ Step 4 Error: {str(e)}")
            return jsonify({
                "status": "error", 
                "error_category": "KNOWLEDGE_GRAPH_ACCESS_ERROR",
                "user_message": "Error accessing category data",
                "suggestion": "Please check knowledge graph availability and try again",
                "technical_message": str(e)
            }), 500
    
    def get_detailed_metrics_by_category(self, **kwargs):
        """Get detailed metrics for a specific category with calculation methods (CQ3-CQ7)"""
        try:
            # Get category from kwargs (Flask route parameter)
            category = kwargs.get('category')
            if not category:
                return jsonify({"status": "error", "message": "Category parameter required"}), 400
                
            # Extract industry and category from the request or determine from category_id
            industry = request.args.get('industry')
            if not industry:
                # Try to determine industry from context or return error
                return jsonify({"status": "error", "message": "Industry parameter required"}), 400
            
            # Convert category back to readable format - handle specific cases
            category_mapping = {
                "greenhouse_gas_emissions": "Greenhouse Gas Emissions",
                "energy_management_in_manufacturing": "Energy Management in Manufacturing", 
                "water_management": "Water Management",
                "waste_management": "Waste Management",
                "workforce_health_safety": "Workforce Health & Safety",
                "recruiting_managing_global_skilled_workforce": "Recruiting & Managing a Global & Skilled Workforce",
                "product_lifecycle_management": "Product Lifecycle Management",
                "materials_sourcing": "Materials Sourcing",
                "intellectual_property_protection_competitive_behaviour": "Intellectual Property Protection & Competitive Behaviour"
            }
            
            category_name = category_mapping.get(category, category.replace("_", " ").title())
            
            # Use CQ3 to get metrics with calculation information
            cq3_result = self.kg_service.cq3_metrics_by_category(industry, category_name)
            metrics = cq3_result.get("metrics", [])
            
            # Process each metric from CQ3 results which already contain calculation info
            detailed_metrics = []
            for metric in metrics:
                try:
                    # Check if metric is a dict (correct format) or string (error case)
                    if not isinstance(metric, dict):
                        print(f"⚠️ Metric is not a dict: {type(metric)} - {metric}")
                        continue
                        
                    metric_code = metric.get("code")
                    metric_name = metric.get("metric_name")
                    has_model = metric.get("has_calculation_model", False)
                    
                    # Get additional details using CQ4 with metric name for unique identification
                    try:
                        cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric_name)
                        model_name = cq4_result.get("model_name", "Direct access")
                        calculation_method = cq4_result.get("measurement_method", "direct_measurement")
                        print(f"✅ CQ4 for {metric_name}: method={calculation_method}, model={model_name}")
                    except Exception as e:
                        print(f"⚠️ CQ4 error for {metric_name}: {str(e)}")
                        model_name = "Direct access"
                        calculation_method = "direct_measurement"
                    
                    # Get model details if it has a calculation model
                    input_datapoints = []
                    model_formula = "Direct access from external dataset"
                    
                    if calculation_method == "calculation_model" and model_name != "Direct access" and model_name != "n/a":
                        try:
                            cq5_result = self.kg_service.cq5_model_input_datapoints(industry, model_name, self.calc_service)
                            input_datapoints = cq5_result.get("required_inputs", [])
                            model_formula = cq5_result.get("formula", "Calculation model formula")
                            print(f"✅ CQ5 for {model_name}: formula={model_formula}")
                        except Exception as e:
                            print(f"⚠️ CQ5 error for model {model_name}: {str(e)}")
                            model_formula = "Model calculation formula"
                    
                    detailed_metrics.append({
                        "metric_id": metric_code,
                        "metric_code": metric_code,
                        "metric_name": metric.get("metric_name"),
                        "description": metric.get("metric_description"),
                        "unit": metric.get("unit"),
                        "metric_type": metric.get("metric_type"),
                        "has_calculation_model": (calculation_method == "calculation_model"),
                        "calculation_method": calculation_method,
                        "model_name": model_name,
                        "input_datapoints": input_datapoints,
                        "model_formula": model_formula,
                        "data_access_type": "Model-based calculation" if calculation_method == "calculation_model" else "Direct access",
                        "complexity": "High" if calculation_method == "calculation_model" else "Low"
                    })
                    
                except Exception as e:
                    print(f"⚠️ Error processing metric {metric}: {str(e)}")
                    # Create fallback entry only if we have at least a metric code
                    if isinstance(metric, dict) and metric.get("code"):
                        detailed_metrics.append({
                            "metric_id": metric.get("code"),
                            "metric_code": metric.get("code"),
                            "metric_name": metric.get("metric_name", "Unknown"),
                            "has_calculation_model": False,
                            "data_access_type": "Direct access",
                            "error": str(e)
                        })
            
            return jsonify({
                "status": "success",
                "category_id": category,
                "category_name": category_name,
                "industry": industry,
                "data": detailed_metrics,
                "count": len(detailed_metrics),
                "cq_queries_used": ["CQ3: Metrics by category", "CQ4: Calculation method", "CQ5: Input datapoints", "CQ6: Model formula", "CQ7: Semantic mapping"],
                "message": f"Detailed metrics for {category_name} category with calculation methods"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def _get_sample_companies_for_industry(self, industry):
        """Helper method to get sample companies for an industry from external dataset"""
        try:
            # Load external dataset and filter by industry
            if not hasattr(self.calc_service, 'external_data_service'):
                print(f"📊 External data service not available, using fallback for {industry}")
                return self._get_fallback_companies_for_industry(industry)
            
            # Try to get companies directly by industry name first
            try:
                companies = self.calc_service.external_data_service.get_companies_by_industry(industry)
                if companies:
                    print(f"📊 Found {len(companies)} companies for {industry}")
                    return companies
            except Exception as e:
                print(f"⚠️ Error getting companies directly: {str(e)}")
            
            # Fallback to broader industry search
            industry_mappings = {
                "semiconductors": ["Industrial Machinery & Goods", "Technology", "Semiconductors", "Electronics"],
                "commercial_banks": ["Banks", "Financial Services", "Commercial Banks", "Banking"]
            }
            
            external_industries = industry_mappings.get(industry, [])
            companies = []
            
            # Get companies from external dataset using broader search
            for ext_industry in external_industries:
                try:
                    industry_companies = self.calc_service.external_data_service.get_companies_by_industry(ext_industry)
                    companies.extend(industry_companies)
                except Exception as e:
                    print(f"⚠️ Error searching {ext_industry}: {str(e)}")
                    continue
            
            # Remove duplicates and return
            unique_companies = list(set(companies))
            if unique_companies:
                print(f"📊 Found {len(unique_companies)} companies using broader search")
                return unique_companies
            else:
                print(f"📊 No companies found in external dataset, using fallback")
                return self._get_fallback_companies_for_industry(industry)
                
        except Exception as e:
            print(f"⚠️ Error in _get_sample_companies_for_industry: {str(e)}")
            return self._get_fallback_companies_for_industry(industry)
    
    def _get_fallback_companies_for_industry(self, industry):
        """Fallback companies when external dataset is not available"""
        fallback_companies = {
            "semiconductors": ["Intel Corp", "STMicroelectronics NV", "ON Semiconductor Corp", "NVIDIA Corp", "Advanced Micro Devices Inc"],
            "commercial_banks": ["Banco Santander SA", "Taishin Financial Holding Co Ltd", "JPMorgan Chase & Co", "Bank of America Corp"]
        }
        return fallback_companies.get(industry, ["Demo Company A", "Demo Company B"])
    
    # ==================== CORE USER SELECTION APIs ====================
    
    def get_frameworks(self):
        """Get all available reporting frameworks"""
        try:
            frameworks = []
            for industry in self.data_service.get_available_industries():
                # Use CQ1 to get framework information
                cq1_result = self.kg_service.cq1_reporting_framework_by_industry(industry)
                
                # Get categories count using CQ2
                cq2_result = self.kg_service.cq2_categories_by_framework(industry)
                categories_count = len(cq2_result.get("categories", []))
                
                frameworks.append({
                    "framework_id": cq1_result["reporting_framework"].replace(" ", "_").lower(),
                    "framework_name": cq1_result["reporting_framework"],
                    "industry": industry,
                    "categories_count": categories_count,
                    "description": f"SASB framework for {industry.replace('_', ' ').title()}"
                })
            
            return jsonify({
                "status": "success",
                "data": frameworks,
                "count": len(frameworks)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_industries_by_framework(self, framework_id):
        """Get industries supported by a specific framework"""
        try:
            industries = []
            for industry in self.data_service.get_available_industries():
                industry_summary = self.kg_service.industries[industry]
                industries.append({
                    "industry_id": industry,
                    "industry_name": industry.replace("_", " ").title(),
                    "framework": industry_summary["framework"],
                    "metrics_count": industry_summary["total_metrics"],
                    "categories": industry_summary["categories"],
                    "calculation_models": industry_summary["metrics_with_models"]
                })
            
            return jsonify({
                "status": "success",
                "framework_id": framework_id,
                "data": industries,
                "count": len(industries)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_categories_by_industry(self, industry_id):
        """Get categories available for a specific industry"""
        try:
            # Check if industry exists by trying to get framework
            try:
                self.kg_service.cq1_reporting_framework_by_industry(industry_id)
            except ValueError:
                return jsonify({"status": "error", "message": "Industry not found"}), 404
            
            # Use CQ2 to get categories
            cq2_result = self.kg_service.cq2_categories_by_framework(industry_id)
            categories = cq2_result.get("categories", [])
            category_details = []
            
            framework_data = self.data_service.load_framework_data(industry_id)
            metrics_by_category = {}
            
            for metric in framework_data["metrics"]:
                category = metric.get("category", "Other")
                if category not in metrics_by_category:
                    metrics_by_category[category] = []
                metrics_by_category[category].append(metric)
            
            for category in categories:
                category_metrics = metrics_by_category.get(category, [])
                category_details.append({
                    "category_id": category.replace(" ", "_").lower(),
                    "category_name": category,
                    "metrics_count": len(category_metrics),
                    "has_calculation_models": any(m.get("model_name") != "n/a" for m in category_metrics),
                    "description": f"ESG metrics related to {category}"
                })
            
            return jsonify({
                "status": "success",
                "industry_id": industry_id,
                "data": category_details,
                "count": len(category_details)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_metrics_by_category(self, category):
        """Step 5: Get metrics available for a specific category using Knowledge Graph Service (CQ3)"""
        try:
            print(f"📊 Step 5: Getting metrics for category {category} using Knowledge Graph Service")
            
            # Get industry from request parameter
            industry = request.args.get('industry')
            if not industry:
                return jsonify({
                    "status": "error", 
                    "error_category": "MISSING_INDUSTRY",
                    "user_message": "Industry parameter required",
                    "suggestion": "Please provide industry parameter",
                    "technical_message": "Missing industry parameter in request"
                }), 400
            
            # Convert category_id back to readable format
            category_mapping = {
                "greenhouse_gas_emissions": "Greenhouse Gas Emissions",
                "energy_management_in_manufacturing": "Energy Management in Manufacturing", 
                "water_management": "Water Management",
                "waste_management": "Waste Management",
                "workforce_health_&_safety": "Workforce Health & Safety",
                "recruiting_&_managing_a_global_&_skilled_workforce": "Recruiting & Managing a Global & Skilled Workforce",
                "product_lifecycle_management": "Product Lifecycle Management",
                "materials_sourcing": "Materials Sourcing",
                "intellectual_property_protection_&_competitive_behaviour": "Intellectual Property Protection & Competitive Behaviour"
            }
            
            category_name = category_mapping.get(category, category.replace("_", " ").title())
            
            # Use CQ3 to get metrics from Knowledge Graph Service
            cq3_result = self.kg_service.cq3_metrics_by_category(industry, category_name)
            metrics = cq3_result.get("metrics", [])
            
            # Process metrics with calculation information
            processed_metrics = []
            for metric in metrics:
                try:
                    # Get calculation method using CQ4
                    metric_name = metric.get("metric_name")
                    cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric_name)
                    
                    processed_metrics.append({
                        "metric_id": metric.get("code"),
                        "metric_code": metric.get("code"),
                        "metric_name": metric.get("metric_name"),
                        "description": metric.get("metric_description"),
                        "unit": metric.get("unit"),
                        "metric_type": metric.get("metric_type"),
                        "category": category_name,
                        "industry": industry,
                        "calculation_method": cq4_result.get("measurement_method", "direct_measurement"),
                        "model_name": cq4_result.get("model_name", "Direct access"),
                        "has_calculation_model": cq4_result.get("measurement_method") == "calculation_model",
                        "data_access_type": "Model-based calculation" if cq4_result.get("measurement_method") == "calculation_model" else "Direct access",
                        "service_used": "knowledge_graph_service",
                        "cq_queries": ["CQ3", "CQ4"]
                    })
                except Exception as e:
                    print(f"⚠️ Error processing metric {metric.get('metric_name')}: {str(e)}")
                    # Create fallback entry
                    processed_metrics.append({
                        "metric_id": metric.get("code"),
                        "metric_code": metric.get("code"),
                        "metric_name": metric.get("metric_name"),
                        "category": category_name,
                        "industry": industry,
                        "calculation_method": "direct_measurement",
                        "has_calculation_model": False,
                        "data_access_type": "Direct access",
                        "service_used": "knowledge_graph_service",
                        "cq_queries": ["CQ3"]
                    })
            
            print(f"📊 Step 5 Complete: Found {len(processed_metrics)} metrics for {category_name} via CQ3")
            return jsonify({
                "status": "success",
                "category_id": category,
                "category_name": category_name,
                "industry": industry,
                "data": processed_metrics,
                "count": len(processed_metrics),
                "service_used": "knowledge_graph_service",
                "cq_queries_used": ["CQ3: Metrics by Category", "CQ4: Calculation Method"],
                "message": f"Metrics retrieved from RDF Knowledge Graph for {category_name} category"
            })
        except Exception as e:
            print(f"❌ Step 5 Error: {str(e)}")
            return jsonify({
                "status": "error", 
                "error_category": "KNOWLEDGE_GRAPH_ACCESS_ERROR",
                "user_message": "Error accessing metrics data",
                "suggestion": "Please check knowledge graph availability and try again",
                "technical_message": str(e)
            }), 500
    
    def get_metric_details(self, metric_id):
        """Get detailed information about a specific metric"""
        try:
            # Search for metric across all industries
            for industry in self.data_service.get_available_industries():
                try:
                    # Use CQ4 to get calculation method
                    cq4_result = self.kg_service.cq4_metric_calculation_method(industry, metric_id)
                    
                    # Get required datapoints if it's a calculated metric
                    required_datapoints = []
                    if cq4_result.get("measurement_method") == "calculation_model":
                        try:
                            # Use CQ5 to get required datapoints
                            cq5_result = self.kg_service.cq5_model_input_datapoints(
                                industry, cq4_result.get("model_name"), self.calc_service
                            )
                            required_datapoints = cq5_result.get("required_datapoints", [])
                        except Exception:
                            required_datapoints = []
                    
                    # Mock coverage stats (replace with real implementation when available)
                    coverage_stats = {
                        "coverage_rate": 0.8,
                        "total_datapoints": len(required_datapoints),
                        "available_datapoints": len(required_datapoints)
                    }
                    
                    return jsonify({
                        "status": "success",
                        "metric_id": metric_id,
                        "industry": industry,
                        "metric_name": cq4_result.get("metric_name"),
                        "calculation_method": cq4_result.get("measurement_method"),
                        "model_name": cq4_result.get("model_name"),
                        "model_description": cq4_result.get("model_description"),
                        "unit": cq4_result.get("unit"),
                        "required_datapoints": required_datapoints,
                        "data_coverage": coverage_stats,
                        "can_calculate": len(required_datapoints) > 0 and coverage_stats["coverage_rate"] > 0.5
                    })
                except ValueError:
                    continue
            
            return jsonify({"status": "error", "message": "Metric not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # ==================== COMPANY & YEAR SELECTION APIS ====================
    
    def get_available_companies(self):
        """Get available companies for selection from external dataset"""
        try:
            industry = request.args.get('industry')
            
            # Use consolidated data retrieval service
            external_service = self.data_service
            
            result = external_service.get_available_companies(industry)
            return jsonify({
                "status": "success",
                "data": result,
                "industry_filter": industry
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_company_years(self, company_name):
        """Get available years for a specific company and determine its industry"""
        try:
            # Use consolidated data retrieval service
            external_service = self.data_service
            
            years = external_service.get_available_years(company_name)
            
            # Get company's industry from external dataset
            company_industry = external_service.get_company_industry(company_name)
            
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "available_years": years,
                "company_industry": company_industry,
                "count": len(years)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_company_metrics(self, company_name):
        """Get all metrics for a company in a specific year"""
        try:
            year = request.args.get('year', '2023')
            
            # Use consolidated data retrieval service  
            external_service = self.data_service
            
            result = external_service.get_company_metrics(company_name, year)
            return jsonify({
                "status": "success",
                "data": result
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # ==================== CALCULATION APIs ====================
    
    def calculate_metrics(self):
        """Execute metric calculations with NO DEMO DATA - real data only with clear reasons"""
        try:
            data = request.get_json()
            
            # Validate input
            if not data:
                return jsonify({
                    "status": "error", 
                    "message": "No data provided"
                }), 400
            
            # Extract parameters
            industry = data.get("industry")
            metrics = data.get("metrics", data.get("selected_metrics", []))
            company_name = data.get("company_name", data.get("company_data", {}).get("company_name"))
            year = data.get("year", data.get("company_data", {}).get("year", "2024"))
            
            if not industry:
                return jsonify({
                    "status": "error", 
                    "message": "Industry is required"
                }), 400
                
            if not metrics:
                return jsonify({
                    "status": "error", 
                    "message": "At least one metric is required"
                }), 400
                
            if not company_name:
                return jsonify({
                    "status": "error", 
                    "message": "Company name is required"
                }), 400
            
            print(f"🔍 API: Calculating {len(metrics)} metrics for {company_name} ({year})")
            
            # Remove duplicates from request while preserving original metric codes
            unique_metrics = []
            seen_metric_names = set()
            
            for metric in metrics:
                # Convert to user-friendly name to check for duplicates
                user_friendly_name = self.calc_service._convert_to_user_friendly_name(metric, industry)
                if user_friendly_name not in seen_metric_names:
                    unique_metrics.append(metric)
                    seen_metric_names.add(user_friendly_name)
                else:
                    print(f"⚠️ Removed duplicate metric: {metric} -> {user_friendly_name}")
            
            # Get already calculated metrics to prevent duplicates
            try:
                existing_calculations = self.calc_service.memory_service.get_all_calculated_metrics_for_company(company_name, year)
                already_calculated = existing_calculations.get("calculated_metrics", {})
            except:
                already_calculated = {}
            
            # Filter out already calculated metrics and track duplicates
            metrics_to_calculate = []
            duplicate_metrics = []
            for metric in unique_metrics:
                metric_key = self.calc_service._convert_to_user_friendly_name(metric, industry)
                if metric_key in already_calculated:
                    duplicate_metrics.append({
                        "metric_name": metric_key,
                        "metric_code": metric,
                        "status": "already_calculated",
                        "previous_calculation": already_calculated[metric_key],
                        "message": "✅ Previously calculated - using cached result"
                    })
                else:
                    metrics_to_calculate.append(metric)
            
            # Calculate only new metrics
            calculation_results = []
            start_time = time.time()
            
            # Add duplicate results (from memory)
            for duplicate in duplicate_metrics:
                calculation_results.append(duplicate)
                print(f"🔄 Using cached: {duplicate['metric_code']} -> already_calculated")
            
            # Calculate new metrics
            for metric in metrics_to_calculate:
                try:
                    result = self.calc_service.calculate(metric, company_name, str(year), industry)
                    calculation_results.append(result)
                    print(f"✅ Calculated: {metric} -> {result.get('status')}")
                except Exception as e:
                    print(f"❌ Error calculating {metric}: {str(e)}")
                    calculation_results.append({
                        "metric_name": metric,
                        "status": "calculation_error",
                        "value": None,
                        "display_value": "Calculation failed",
                        "reason": f"Error: {str(e)}",
                        "company_name": company_name,
                        "year": year
                    })
            
            total_time = time.time() - start_time
            
            # Analyze results
            real_data_count = sum(1 for r in calculation_results if r.get("data_source") == "external_dataset")
            calculated_count = sum(1 for r in calculation_results if r.get("data_source") == "calculated_from_real_data")
            unavailable_count = sum(1 for r in calculation_results if r.get("status") in ["data_unavailable", "failed_no_data"])
            cached_count = len(duplicate_metrics)
            
            return jsonify({
                "status": "success",
                "calculation_results": calculation_results,
                "summary": {
                    "company_name": company_name,
                    "year": year,
                    "industry": industry,
                    "metrics_requested": len(metrics),
                    "unique_metrics_processed": len(unique_metrics),
                    "metrics_already_calculated": cached_count,
                    "metrics_newly_calculated": len(metrics_to_calculate),
                    "metrics_with_real_data": real_data_count,
                    "metrics_calculated_from_real_data": calculated_count,
                    "metrics_unavailable": unavailable_count,
                    "duplicates_removed": len(metrics) - len(unique_metrics),
                    "total_calculation_time": f"{total_time:.3f}s",
                    "data_policy": "No demo data - real data only with clear reasons",
                    "duplicate_prevention": f"Removed {len(metrics) - len(unique_metrics)} duplicates, prevented {cached_count} recalculations"
                },
                "data_transparency": {
                    "authenticity_policy": "No fake/demo data provided",
                    "unavailable_data_policy": "Clear reasons provided when data unavailable",
                    "calculation_engine": "Direct calculation service - no demo fallbacks",
                    "cache_policy": "Previously calculated metrics retrieved from memory"
                }
            })
            
        except Exception as e:
            print(f"❌ Calculate endpoint error: {str(e)}")
            return jsonify({
                "status": "error", 
                "message": f"Calculation failed: {str(e)}",
                "debug_info": {
                    "error_type": type(e).__name__,
                    "endpoint": "calculate_metrics"
                }
            }), 500
    
    def get_model_input_requirements(self, model_id):
        """Get input requirements for a specific calculation model"""
        try:
            # Find model across industries
            for industry in self.data_service.get_available_industries():
                required_inputs = self.kg_service.get_required_datapoints(industry, model_id)
                
                if required_inputs:
                    return jsonify({
                        "status": "success",
                        "model_id": model_id,
                        "industry": industry,
                        "required_inputs": required_inputs,
                        "input_count": len(required_inputs),
                        "example_inputs": {
                            input_name: f"example_value_for_{input_name.lower()}"
                            for input_name in required_inputs[:3]  # Show first 3 as examples
                        }
                    })
            
            return jsonify({"status": "error", "message": "Model not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_calculable_metrics(self, industry):
        """Get metrics that can be calculated for a specific industry"""
        try:
            calculable_metrics = self.kg_service.get_calculable_metrics(industry)
            return jsonify({
                "status": "success",
                "industry": industry,
                "data": calculable_metrics,
                "count": len(calculable_metrics)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # ==================== MEMORY AND SESSION MANAGEMENT APIs ====================
    
    def get_memory_summary(self):
        """Get calculation memory summary"""
        try:
            memory_summary = self.calc_service.get_memory_summary()
            return jsonify({
                "status": "success",
                "memory_summary": memory_summary,
                "message": "Calculation memory summary retrieved"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_company_calculations(self, company_name, year):
        """Get all calculated metrics for a company across categories"""
        try:
            calculations = self.calc_service.get_all_calculated_metrics(company_name, year)
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "year": year,
                "calculations": calculations,
                "message": f"All calculations for {company_name} in {year}"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_session_calculations(self, session_id):
        """Get calculations for a specific session"""
        try:
            session_data = self.calc_service.memory_service.get_session_calculations(session_id)
            return jsonify({
                "status": "success",
                "session_id": session_id,
                "session_data": session_data,
                "message": f"Session calculations for {session_id}"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # ==================== REPORT GENERATION APIs ====================
    
    def generate_report(self):
        """Generate comprehensive ESG report using Report Service"""
        try:
            data = request.get_json()
            
            required_fields = ["industry", "selected_metrics", "company_info"]
            for field in required_fields:
                if field not in data:
                    return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
            
            industry = data["industry"]
            selected_metrics = data["selected_metrics"]
            company_info = data["company_info"]
            
            # NEW: Get pre-calculated metrics from frontend if available
            all_calculated_metrics = data.get("all_calculated_metrics", [])
            
            print(f"📋 Report generation request:")
            print(f"   📊 Industry: {industry}")
            print(f"   📈 Selected metrics: {len(selected_metrics)}")
            print(f"   💾 Pre-calculated metrics: {len(all_calculated_metrics)}")
            
            # Generate report using dedicated Report Service
            # Pass the pre-calculated metrics to avoid re-computation
            result = self.report_service.generate_esg_compliance_report(
                industry=industry,
                selected_metrics=selected_metrics,
                company_info=company_info,
                pre_calculated_metrics=all_calculated_metrics  # Pass the calculated metrics
            )
            
            if result["status"] == "success":
                return jsonify({
                    "status": "success",
                    "report_id": result["report_id"],
                    "report": result["report"],
                    "generation_time": result["generation_time"],
                    "download_url": f"/api/v1/reports/{result['report_id']}"
                })
            else:
                return jsonify(result), 500
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def generate_word_report(self):
        """Generate ESG report in Word format"""
        try:
            from flask import send_file
            data = request.get_json()

            # Extract report data
            calculations = data.get("calculations", [])
            company_name = data.get("company_name", "Unknown Company")
            year = data.get("year", "N/A")
            industry = data.get("industry", "N/A")

            if not calculations:
                return jsonify({
                    "status": "error",
                    "message": "No calculations provided for report generation"
                }), 400

            # Filter to only include successfully calculated metrics (both direct and calculated)
            successful_calculations = [
                calc for calc in calculations
                if calc.get('status') == 'success'
            ]

            print(f"📄 Generating Word report: {len(successful_calculations)} metrics")
            print(f"   Categories found: {set([c.get('category', 'N/A') for c in successful_calculations])}")
            print(f"   Sample metric: {successful_calculations[0] if successful_calculations else 'None'}")

            # Prepare data for Word report
            report_data = {
                "company_name": company_name,
                "year": year,
                "industry": industry,
                "framework": f"SASB {industry.replace('_', ' ').title()}",
                "calculations": successful_calculations,
                "quality_score": data.get("quality_score", 85)
            }

            # Generate Word document using new ReportService
            result = self.report_service.generate_word_report(report_data)

            # Check if generation was successful
            if result.get("status") != "success":
                return jsonify({
                    "status": "error",
                    "message": result.get("message", "Failed to generate Word report")
                }), 500

            return jsonify({
                "status": "success",
                "message": "Word report generated successfully",
                "filename": result.get("filename"),
                "download_url": result.get("download_url"),
                "metrics_count": len(successful_calculations)
            })

        except Exception as e:
            print(f"❌ Error generating Word report: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def generate_pdf_report(self):
        """Generate ESG report in PDF format"""
        try:
            from flask import send_file
            data = request.get_json()

            # Extract report data
            calculations = data.get("calculations", [])
            company_name = data.get("company_name", "Unknown Company")
            year = data.get("year", "N/A")
            industry = data.get("industry", "N/A")

            if not calculations:
                return jsonify({
                    "status": "error",
                    "message": "No calculations provided for report generation"
                }), 400

            # Filter to only include successfully calculated metrics (both direct and calculated)
            successful_calculations = [
                calc for calc in calculations
                if calc.get('status') == 'success'
            ]

            print(f"📄 Generating PDF report: {len(successful_calculations)} metrics")
            print(f"   Categories found: {set([c.get('category', 'N/A') for c in successful_calculations])}")
            print(f"   Sample metric: {successful_calculations[0] if successful_calculations else 'None'}")

            # Prepare data for PDF report
            report_data = {
                "company_name": company_name,
                "year": year,
                "industry": industry,
                "framework": f"SASB {industry.replace('_', ' ').title()}",
                "calculations": successful_calculations,
                "quality_score": data.get("quality_score", 85)
            }

            # Generate PDF document using new ReportService
            result = self.report_service.generate_pdf_report(report_data)

            # Check if generation was successful
            if result.get("status") != "success":
                return jsonify({
                    "status": "error",
                    "message": result.get("message", "Failed to generate PDF report")
                }), 500

            return jsonify({
                "status": "success",
                "message": "PDF report generated successfully",
                "filename": result.get("filename"),
                "download_url": result.get("download_url"),
                "metrics_count": len(successful_calculations)
            })

        except Exception as e:
            print(f"❌ Error generating PDF report: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def download_report(self, filename):
        """Download a generated report file"""
        try:
            from flask import send_file

            # Use ReportService to get the file path
            filepath = self.report_service.get_report_file(filename)

            if not filepath:
                return jsonify({
                    "status": "error",
                    "message": "Report file not found"
                }), 404

            # Determine MIME type based on file extension
            if filename.endswith('.pdf'):
                mimetype = 'application/pdf'
            elif filename.endswith('.docx'):
                mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                mimetype = 'application/octet-stream'

            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )

        except Exception as e:
            print(f"❌ Error downloading report: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def get_report(self, report_id):
        """Retrieve a generated report using Report Service"""
        try:
            report = self.report_service.get_report(report_id)
            if not report:
                return jsonify({"status": "error", "message": "Report not found"}), 404
            
            return jsonify({
                "status": "success",
                "report_id": report_id,
                "report": report
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_report_lineage(self, report_id):
        """Get detailed data lineage for a report using Report Service"""
        try:
            result = self.report_service.generate_data_lineage_report(report_id)
            
            if result["status"] == "success":
                return jsonify({
                    "status": "success",
                    "lineage": result["report"]
                })
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def list_reports(self):
        """List all generated reports with filtering options"""
        try:
            report_type = request.args.get('type')
            limit = int(request.args.get('limit', 50))
            
            reports = self.report_service.list_reports(report_type=report_type, limit=limit)
            
            return jsonify({
                "status": "success",
                "data": reports,
                "count": len(reports),
                "filters_applied": {
                    "type": report_type,
                    "limit": limit
                }
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def generate_cross_industry_report(self):
        """Generate cross-industry comparison report"""
        try:
            data = request.get_json()
            industries = data.get("industries", [])
            
            if not industries:
                industries = list(self.data_service.get_available_industries())
            
            result = self.report_service.generate_cross_industry_comparison_report(industries)
            
            if result["status"] == "success":
                return jsonify({
                    "status": "success",
                    "report_id": result["report_id"],
                    "report": result["report"],
                    "comparison_url": f"/api/v1/reports/{result['report_id']}"
                })
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # ==================== SPARQL APIs ====================
    
    def execute_sparql_query(self):
        """Execute custom SPARQL query"""
        try:
            data = request.get_json()
            
            if "query" not in data:
                return jsonify({"status": "error", "message": "Missing SPARQL query"}), 400
            
            sparql_query = data["query"]
            result = self.kg_service.execute_sparql_query(sparql_query)
            
            # Convert results to JSON-serializable format
            processed_results = []
            for row in result["results"]:
                processed_row = {}
                for var in row.labels:
                    processed_row[str(var)] = str(row[var])
                processed_results.append(processed_row)
            
            return jsonify({
                "status": "success",
                "query": sparql_query,
                "results": processed_results,
                "result_count": result["result_count"],
                "query_time_seconds": result["query_time"],
                "performance_info": {
                    "queries_per_second": 1 / result["query_time"] if result["query_time"] > 0 else float('inf'),
                    "graph_size_triples": len(self.kg_service.rdf_graph)
                }
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def execute_predefined_query(self, query_id):
        """Execute predefined SPARQL queries"""
        predefined_queries = {
            "all_industries": "SELECT DISTINCT ?industry WHERE { ?industry a esg:Industry }",
            "all_frameworks": "SELECT ?industry ?framework WHERE { ?industry esg:ReportUsing ?framework }",
            "metrics_with_models": "SELECT ?metric ?model WHERE { ?metric esg:IsCalculatedBy ?model }"
        }
        
        if query_id not in predefined_queries:
            return jsonify({"status": "error", "message": "Predefined query not found"}), 404
        
        try:
            result = self.kg_service.execute_sparql_query(predefined_queries[query_id])
            return jsonify({
                "status": "success",
                "query_id": query_id,
                "result_count": result["result_count"],
                "query_time_seconds": result["query_time"]
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # ==================== PERFORMANCE & ANALYTICS APIs ====================
    
    def get_performance_metrics(self):
        """Get system performance metrics"""
        return jsonify({
            "status": "success",
            "performance_metrics": {
                "total_api_requests": self.api_metrics["total_requests"],
                "average_response_time_seconds": self.api_metrics["avg_response_time"],
                "error_rate_percentage": (self.api_metrics["error_count"] / max(self.api_metrics["total_requests"], 1)) * 100,
                "knowledge_graph_size": {
                    "total_triples": len(self.kg_service.rdf_graph),
                    "industries_loaded": len(self.kg_service.industries),
                    "graph_build_time": "< 1 second"
                },
                "sparql_engine": {
                    "engine": "rdflib",
                    "query_optimization": "enabled",
                    "concurrent_support": "thread-safe"
                }
            }
        })
    
    def get_data_coverage_analytics(self):
        """Get data coverage analytics across industries"""
        coverage_analytics = {}
        
        for industry in self.data_service.get_available_industries():
            coverage_stats = self.kg_service.get_data_coverage_stats(industry)
            coverage_analytics[industry] = coverage_stats
        
        return jsonify({
            "status": "success",
            "coverage_analytics": coverage_analytics,
            "aggregate_stats": {
                "average_coverage_rate": sum(stats["coverage_rate"] for stats in coverage_analytics.values()) / len(coverage_analytics),
                "total_alignments": sum(stats["total_alignments"] for stats in coverage_analytics.values()),
                "high_confidence_percentage": sum(stats["high_confidence_count"] for stats in coverage_analytics.values()) / sum(stats["total_alignments"] for stats in coverage_analytics.values()) * 100 if sum(stats["total_alignments"] for stats in coverage_analytics.values()) > 0 else 0
            }
        })
    
    def get_api_usage_analytics(self):
        """Get API usage analytics"""
        if not self.api_metrics["request_history"]:
            return jsonify({
                "status": "success",
                "message": "No usage data available yet"
            })
        
        # Analyze recent requests
        recent_requests = self.api_metrics["request_history"][-100:]  # Last 100 requests
        
        endpoint_usage = {}
        for req in recent_requests:
            endpoint = req["endpoint"] or "unknown"
            if endpoint not in endpoint_usage:
                endpoint_usage[endpoint] = {"count": 0, "avg_response_time": 0, "total_time": 0}
            endpoint_usage[endpoint]["count"] += 1
            endpoint_usage[endpoint]["total_time"] += req["response_time"]
        
        # Calculate averages
        for endpoint, stats in endpoint_usage.items():
            stats["avg_response_time"] = stats["total_time"] / stats["count"]
            del stats["total_time"]
        
        return jsonify({
            "status": "success",
            "usage_analytics": {
                "total_requests": self.api_metrics["total_requests"],
                "recent_requests_analyzed": len(recent_requests),
                "endpoint_usage": endpoint_usage,
                "performance_summary": {
                    "fastest_endpoint": min(endpoint_usage.items(), key=lambda x: x[1]["avg_response_time"])[0] if endpoint_usage else None,
                    "slowest_endpoint": max(endpoint_usage.items(), key=lambda x: x[1]["avg_response_time"])[0] if endpoint_usage else None,
                    "most_used_endpoint": max(endpoint_usage.items(), key=lambda x: x[1]["count"])[0] if endpoint_usage else None
                }
            }
        })
    
    # ==================== SYSTEM APIs ====================
    
    def health_check(self):
        """Health check endpoint"""
        try:
            # Test key components
            kg_health = len(self.kg_service.rdf_graph) > 0
            data_health = len(self.data_service.get_available_industries()) > 0
            
            return jsonify({
                "status": "healthy" if kg_health and data_health else "degraded",
                "components": {
                    "knowledge_graph": "healthy" if kg_health else "unhealthy",
                    "data_service": "healthy" if data_health else "unhealthy",
                    "calculation_service": "healthy",
                    "api_server": "healthy"
                },
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    def get_system_info(self):
        """Get system information"""
        return jsonify({
            "status": "success",
            "system_info": {
                "name": "Ontometric System",
                "version": "1.0.0",
                "description": "Knowledge graph-driven ESG reporting system with SASB framework support",
                "capabilities": [
                    "Multi-industry ESG reporting",
                    "SPARQL query execution",
                    "Automated metric calculation",
                    "Data lineage tracking",
                    "Performance analytics",
                    "REST API with OpenAPI specification"
                ],
                "supported_industries": list(self.data_service.get_available_industries()),
                "supported_frameworks": ["SASB"],
                "knowledge_graph": {
                    "total_triples": len(self.kg_service.rdf_graph),
                    "namespace": "http://example.org/esg#",
                    "query_engine": "rdflib SPARQL"
                },
                "api_version": "v1",
                "documentation": "/api/v1/openapi.json"
            }
        })
    
    def get_openapi_spec(self):
        """Return OpenAPI 3.0 specification"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "ESG Knowledge Graph API",
                "version": "1.0.0",
                "description": "Comprehensive REST API for ESG knowledge graph-driven reporting system",
                "contact": {
                    "name": "ESG Research Team",
                    "email": "esg-research@example.com"
                }
            },
            "servers": [
                {"url": "http://localhost:5000", "description": "Development server"}
            ],
            "paths": {
                "/api/v1/frameworks": {
                    "get": {
                        "summary": "Get all available reporting frameworks",
                        "responses": {
                            "200": {"description": "List of frameworks with industry mappings"}
                        }
                    }
                },
                "/api/v1/industries/{industry_id}/categories": {
                    "get": {
                        "summary": "Get categories for a specific industry",
                        "parameters": [
                            {
                                "name": "industry_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "example": "semiconductors"
                            }
                        ],
                        "responses": {
                            "200": {"description": "List of categories with metrics count"}
                        }
                    }
                },
                "/api/v1/calculate": {
                    "post": {
                        "summary": "Calculate ESG metrics",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "industry": {"type": "string"},
                                            "metrics": {"type": "array", "items": {"type": "string"}},
                                            "company_data": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Calculation results with lineage information"}
                        }
                    }
                },
                "/api/v1/reports/generate": {
                    "post": {
                        "summary": "Generate comprehensive ESG report",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "industry": {"type": "string"},
                                            "selected_metrics": {"type": "array"},
                                            "company_info": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Generated report with transparency information"}
                        }
                    }
                },
                "/api/v1/sparql/query": {
                    "post": {
                        "summary": "Execute custom SPARQL query",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string", "description": "SPARQL query string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Query results with performance metrics"}
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Framework": {
                        "type": "object",
                        "properties": {
                            "framework_id": {"type": "string"},
                            "framework_name": {"type": "string"},
                            "industry": {"type": "string"},
                            "categories_count": {"type": "integer"}
                        }
                    },
                    "Metric": {
                        "type": "object",
                        "properties": {
                            "metric_id": {"type": "string"},
                            "metric_name": {"type": "string"},
                            "category": {"type": "string"},
                            "unit": {"type": "string"},
                            "calculation_method": {"type": "string", "enum": ["model", "direct_measurement"]}
                        }
                    }
                }
            }
        }
        
        return jsonify(spec)
    
    # ==================== COMPREHENSIVE EVALUATION APIs ====================
    
    def run_comprehensive_evaluation(self):
        """Run comprehensive system evaluation — generates performance diagram"""
        try:
            self.create_performance_diagram()
            return jsonify({
                "status": "success",
                "evaluation_type": "performance_diagram",
                "message": "Comprehensive performance diagram generated",
                "output": "src/evaluation/comprehensive_performance_analysis.png"
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Performance evaluation failed: {str(e)}",
                "error_type": "evaluation_error"
            }), 500

    def get_cq_performance(self):
        """Get competency question performance summary"""
        try:
            from src.evaluation.performance_evaluator import load_evaluation_data
            data = load_evaluation_data()
            service_perf = data["performance_results"]["service_performance"]
            tat_perf = data["performance_results"]["tat_performance"]
            return jsonify({
                "status": "success",
                "service_performance": service_perf,
                "tat_performance": tat_perf
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Performance data retrieval failed: {str(e)}"
            }), 500

    def get_quick_summary(self):
        """Get quick system performance summary"""
        try:
            from src.evaluation.performance_evaluator import load_evaluation_data
            data = load_evaluation_data()
            tat = data["performance_results"]["tat_performance"]
            return jsonify({
                "status": "success",
                "performance_summary": {
                    "transparency_score": tat["transparency"]["overall_transparency_score"],
                    "adaptability_score": tat["adaptability"]["overall_adaptability_score"],
                    "traceability_score": tat["traceability"]["overall_traceability_score"]
                },
                "system_status": "operational"
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Performance summary failed: {str(e)}"
            }), 500

    def serve_web_interface(self):
        """Serve the enhanced web interface"""
        return render_template('enhanced_demo.html')
    
    def industry_summary_legacy(self):
        """Legacy endpoint for industry summary"""
        return self.get_frameworks()
    
    def generate_report_legacy(self, industry):
        """Legacy endpoint for report generation"""
        try:
            if industry not in self.kg_service.industries:
                return jsonify({"status": "error", "message": "Industry not found"}), 404
                
            industry_summary = self.kg_service.industries[industry]
            return jsonify({
                "status": "success",
                "industry": industry,
                "industry_summary": industry_summary,
                "message": f"Legacy endpoint - use /api/v1/reports/generate for full functionality"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    
    def compare_industries_legacy(self):
        """Legacy endpoint for industry comparison"""
        try:
            industries = self.data_service.get_available_industries()
            comparison = {}
            
            for industry in industries:
                coverage_stats = self.kg_service.get_data_coverage_stats(industry)
                industry_summary = self.kg_service.industries[industry]
                
                comparison[industry] = {
                    "framework": industry_summary["framework"],
                    "total_metrics": industry_summary["total_metrics"],
                    "coverage_rate": coverage_stats["coverage_rate"],
                    "automation_level": "High" if coverage_stats["coverage_rate"] > 0.7 else "Medium",
                    "metrics_with_models": industry_summary["metrics_with_models"]
                }
            
            return jsonify({
                "status": "success",
                "comparison": comparison,
                "service_reuse_rate": 100,
                "key_insights": [
                    "100% service architecture reuse across industries",
                    "Data alignment quality directly impacts automation level", 
                    "Same service interfaces adapt to different workflow patterns"
                ]
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # ==================== ERROR HANDLERS ====================
    
    def handle_bad_request(self, e):
        return jsonify({
            "status": "error",
            "error_code": 400,
            "message": "Bad request - please check your input parameters",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    def handle_not_found(self, e):
        return jsonify({
            "status": "error",
            "error_code": 404,
            "message": "Resource not found",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    def handle_internal_error(self, e):
        return jsonify({
            "status": "error",
            "error_code": 500,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }), 500
    
    # ==================== HELPER METHODS ====================
    
    def _generate_recommendations(self, industry: str, coverage_stats: Dict) -> List[str]:
        """Generate recommendations based on coverage statistics"""
        recommendations = []
        
        if coverage_stats["coverage_rate"] < 0.5:
            recommendations.append("Consider improving data quality to increase automation opportunities")
        
        if coverage_stats["high_confidence_count"] < coverage_stats["total_alignments"] * 0.3:
            recommendations.append("Review data alignment methodologies to improve confidence scores")
        
        if self.kg_service.industries[industry]["metrics_with_models"] > 5:
            recommendations.append("High model complexity detected - ensure input data quality for accurate calculations")
        
        recommendations.append("Regular framework updates recommended to maintain compliance")
        
        return recommendations
    
    def _store_report(self, report_id: str, report: Dict):
        """Store report (in-memory for demo, would be database in production)"""
        if not hasattr(self, '_report_store'):
            self._report_store = {}
        self._report_store[report_id] = report
    
    def _retrieve_report(self, report_id: str) -> Optional[Dict]:
        """Retrieve report (in-memory for demo, would be database in production)"""
        if not hasattr(self, '_report_store'):
            return None
        return self._report_store.get(report_id)

    def check_data_availability(self, company_name, year):
        """Check data availability for a specific company and year"""
        try:
            # Get industry parameter for context
            industry = request.args.get('industry', 'semiconductors')
            
            # Get all metrics for the industry from the knowledge graph
            try:
                # Use CQ1 to get framework, then get all metrics
                cq1_result = self.kg_service.cq1_reporting_framework_by_industry(industry)
                framework_name = cq1_result.get("framework_name", f"SASB {industry.title()}")
                
                # Get all categories and their metrics
                cq2_result = self.kg_service.cq2_categories_by_industry(industry)
                categories = cq2_result.get("categories", [])
                
                all_metrics = []
                for category in categories:
                    cq3_result = self.kg_service.cq3_metrics_by_category(industry, category)
                    metrics = cq3_result.get("metrics", [])
                    all_metrics.extend([m.get("metric_name") for m in metrics if m.get("metric_name")])
                
            except Exception as e:
                print(f"⚠️ Error getting metrics from knowledge graph: {e}")
                # Fallback to a basic set of metrics
                all_metrics = [
                    "Gross Global Scope 1 Emissions",
                    "Total Energy Consumed", 
                    "Percentage Grid Electricity",
                    "Percentage Renewable Energy",
                    "Total Water Withdrawn",
                    "Total Water Consumed"
                ]
            
            # Check data availability for all metrics
            availability_result = self.data_service.check_data_availability(
                company_name, year, all_metrics
            )
            
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "year": year,
                "industry": industry,
                "framework": framework_name,
                "data_availability": availability_result,
                "frontend_guidance": {
                    "selectable_metrics": [m["metric_name"] for m in availability_result.get("available_metrics", [])],
                    "disabled_metrics": [m["metric_name"] for m in availability_result.get("unavailable_metrics", [])],
                    "suggestion": availability_result.get("suggestion", "")
                }
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def check_multiple_data_availability(self):
        """Check data availability for multiple companies/years"""
        try:
            data = request.json
            checks = data.get('checks', [])  # List of {company_name, year, industry}
            
            results = []
            for check in checks:
                company_name = check.get('company_name')
                year = check.get('year')
                industry = check.get('industry', 'semiconductors')
                
                if not company_name or not year:
                    results.append({
                        "company_name": company_name,
                        "year": year,
                        "status": "error",
                        "message": "Missing company_name or year"
                    })
                    continue
                
                # Get metrics for this industry
                try:
                    cq2_result = self.kg_service.cq2_categories_by_industry(industry)
                    categories = cq2_result.get("categories", [])
                    
                    all_metrics = []
                    for category in categories:
                        cq3_result = self.kg_service.cq3_metrics_by_category(industry, category)
                        metrics = cq3_result.get("metrics", [])
                        all_metrics.extend([m.get("metric_name") for m in metrics if m.get("metric_name")])
                except:
                    all_metrics = ["Gross Global Scope 1 Emissions", "Total Energy Consumed"]
                
                # Check availability
                availability = self.data_service.check_data_availability(
                    company_name, year, all_metrics
                )
                
                results.append({
                    "company_name": company_name,
                    "year": year,
                    "industry": industry,
                    "availability": availability,
                    "selectable_count": len(availability.get("available_metrics", [])),
                    "unavailable_count": len(availability.get("unavailable_metrics", []))
                })
            
            return jsonify({
                "status": "success",
                "results": results,
                "summary": {
                    "total_checks": len(checks),
                    "successful_checks": len([r for r in results if r.get("availability", {}).get("status") == "checked"])
                }
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

# Flask App Factory
def create_app():
    api = ESGKnowledgeGraphAPI()
    return api.app

if __name__ == '__main__':
    # Import port manager for consistent port handling
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.port_manager import PortManager
    
    app = create_app()
    print("🚀 Starting ESG Knowledge Graph API Server")
    print("📖 API Documentation: http://localhost:5000/api/v1/openapi.json")
    print("🌐 Web Interface: http://localhost:5000/")
    
    # Use port manager for consistent and clean port handling
    PortManager.run_flask_app_with_port_management(app, host='0.0.0.0', preferred_port=5000, debug=True) 