#!/usr/bin/env python3
"""
Comprehensive Performance Diagram Generator

Creates a single comprehensive visualization with four subplots:
1. Service Performance (4 services) - response times
2. Transparency Performance - data lineage, explainability, audit trail
3. Adaptability Performance - framework extensibility, flexibility, scalability
4. Traceability Performance - provenance, reproducibility, audit compliance

Based on actual evaluation data from comprehensive system evaluation.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Professional styling for research-quality diagrams
plt.style.use('default')
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.linewidth': 1,
    'axes.spines.left': True,
    'axes.spines.bottom': True,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'axes.grid': True,
    'grid.alpha': 0.3
})


def load_evaluation_data():
    """
    Load real performance evaluation data based on documented analysis.
    Using actual performance metrics from comprehensive system evaluation.
    """
    return {
        "performance_results": {
            "service_performance": {
                "data_retrieval_service": {"avg_response_time": 10.8},
                "knowledge_graph_service": {"avg_response_time": 13.76},
                "calculation_service": {"avg_response_time": 141.25},
                "report_service": {"avg_response_time": 35.39}
            },
            "tat_performance": {
                "transparency": {
                    "data_lineage_coverage": 19.1,
                    "calculation_explainability": 57.1,
                    "audit_trail_completeness": 75.0,
                    "overall_transparency_score": 50.4
                },
                "adaptability": {
                    "framework_extensibility": 100.0,
                    "data_source_flexibility": 50.0,
                    "scalability_performance": 87.8,
                    "overall_adaptability_score": 79.33
                },
                "traceability": {
                    "provenance_tracking_rate": 75.0,
                    "reproducibility_rate": 100.0,
                    "audit_compliance_rate": 100.0,
                    "overall_traceability_score": 91.67
                }
            }
        }
    }


def create_comprehensive_performance_diagram():
    """
    Generate comprehensive performance analysis diagram with real performance data.

    Four subplots:
    - Service Performance: 4 core services with actual response times
    - Transparency: split data lineage (Industry->Metric vs Metric->Datasource)
    - Adaptability: framework extensibility and scalability
    - Traceability: data provenance and audit compliance
    """
    print("Generating comprehensive performance diagram...")

    data = load_evaluation_data()

    service_perf = data["performance_results"]["service_performance"]
    transparency_perf = data["performance_results"]["tat_performance"]["transparency"]
    adaptability_perf = data["performance_results"]["tat_performance"]["adaptability"]
    traceability_perf = data["performance_results"]["tat_performance"]["traceability"]

    # Service performance data
    service_times = [
        service_perf["data_retrieval_service"]["avg_response_time"],
        service_perf["knowledge_graph_service"]["avg_response_time"],
        service_perf["calculation_service"]["avg_response_time"],
        service_perf["report_service"]["avg_response_time"]
    ]
    service_labels = ['Data\nRetrieval', 'Knowledge\nGraph', 'Calculation\nService', 'Report\nService']

    # Transparency components
    transparency_components = {
        'Calculation\nExplainability': transparency_perf["calculation_explainability"],
        'Audit Trail\nCompleteness': transparency_perf["audit_trail_completeness"]
    }
    industry_to_metric = 85.7  # Framework coverage
    metric_to_datasource = transparency_perf["data_lineage_coverage"]
    transparency_score = transparency_perf["overall_transparency_score"]

    # Adaptability components
    adaptability_components = {
        'Framework\nExtensibility': adaptability_perf["framework_extensibility"],
        'Data Source\nFlexibility': adaptability_perf["data_source_flexibility"],
        'Scalability\nPerformance': adaptability_perf["scalability_performance"]
    }
    adaptability_score = adaptability_perf["overall_adaptability_score"]

    # Traceability components
    traceability_components = {
        'Data\nProvenance': traceability_perf["provenance_tracking_rate"],
        'Calculation\nReproducibility': traceability_perf["reproducibility_rate"],
        'Audit\nCompliance': traceability_perf["audit_compliance_rate"]
    }
    traceability_score = traceability_perf["overall_traceability_score"]

    # Color scheme - one color per subplot
    service_color = '#3498DB'
    transparency_color = '#E74C3C'
    adaptability_color = '#2ECC71'
    traceability_color = '#9B59B6'

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))

    # --- 1. Service Performance (Top Left) ---
    bars1 = ax1.bar(service_labels, service_times, color=service_color, alpha=0.8,
                    edgecolor='black', linewidth=1)
    ax1.set_ylabel('Response Time (ms)', fontweight='bold')
    ax1.set_title('Service Performance', fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0, ha='center', fontsize=9)

    for bar, time_val in zip(bars1, service_times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(service_times)*0.02,
                f'{time_val:.1f}ms', ha='center', va='bottom', fontweight='bold', fontsize=9)

    # --- 2. Transparency Performance (Top Right) ---
    trans_values = list(transparency_components.values())
    trans_labels = list(transparency_components.keys())

    positions = [0, 1, 2]
    bar_width = 0.8
    half_width = bar_width / 2

    # Data Lineage Coverage as two half-width bars at position 0
    ax2.bar(0 - half_width/2, industry_to_metric,
            width=half_width, color=transparency_color, alpha=0.8,
            edgecolor='black', linewidth=1)
    ax2.bar(0 + half_width/2, metric_to_datasource,
            width=half_width, color=transparency_color, alpha=0.6,
            edgecolor='black', linewidth=1)

    # Other transparency bars at positions 1 and 2
    bars2_regular = ax2.bar([1, 2], trans_values,
                           width=bar_width, color=transparency_color, alpha=0.8,
                           edgecolor='black', linewidth=1)

    ax2.set_ylim(0, 110)
    ax2.set_ylabel('Score (%)', fontweight='bold')
    ax2.set_title('TAT Performance: Transparency', fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)

    all_labels = ['Data Lineage\nCoverage'] + trans_labels
    ax2.set_xticks(positions)
    ax2.set_xticklabels(all_labels, fontsize=8, ha='center')

    ax2.text(0 - half_width/2, industry_to_metric + 2,
            f'{industry_to_metric:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=7)
    ax2.text(0 + half_width/2, metric_to_datasource + 2,
            f'{metric_to_datasource:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=7)

    ax2.text(0 - half_width/2, industry_to_metric/2, 'Industry→\nMetric',
            ha='center', va='center', fontweight='bold', fontsize=6, color='white')
    ax2.text(0 + half_width/2, metric_to_datasource/2, 'Metric→\nDatasource',
            ha='center', va='center', fontweight='bold', fontsize=6, color='white')

    for bar, val in zip(bars2_regular, trans_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=8)

    # --- 3. Adaptability Performance (Bottom Left) ---
    adapt_values = list(adaptability_components.values())
    adapt_labels = list(adaptability_components.keys())
    bars3 = ax3.bar(adapt_labels, adapt_values, color=adaptability_color, alpha=0.8,
                    edgecolor='black', linewidth=1)
    ax3.set_ylim(0, 110)
    ax3.set_ylabel('Score (%)', fontweight='bold')
    ax3.set_title('TAT Performance: Adaptability', fontweight='bold', pad=15)
    ax3.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=0, ha='center', fontsize=9)

    for bar, val in zip(bars3, adapt_values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)

    # --- 4. Traceability Performance (Bottom Right) ---
    trace_values = list(traceability_components.values())
    trace_labels = list(traceability_components.keys())
    bars4 = ax4.bar(trace_labels, trace_values, color=traceability_color, alpha=0.8,
                    edgecolor='black', linewidth=1)
    ax4.set_ylim(0, 110)
    ax4.set_ylabel('Score (%)', fontweight='bold')
    ax4.set_title('TAT Performance: Traceability', fontweight='bold', pad=15)
    ax4.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=0, ha='center', fontsize=9)

    for bar, val in zip(bars4, trace_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)

    # Main title and layout
    fig.suptitle('Service Performance and TAT Performance',
                 fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout(rect=[0, 0.02, 1, 0.93], pad=2.0, w_pad=2.5, h_pad=3.0)

    # Save
    output_dir = Path(__file__).parent
    output_path = output_dir / "comprehensive_performance_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    print(f"Saved: {output_path}")
    print(f"Service Performance: Data={service_times[0]:.1f}ms, KG={service_times[1]:.1f}ms, Calc={service_times[2]:.1f}ms, Report={service_times[3]:.1f}ms")
    print(f"TAT Performance: Transparency={transparency_score:.1f}%, Adaptability={adaptability_score:.1f}%, Traceability={traceability_score:.1f}%")


if __name__ == "__main__":
    create_comprehensive_performance_diagram()
