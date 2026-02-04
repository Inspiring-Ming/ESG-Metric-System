#!/usr/bin/env python3
"""
Generate figures for Chapter 4 and Chapter 5 of PhD thesis.
- Figure 4.2: Metric Derivation Paths
- Figure 5.1: Use Case Diagram (UML)
- Figure 5.3: Calculation Service Workflow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionPatch, Ellipse, Rectangle
import numpy as np

# Set up consistent styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11


def draw_figure_4_2_metric_derivation_paths():
    """
    Figure 4.2: Metric derivation paths showing:
    - Left: Hierarchical calculated metric path with recursive resolution
    - Right: Direct metric path (simple case)

    Improvements:
    - Step labels moved further left
    - Larger fonts
    - Better box spacing and narrower data source boxes
    - More beautiful colors
    """
    fig, axes = plt.subplots(1, 2, figsize=(18, 13))

    # Professional color palette
    colors = {
        'target_metric': '#E74C3C',      # Red - bold
        'calculated_metric': '#3498DB',   # Blue
        'model': '#9B59B6',               # Purple
        'input_esg': '#27AE60',           # Green
        'input_fin': '#F39C12',           # Orange
        'variable': '#5DADE2',            # Light blue
        'datasource': '#E67E22',          # Dark orange
        'text_dark': '#2C3E50',           # Dark text
        'text_light': '#7F8C8D',          # Light text
    }

    # =========== LEFT SIDE: Hierarchical Calculated Metric Path ===========
    ax1 = axes[0]
    ax1.set_xlim(-1, 13)
    ax1.set_ylim(0, 15)
    ax1.axis('off')
    ax1.set_title('Calculated Metric Path with Recursive Resolution\n(hasCalculationMethod = "calculation_model")',
                  fontsize=13, fontweight='bold', pad=15, color=colors['text_dark'])

    # Resolution step labels - moved to far left
    step_x = -0.8
    ax1.text(step_x, 13, 'Step 1\n(Target)', fontsize=10, fontweight='bold', color=colors['text_light'], ha='left')
    ax1.text(step_x, 10.5, 'Step 2\n(Resolve)', fontsize=10, fontweight='bold', color=colors['text_light'], ha='left')
    ax1.text(step_x, 7, 'Step 3\n(Resolve)', fontsize=10, fontweight='bold', color=colors['text_light'], ha='left')
    ax1.text(step_x, 4, 'Step 4\n(Map)', fontsize=10, fontweight='bold', color=colors['text_light'], ha='left')
    ax1.text(step_x, 1.5, 'Step 5\n(Source)', fontsize=10, fontweight='bold', color=colors['text_light'], ha='left')

    # Step 1: EnvironmentalRiskMetric (Target)
    box_top = FancyBboxPatch((3.5, 12.5), 6, 1.2, boxstyle="round,pad=0.08,rounding_size=0.3",
                              facecolor=colors['target_metric'], edgecolor='#C0392B', linewidth=2.5)
    ax1.add_patch(box_top)
    ax1.text(6.5, 13.1, 'EnvironmentalRiskMetric', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    # Model for Step 1
    box_model1 = FancyBboxPatch((3.8, 11.2), 5.4, 0.7, boxstyle="round,pad=0.05,rounding_size=0.2",
                                 facecolor=colors['model'], edgecolor='#7D3C98', linewidth=1.5)
    ax1.add_patch(box_model1)
    ax1.text(6.5, 11.55, 'EnvironmentalRiskModel', ha='center', va='center', fontsize=10, color='white')

    ax1.annotate('', xy=(6.5, 11.9), xytext=(6.5, 12.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=1.8))
    ax1.text(7.2, 12.2, 'IsCalculatedBy', ha='left', fontsize=9, style='italic', color=colors['text_dark'])

    # Step 2: Two component metrics
    # GHGEmissionIntensity
    box_ghg = FancyBboxPatch((1, 9.5), 4.5, 1.2, boxstyle="round,pad=0.08,rounding_size=0.3",
                              facecolor=colors['calculated_metric'], edgecolor='#2980B9', linewidth=2)
    ax1.add_patch(box_ghg)
    ax1.text(3.25, 10.1, 'GHGEmissionIntensity', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # AirQualityPollutant
    box_air = FancyBboxPatch((7.5, 9.5), 4.5, 1.2, boxstyle="round,pad=0.08,rounding_size=0.3",
                              facecolor=colors['calculated_metric'], edgecolor='#2980B9', linewidth=2)
    ax1.add_patch(box_air)
    ax1.text(9.75, 10.1, 'AirQualityPollutant', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Arrows from model to Step 2
    ax1.annotate('', xy=(3.25, 10.7), xytext=(5.2, 11.2),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=1.5))
    ax1.annotate('', xy=(9.75, 10.7), xytext=(7.8, 11.2),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=1.5))
    ax1.text(6.5, 11, 'RequiresInputFrom', ha='center', fontsize=9, style='italic', color=colors['text_dark'])

    # Models for Step 2
    box_model2a = FancyBboxPatch((1.3, 8.3), 3.9, 0.7, boxstyle="round,pad=0.05,rounding_size=0.2",
                                  facecolor=colors['model'], edgecolor='#7D3C98', linewidth=1.2)
    ax1.add_patch(box_model2a)
    ax1.text(3.25, 8.65, 'GHGIntensityModel', ha='center', va='center', fontsize=10, color='white')

    box_model2b = FancyBboxPatch((7.8, 8.3), 3.9, 0.7, boxstyle="round,pad=0.05,rounding_size=0.2",
                                  facecolor=colors['model'], edgecolor='#7D3C98', linewidth=1.2)
    ax1.add_patch(box_model2b)
    ax1.text(9.75, 8.65, 'AirQualityModel', ha='center', va='center', fontsize=10, color='white')

    ax1.annotate('', xy=(3.25, 9), xytext=(3.25, 9.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=1.2))
    ax1.annotate('', xy=(9.75, 9), xytext=(9.75, 9.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=1.2))

    # Step 3: Inputs for component metrics
    # GHG inputs: Scope1, Scope2, Revenue
    inputs_left = [
        ('Scope1', 1.3, colors['input_esg']),
        ('Scope2', 3.3, colors['input_esg']),
        ('Revenue', 5.3, colors['input_fin']),
    ]
    for name, x, color in inputs_left:
        box = FancyBboxPatch((x-0.9, 6.3), 1.8, 1.1, boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=color, edgecolor='#1E8449' if 'ESG' in name or name in ['Scope1', 'Scope2'] else '#D68910', linewidth=1.2)
        ax1.add_patch(box)
        domain = '(ESG)' if name != 'Revenue' else '(Fin)'
        ax1.text(x, 6.85, f'{name}\n{domain}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax1.annotate('', xy=(x, 7.4), xytext=(3.25, 8.3),
                    arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.9))

    # Air quality inputs: SOX, NOX, VOC
    inputs_right = [
        ('SOX', 7.7, colors['input_esg']),
        ('NOX', 9.7, colors['input_esg']),
        ('VOC', 11.7, colors['input_esg']),
    ]
    for name, x, color in inputs_right:
        box = FancyBboxPatch((x-0.9, 6.3), 1.8, 1.1, boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=color, edgecolor='#1E8449', linewidth=1.2)
        ax1.add_patch(box)
        ax1.text(x, 6.85, f'{name}\n(ESG)', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax1.annotate('', xy=(x, 7.4), xytext=(9.75, 8.3),
                    arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.9))

    ax1.text(3.25, 7.9, 'RequiresInputFrom', ha='center', fontsize=8, style='italic', color=colors['text_dark'])
    ax1.text(9.75, 7.9, 'RequiresInputFrom', ha='center', fontsize=8, style='italic', color=colors['text_dark'])

    # Step 4: Dataset Variables
    variables = [
        ('CO2SCOPE1', 1.3),
        ('CO2SCOPE2', 3.3),
        ('revt', 5.3),
        ('SOXEMISSIONS', 7.7),
        ('NOXEMISSIONS', 9.7),
        ('VOCEMISSIONS', 11.7),
    ]
    for name, x in variables:
        box = FancyBboxPatch((x-0.95, 3.5), 1.9, 0.9, boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=colors['variable'], edgecolor='#2E86AB', linewidth=1)
        ax1.add_patch(box)
        ax1.text(x, 3.95, name, ha='center', va='center', fontsize=8, fontweight='bold', color=colors['text_dark'])
        ax1.annotate('', xy=(x, 4.4), xytext=(x, 6.3),
                    arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.9))

    ax1.text(6.5, 5.3, 'ObtainedFrom', ha='center', fontsize=9, style='italic', color=colors['text_dark'])

    # Step 5: Data Sources - narrower boxes with better spacing
    box_euro1 = FancyBboxPatch((1.3, 1), 2.5, 0.9, boxstyle="round,pad=0.05,rounding_size=0.2",
                               facecolor=colors['datasource'], edgecolor='#BA4A00', linewidth=1.2)
    ax1.add_patch(box_euro1)
    ax1.text(2.55, 1.45, 'Eurofidai', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    box_wrds = FancyBboxPatch((4.4, 1), 2, 0.9, boxstyle="round,pad=0.05,rounding_size=0.2",
                              facecolor=colors['datasource'], edgecolor='#BA4A00', linewidth=1.2)
    ax1.add_patch(box_wrds)
    ax1.text(5.4, 1.45, 'WRDS', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    box_euro2 = FancyBboxPatch((8.5, 1), 2.5, 0.9, boxstyle="round,pad=0.05,rounding_size=0.2",
                               facecolor=colors['datasource'], edgecolor='#BA4A00', linewidth=1.2)
    ax1.add_patch(box_euro2)
    ax1.text(9.75, 1.45, 'Eurofidai', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    # Arrows to sources
    ax1.annotate('', xy=(2.55, 1.9), xytext=(1.3, 3.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.7))
    ax1.annotate('', xy=(2.55, 1.9), xytext=(3.3, 3.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.7))
    ax1.annotate('', xy=(5.4, 1.9), xytext=(5.3, 3.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.7))
    for x in [7.7, 9.7, 11.7]:
        ax1.annotate('', xy=(9.75, 1.9), xytext=(x, 3.5),
                    arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=0.7))

    ax1.text(6.5, 2.6, 'SourcesFrom', ha='center', fontsize=9, style='italic', color=colors['text_dark'])

    # =========== RIGHT SIDE: Direct Metric Path ===========
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 15)
    ax2.axis('off')
    ax2.set_title('Direct Metric Path\n(hasCalculationMethod = "direct_measurement")',
                  fontsize=13, fontweight='bold', pad=15, color=colors['text_dark'])

    ax2.text(5, 13.5, 'Simple Path: No Recursive Resolution Required',
             ha='center', fontsize=11, style='italic', color=colors['text_light'])

    # Metric
    box_direct = FancyBboxPatch((1.5, 11), 7, 1.5, boxstyle="round,pad=0.1,rounding_size=0.3",
                                facecolor=colors['calculated_metric'], edgecolor='#2980B9', linewidth=2.5)
    ax2.add_patch(box_direct)
    ax2.text(5, 11.75, 'TotalWaterConsumed', ha='center', va='center', fontsize=13, fontweight='bold', color='white')

    # No Model - styled text - MOVED UP to avoid overlap
    ax2.text(5, 9.5, '✗ No Model Required', ha='center', va='center', fontsize=12,
             style='italic', color=colors['text_light'])

    # Arrow from metric to variable - starts lower
    ax2.annotate('', xy=(5, 7.5), xytext=(5, 11),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2.5))
    # ObtainedFrom label - positioned clearly below "No Model Required"
    ax2.text(5.5, 8.5, 'ObtainedFrom', ha='left', fontsize=11, style='italic', fontweight='bold', color=colors['text_dark'])

    # Dataset Variable - moved up
    box_var = FancyBboxPatch((1, 5.5), 8, 1.8, boxstyle="round,pad=0.1,rounding_size=0.3",
                             facecolor=colors['variable'], edgecolor='#2E86AB', linewidth=2.5)
    ax2.add_patch(box_var)
    ax2.text(5, 6.4, 'WATERCONSUMPTIONTOTAL', ha='center', va='center', fontsize=12, fontweight='bold', color=colors['text_dark'])

    # Data Source
    box_ds = FancyBboxPatch((2, 2), 6, 1.5, boxstyle="round,pad=0.1,rounding_size=0.3",
                            facecolor=colors['datasource'], edgecolor='#BA4A00', linewidth=2.5)
    ax2.add_patch(box_ds)
    ax2.text(5, 2.75, 'Eurofidai', ha='center', va='center', fontsize=13, fontweight='bold', color='white')

    # Arrow from variable to source
    ax2.annotate('', xy=(5, 3.5), xytext=(5, 5.5),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2.5))
    ax2.text(5.5, 4.5, 'SourcesFrom', ha='left', fontsize=11, style='italic', color=colors['text_dark'])

    # Legend with better colors
    legend_elements = [
        mpatches.Patch(facecolor=colors['target_metric'], edgecolor='#C0392B', label='Target Metric (Aggregate)'),
        mpatches.Patch(facecolor=colors['calculated_metric'], edgecolor='#2980B9', label='Calculated/Direct Metric'),
        mpatches.Patch(facecolor=colors['model'], edgecolor='#7D3C98', label='Calculation Model'),
        mpatches.Patch(facecolor=colors['input_esg'], edgecolor='#1E8449', label='Metric Input (ESG)'),
        mpatches.Patch(facecolor=colors['input_fin'], edgecolor='#D68910', label='Metric Input (Financial)'),
        mpatches.Patch(facecolor=colors['variable'], edgecolor='#2E86AB', label='Dataset Variable'),
        mpatches.Patch(facecolor=colors['datasource'], edgecolor='#BA4A00', label='Data Source'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=10, bbox_to_anchor=(0.5, 0.01),
               frameon=True, fancybox=True, shadow=True)

    plt.tight_layout(rect=[0, 0.07, 1, 1])
    plt.savefig('/Users/mingqin/Downloads/esg-knowledge-graph-demo/Demo corresponding acadedmic paper/figures/figure_4_2_metric_derivation_paths.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 4.2 saved: figure_4_2_metric_derivation_paths.png")


def draw_figure_5_3_calculation_service_workflow():
    """
    Figure 5.3: Calculation Service workflow showing dual derivation paths

    Improvements:
    - Smaller boxes with larger fonts
    - Color box legend (no text-only legend)
    - Fixed grey dashed line with clear start/end points
    - Arrow endpoints outside boxes
    - Narrower result box to show End circle completely
    - Connected arrows from decision diamond using angled paths
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(-1, 13)
    ax.axis('off')

    # Professional color palette
    colors = {
        'start_end': '#27AE60',
        'query': '#3498DB',
        'decision': '#F1C40F',
        'direct_path': '#2ECC71',
        'calc_path': '#E74C3C',
        'execute': '#9B59B6',
        'result': '#E67E22',
        'text_dark': '#2C3E50',
        'text_light': '#7F8C8D',
        'recursive': '#95A5A6',
    }

    # Title
    ax.text(7, 12.5, 'Figure 5.3: Calculation Service Workflow',
            ha='center', va='center', fontsize=15, fontweight='bold', color=colors['text_dark'])

    # Start
    start = plt.Circle((7, 11.5), 0.4, color=colors['start_end'], ec='#1E8449', lw=2)
    ax.add_patch(start)
    ax.text(7, 11.5, 'Start', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Step 1: Query CQ4 - smaller box, larger font
    box1 = FancyBboxPatch((3.8, 10), 6.4, 0.85, boxstyle="round,pad=0.06,rounding_size=0.15",
                          facecolor=colors['query'], edgecolor='#2980B9', linewidth=2)
    ax.add_patch(box1)
    ax.text(7, 10.42, 'Step 1 (CQ4): Query hasCalculationMethod', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    # Arrow from Start to Step 1
    ax.annotate('', xy=(7, 10.85), xytext=(7, 11.1),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2))

    # Decision diamond - smaller
    diamond_x = [7, 8.8, 7, 5.2, 7]
    diamond_y = [9.6, 8.5, 7.4, 8.5, 9.6]
    ax.fill(diamond_x, diamond_y, facecolor=colors['decision'], edgecolor='#D4AC0D', linewidth=2)
    ax.text(7, 8.5, 'Calculation\nMethod?', ha='center', va='center', fontsize=11, fontweight='bold', color=colors['text_dark'])
    # Arrow from Step 1 to Decision
    ax.annotate('', xy=(7, 9.6), xytext=(7, 10),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2))

    # Left branch: direct_measurement - draw connected line from diamond edge
    ax.text(3.5, 8.9, 'direct_measurement', ha='center', fontsize=10, style='italic', color=colors['direct_path'], fontweight='bold')
    # Draw line from diamond left point, then down to box
    ax.plot([5.2, 2.6, 2.6], [8.5, 8.5, 7.7], color=colors['direct_path'], lw=2)
    ax.annotate('', xy=(2.6, 7.7), xytext=(2.6, 7.9),
                arrowprops=dict(arrowstyle='->', color=colors['direct_path'], lw=2))

    # Step 2a: Query CQ7 - smaller box
    box2a = FancyBboxPatch((0.8, 6.8), 3.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                           facecolor=colors['direct_path'], edgecolor='#27AE60', linewidth=2)
    ax.add_patch(box2a)
    ax.text(2.6, 7.25, 'Step 2a (CQ7): Get Data Source', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Retrieve value - smaller box
    box2a_ret = FancyBboxPatch((0.8, 5.3), 3.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                               facecolor=colors['direct_path'], edgecolor='#27AE60', linewidth=2)
    ax.add_patch(box2a_ret)
    ax.text(2.6, 5.75, 'Retrieve Value', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.annotate('', xy=(2.6, 6.2), xytext=(2.6, 6.8),
                arrowprops=dict(arrowstyle='->', color=colors['direct_path'], lw=1.5))

    # Right branch: calculation_model - draw connected line from diamond edge
    ax.text(10.5, 8.9, 'calculation_model', ha='center', fontsize=10, style='italic', color=colors['calc_path'], fontweight='bold')
    # Draw line from diamond right point, then down to box
    ax.plot([8.8, 11.4, 11.4], [8.5, 8.5, 7.7], color=colors['calc_path'], lw=2)
    ax.annotate('', xy=(11.4, 7.7), xytext=(11.4, 7.9),
                arrowprops=dict(arrowstyle='->', color=colors['calc_path'], lw=2))

    # Step 3: Query CQ5 - smaller box
    box3 = FancyBboxPatch((9.6, 6.8), 3.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                          facecolor=colors['calc_path'], edgecolor='#C0392B', linewidth=2)
    ax.add_patch(box3)
    ax.text(11.4, 7.25, 'Step 3 (CQ5): Get Model Inputs', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Step 4: Recursive resolution - smaller box
    box4 = FancyBboxPatch((9.6, 5.3), 3.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                          facecolor=colors['calc_path'], edgecolor='#C0392B', linewidth=2)
    ax.add_patch(box4)
    ax.text(11.4, 5.75, 'Step 4: Resolve Inputs', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.annotate('', xy=(11.4, 6.2), xytext=(11.4, 6.8),
                arrowprops=dict(arrowstyle='->', color=colors['calc_path'], lw=1.5))

    # Recursive arrow - bracket-style loop on the right side
    ax.plot([13.2, 13.6, 13.6, 13.2], [5.75, 5.75, 7.25, 7.25],
            color=colors['recursive'], lw=2, linestyle='--')
    # Arrow head at the top
    ax.annotate('', xy=(13.2, 7.25), xytext=(13.4, 7.25),
                arrowprops=dict(arrowstyle='->', color=colors['recursive'], lw=2))
    ax.text(13.8, 6.5, 'Recursive', ha='left', fontsize=9, color=colors['recursive'], style='italic')

    # Step 5: Query CQ6 - smaller box
    box5 = FancyBboxPatch((9.6, 3.8), 3.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                          facecolor=colors['execute'], edgecolor='#7D3C98', linewidth=2)
    ax.add_patch(box5)
    ax.text(11.4, 4.25, 'Step 5 (CQ6): Get Implementation', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.annotate('', xy=(11.4, 4.7), xytext=(11.4, 5.3),
                arrowprops=dict(arrowstyle='->', color=colors['execute'], lw=1.5))

    # Step 6: Execute - smaller box
    box6 = FancyBboxPatch((9.6, 2.3), 3.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.15",
                          facecolor=colors['execute'], edgecolor='#7D3C98', linewidth=2)
    ax.add_patch(box6)
    ax.text(11.4, 2.75, 'Step 6: Execute Model', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.annotate('', xy=(11.4, 3.2), xytext=(11.4, 3.8),
                arrowprops=dict(arrowstyle='->', color=colors['execute'], lw=1.5))

    # Merge paths - arrows end at top of Return box
    ax.annotate('', xy=(5.8, 1.05), xytext=(2.6, 5.3),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2,
                               connectionstyle='arc3,rad=0.15'))
    ax.annotate('', xy=(8.2, 1.05), xytext=(11.4, 2.3),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2,
                               connectionstyle='arc3,rad=-0.15'))

    # Return result - NARROWER box
    box_return = FancyBboxPatch((5, 0.3), 4, 0.75, boxstyle="round,pad=0.06,rounding_size=0.15",
                                facecolor=colors['result'], edgecolor='#D35400', linewidth=2)
    ax.add_patch(box_return)
    ax.text(7, 0.67, 'Return Calculated Value', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    # End - moved down a bit to show completely
    end = plt.Circle((7, -0.5), 0.35, color='#E74C3C', ec='#C0392B', lw=2)
    ax.add_patch(end)
    ax.text(7, -0.5, 'End', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    ax.annotate('', xy=(7, -0.15), xytext=(7, 0.3),
                arrowprops=dict(arrowstyle='->', color=colors['text_dark'], lw=2))

    # Color Box Legend - positioned at bottom left
    legend_x = 0.3
    legend_y = 4.2
    box_w = 0.5
    box_h = 0.35
    spacing = 0.5

    ax.text(legend_x, legend_y + 0.3, 'Legend:', fontsize=10, fontweight='bold', color=colors['text_dark'])

    legend_items = [
        (colors['query'], 'Knowledge Graph Query'),
        (colors['direct_path'], 'Direct Measurement Path'),
        (colors['calc_path'], 'Calculation Model Path'),
        (colors['execute'], 'Model Execution'),
        (colors['result'], 'Result'),
    ]

    for i, (color, label) in enumerate(legend_items):
        y = legend_y - (i + 1) * spacing
        legend_box = FancyBboxPatch((legend_x, y - box_h/2), box_w, box_h,
                                     boxstyle="round,pad=0.02,rounding_size=0.05",
                                     facecolor=color, edgecolor='#555', linewidth=1)
        ax.add_patch(legend_box)
        ax.text(legend_x + box_w + 0.15, y, label, fontsize=9, va='center', color=colors['text_dark'])

    plt.tight_layout()
    plt.savefig('/Users/mingqin/Downloads/esg-knowledge-graph-demo/Demo corresponding acadedmic paper/figures/figure_5_3_calculation_workflow.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 5.3 saved: figure_5_3_calculation_workflow.png")


def draw_figure_5_1_use_case_diagram():
    """
    Figure 5.1: UML Use Case Diagram for ESG Reporting Framework

    Shows three core use cases:
    - UC1: ESG Report Generation (CQ1, CQ2, CQ3)
    - UC2: Metric Calculation (CQ4, CQ5, CQ6)
    - UC3: Data Access (CQ7)

    With actors and relationships including <<include>> dependencies
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Professional color palette
    colors = {
        'actor': '#2C3E50',
        'usecase_bg': '#EBF5FB',
        'usecase_border': '#3498DB',
        'system_border': '#95A5A6',
        'include_arrow': '#7F8C8D',
        'text_dark': '#2C3E50',
        'uc1': '#E8F6F3',  # Light teal for UC1
        'uc2': '#FEF9E7',  # Light yellow for UC2
        'uc3': '#FDEDEC',  # Light red for UC3
        'uc1_border': '#1ABC9C',
        'uc2_border': '#F39C12',
        'uc3_border': '#E74C3C',
    }

    # Title
    ax.text(8, 11.5, 'Figure 5.1: ESG Reporting Framework - Use Case Diagram',
            ha='center', va='center', fontsize=14, fontweight='bold', color=colors['text_dark'])

    # System boundary box
    system_box = FancyBboxPatch((4, 0.5), 10.5, 10, boxstyle="round,pad=0.02,rounding_size=0.2",
                                 facecolor='white', edgecolor=colors['system_border'], linewidth=2, linestyle='-')
    ax.add_patch(system_box)
    ax.text(9.25, 10.2, 'ESG Reporting Framework', ha='center', va='center',
            fontsize=12, fontweight='bold', color=colors['text_dark'])

    # ============ ACTORS (Left Side) ============
    # Actor 1: ESG Reporting Officer
    # Stick figure
    ax.plot([1.5, 1.5], [7.5, 8.3], color=colors['actor'], lw=2)  # body
    ax.plot([1.5, 1.5], [8.3, 8.6], color=colors['actor'], lw=2)  # neck
    head1 = plt.Circle((1.5, 8.85), 0.25, color=colors['actor'], ec=colors['actor'], lw=2)
    ax.add_patch(head1)
    ax.plot([1, 2], [8.0, 8.0], color=colors['actor'], lw=2)  # arms
    ax.plot([1.5, 1.1], [7.5, 6.9], color=colors['actor'], lw=2)  # left leg
    ax.plot([1.5, 1.9], [7.5, 6.9], color=colors['actor'], lw=2)  # right leg
    ax.text(1.5, 6.5, 'ESG Reporting\nOfficer', ha='center', va='top', fontsize=10, color=colors['text_dark'])

    # Actor 2: Data Analyst
    ax.plot([1.5, 1.5], [3.5, 4.3], color=colors['actor'], lw=2)  # body
    ax.plot([1.5, 1.5], [4.3, 4.6], color=colors['actor'], lw=2)  # neck
    head2 = plt.Circle((1.5, 4.85), 0.25, color=colors['actor'], ec=colors['actor'], lw=2)
    ax.add_patch(head2)
    ax.plot([1, 2], [4.0, 4.0], color=colors['actor'], lw=2)  # arms
    ax.plot([1.5, 1.1], [3.5, 2.9], color=colors['actor'], lw=2)  # left leg
    ax.plot([1.5, 1.9], [3.5, 2.9], color=colors['actor'], lw=2)  # right leg
    ax.text(1.5, 2.5, 'Data Analyst\n/ Auditor', ha='center', va='top', fontsize=10, color=colors['text_dark'])

    # ============ USE CASES (Center) ============
    # UC1: ESG Report Generation (top) - Ellipse
    uc1 = Ellipse((9, 8.5), 5.5, 1.8, facecolor=colors['uc1'], edgecolor=colors['uc1_border'], linewidth=2.5)
    ax.add_patch(uc1)
    ax.text(9, 8.7, 'UC1: ESG Report Generation', ha='center', va='center', fontsize=11, fontweight='bold', color=colors['text_dark'])
    ax.text(9, 8.2, '(CQ1, CQ2, CQ3)', ha='center', va='center', fontsize=10, style='italic', color=colors['uc1_border'])

    # UC2: Metric Calculation (middle)
    uc2 = Ellipse((9, 5.5), 5.5, 1.8, facecolor=colors['uc2'], edgecolor=colors['uc2_border'], linewidth=2.5)
    ax.add_patch(uc2)
    ax.text(9, 5.7, 'UC2: Metric Calculation', ha='center', va='center', fontsize=11, fontweight='bold', color=colors['text_dark'])
    ax.text(9, 5.2, '(CQ4, CQ5, CQ6)', ha='center', va='center', fontsize=10, style='italic', color=colors['uc2_border'])

    # UC3: Data Access (bottom)
    uc3 = Ellipse((9, 2.5), 5.5, 1.8, facecolor=colors['uc3'], edgecolor=colors['uc3_border'], linewidth=2.5)
    ax.add_patch(uc3)
    ax.text(9, 2.7, 'UC3: Data Access', ha='center', va='center', fontsize=11, fontweight='bold', color=colors['text_dark'])
    ax.text(9, 2.2, '(CQ7)', ha='center', va='center', fontsize=10, style='italic', color=colors['uc3_border'])

    # ============ RELATIONSHIPS ============
    # Actor to UC associations (solid lines)
    # ESG Officer -> UC1
    ax.annotate('', xy=(6.25, 8.5), xytext=(2, 7.8),
                arrowprops=dict(arrowstyle='-', color=colors['actor'], lw=1.5))

    # ESG Officer -> UC2
    ax.annotate('', xy=(6.25, 5.5), xytext=(2, 7.5),
                arrowprops=dict(arrowstyle='-', color=colors['actor'], lw=1.5))

    # Data Analyst -> UC2
    ax.annotate('', xy=(6.25, 5.5), xytext=(2, 4.2),
                arrowprops=dict(arrowstyle='-', color=colors['actor'], lw=1.5))

    # Data Analyst -> UC3
    ax.annotate('', xy=(6.25, 2.5), xytext=(2, 4.0),
                arrowprops=dict(arrowstyle='-', color=colors['actor'], lw=1.5))

    # <<include>> relationships (dashed arrows)
    # UC1 includes UC2
    ax.annotate('', xy=(9, 6.4), xytext=(9, 7.6),
                arrowprops=dict(arrowstyle='->', color=colors['include_arrow'], lw=1.5, linestyle='--'))
    ax.text(9.5, 7, '<<include>>', ha='left', va='center', fontsize=9, style='italic', color=colors['include_arrow'])

    # UC2 includes UC3
    ax.annotate('', xy=(9, 3.4), xytext=(9, 4.6),
                arrowprops=dict(arrowstyle='->', color=colors['include_arrow'], lw=1.5, linestyle='--'))
    ax.text(9.5, 4, '<<include>>', ha='left', va='center', fontsize=9, style='italic', color=colors['include_arrow'])

    # ============ CQ BOXES (Right side) ============
    # CQ groupings
    cq_box_width = 2.2
    cq_box_height = 0.5

    # CQ1-CQ3 for UC1
    for i, cq in enumerate(['CQ1: Framework Discovery', 'CQ2: Category Enumeration', 'CQ3: Metric Identification']):
        y_pos = 9.3 - i * 0.55
        box = FancyBboxPatch((12, y_pos - 0.2), cq_box_width, cq_box_height,
                             boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor='white', edgecolor=colors['uc1_border'], linewidth=1)
        ax.add_patch(box)
        ax.text(13.1, y_pos + 0.05, cq.split(':')[0], ha='center', va='center', fontsize=8, fontweight='bold', color=colors['uc1_border'])
    ax.annotate('', xy=(12, 8.5), xytext=(11.75, 8.5),
                arrowprops=dict(arrowstyle='-', color=colors['uc1_border'], lw=1, linestyle=':'))

    # CQ4-CQ6 for UC2
    for i, cq in enumerate(['CQ4: Calculation Method', 'CQ5: Model Inputs', 'CQ6: Implementation']):
        y_pos = 6.3 - i * 0.55
        box = FancyBboxPatch((12, y_pos - 0.2), cq_box_width, cq_box_height,
                             boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor='white', edgecolor=colors['uc2_border'], linewidth=1)
        ax.add_patch(box)
        ax.text(13.1, y_pos + 0.05, cq.split(':')[0], ha='center', va='center', fontsize=8, fontweight='bold', color=colors['uc2_border'])
    ax.annotate('', xy=(12, 5.5), xytext=(11.75, 5.5),
                arrowprops=dict(arrowstyle='-', color=colors['uc2_border'], lw=1, linestyle=':'))

    # CQ7 for UC3
    box = FancyBboxPatch((12, 2.3), cq_box_width, cq_box_height,
                         boxstyle="round,pad=0.02,rounding_size=0.1",
                         facecolor='white', edgecolor=colors['uc3_border'], linewidth=1)
    ax.add_patch(box)
    ax.text(13.1, 2.55, 'CQ7', ha='center', va='center', fontsize=8, fontweight='bold', color=colors['uc3_border'])
    ax.annotate('', xy=(12, 2.5), xytext=(11.75, 2.5),
                arrowprops=dict(arrowstyle='-', color=colors['uc3_border'], lw=1, linestyle=':'))

    # Legend
    legend_y = 0.8
    ax.text(5, legend_y, 'Legend:', fontsize=10, fontweight='bold', color=colors['text_dark'])

    # Solid line = association
    ax.plot([6.5, 7.5], [legend_y, legend_y], color=colors['actor'], lw=1.5)
    ax.text(7.7, legend_y, 'Actor Association', fontsize=9, va='center', color=colors['text_dark'])

    # Dashed arrow = include
    ax.annotate('', xy=(11, legend_y), xytext=(10, legend_y),
                arrowprops=dict(arrowstyle='->', color=colors['include_arrow'], lw=1.5, linestyle='--'))
    ax.text(11.2, legend_y, '<<include>>', fontsize=9, va='center', color=colors['text_dark'])

    plt.tight_layout()
    plt.savefig('/Users/mingqin/Downloads/esg-knowledge-graph-demo/Demo corresponding acadedmic paper/figures/figure_5_1_use_case_diagram.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Figure 5.1 saved: figure_5_1_use_case_diagram.png")


if __name__ == '__main__':
    import os
    # Create figures directory
    os.makedirs('/Users/mingqin/Downloads/esg-knowledge-graph-demo/Demo corresponding acadedmic paper/figures', exist_ok=True)

    print("Generating figures...")
    draw_figure_4_2_metric_derivation_paths()
    draw_figure_5_1_use_case_diagram()
    draw_figure_5_3_calculation_service_workflow()
    print("\nAll figures generated successfully!")
