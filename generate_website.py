#!/usr/bin/env python3
"""
SIRS Website Generator
Generates a static HTML website from the schedules JSON data
"""

import json
import os
from datetime import datetime

def load_schedules(schedules_file="schedules.json"):
    """Load schedules data from JSON file"""
    try:
        with open(schedules_file, 'r') as f:
            data = json.load(f)
        return data.get('schedules', [])
    except FileNotFoundError:
        print(f"❌ Schedules file {schedules_file} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {schedules_file}: {e}")
        return []

def generate_html(schedules):
    """Generate HTML content from schedules data"""

    # Group schedules by rink name
    rinks = {}
    for schedule in schedules:
        rink_name = schedule.get('ice_rink_name', 'Unknown')
        if rink_name not in rinks:
            rinks[rink_name] = []
        rinks[rink_name].append(schedule)

    # Sort rinks alphabetically
    rinks = dict(sorted(rinks.items()))

    # Sort schedules within each rink by year and month
    month_order = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    for rink_name in rinks:
        rinks[rink_name].sort(key=lambda x: (
            x.get('year', 0),
            month_order.get(x.get('month', '').lower(), 0)
        ))

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>St. Louis Ice Rink Schedules</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            line-height: 1.4;
            margin: 0;
            padding: 8px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            color: #0f172a;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .rink-section {{
            margin-bottom: 12px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(186, 230, 253, 0.5);
            backdrop-filter: blur(10px);
        }}

        .rink-header {{
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%);
            color: white;
            padding: 12px 16px;
            margin: 0;
            font-size: 1.05em;
            font-weight: 600;
            letter-spacing: 0.025em;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }}

        .schedule-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
            padding: 16px;
        }}

        .schedule-card {{
            background: rgba(248, 250, 252, 0.8);
            border: 1px solid rgba(186, 230, 253, 0.6);
            border-radius: 6px;
            padding: 12px;
            transition: all 0.15s ease;
            backdrop-filter: blur(5px);
            position: relative;
            overflow: visible;
        }}

        .schedule-card:hover {{
            background: rgba(255, 255, 255, 0.95);
            border-color: rgba(14, 165, 233, 0.5);
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(14, 165, 233, 0.15), 0 2px 8px rgba(59, 130, 246, 0.1);
        }}

        .schedule-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .schedule-title {{
            font-size: 1.05em;
            font-weight: 600;
            color: #1a202c;
            margin: 0;
        }}

        .confidence {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.7em;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: all 0.15s ease;
            min-height: 32px;
            min-width: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .confidence.high {{
            background: rgba(220, 252, 231, 0.9);
            color: #14532d;
            border: 1px solid rgba(187, 247, 208, 0.8);
        }}

        .confidence.medium {{
            background: rgba(254, 243, 199, 0.9);
            color: #92400e;
            border: 1px solid rgba(253, 230, 138, 0.8);
        }}

        .confidence.low {{
            background: rgba(254, 226, 226, 0.9);
            color: #991b1b;
            border: 1px solid rgba(254, 202, 202, 0.8);
        }}

        .confidence:hover {{
            transform: scale(1.05);
        }}

        .links-container {{
            display: flex;
            gap: 6px;
        }}

        .schedule-link {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            color: white;
            padding: 12px 16px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.85em;
            transition: all 0.15s ease;
            text-align: center;
            min-height: 44px;
        }}

        .schedule-link.primary {{
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            box-shadow: 0 2px 4px rgba(14, 165, 233, 0.2);
        }}

        .schedule-link.primary:hover {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(14, 165, 233, 0.3);
        }}

        .schedule-link.secondary {{
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
            box-shadow: 0 2px 4px rgba(100, 116, 139, 0.2);
        }}

        .schedule-link.secondary:hover {{
            background: linear-gradient(135deg, #475569 0%, #334155 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(71, 85, 105, 0.3);
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
        }}

        .modal-content {{
            background: rgba(255, 255, 255, 0.95);
            margin: 10vh auto;
            padding: 20px;
            border-radius: 8px;
            width: 92%;
            max-width: 480px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 25px -5px rgba(14, 165, 233, 0.1), 0 10px 10px -5px rgba(59, 130, 246, 0.05);
            border: 1px solid rgba(186, 230, 253, 0.3);
            backdrop-filter: blur(10px);
            position: relative;
        }}

        .close {{
            color: #9ca3af;
            position: absolute;
            top: 12px;
            right: 16px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
            z-index: 1001;
        }}

        .close:hover {{
            color: #374151;
        }}

        .modal h3 {{
            margin: 0 0 12px 0;
            color: #1f2937;
            font-size: 1.1em;
            font-weight: 600;
            padding-right: 30px;
        }}

        .modal p {{
            margin: 6px 0;
            line-height: 1.4;
            color: #4b5563;
            font-size: 0.9em;
        }}

        .modal p:last-child {{
            margin-bottom: 0;
        }}

        .no-schedules {{
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
            background: white;
            border-radius: 8px;
            margin: 12px 0;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 6px;
            }}

            .schedule-grid {{
                grid-template-columns: 1fr;
                gap: 10px;
                padding: 12px;
            }}

            .rink-header {{
                padding: 10px 12px;
                font-size: 1em;
            }}

            .schedule-card {{
                padding: 10px;
            }}

            .schedule-header {{
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
            }}

            .schedule-title {{
                font-size: 1em;
                flex: 1;
                min-width: 0;
            }}

            .confidence {{
                font-size: 0.68em;
                padding: 5px 10px;
                min-height: 30px;
                min-width: 45px;
                flex-shrink: 0;
            }}

            .links-container {{
                flex-direction: column;
                gap: 6px;
            }}

            .modal-content {{
                margin: 5vh auto;
                padding: 16px;
                width: 96%;
                max-height: 85vh;
            }}

            .modal h3 {{
                font-size: 1em;
                margin-bottom: 10px;
            }}

            .modal p {{
                font-size: 0.85em;
            }}
        }}

        @media (max-width: 480px) {{
            .schedule-header {{
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
            }}

            .schedule-title {{
                font-size: 0.95em;
                flex: 1;
                min-width: 0;
            }}

            .confidence {{
                font-size: 0.65em;
                padding: 4px 8px;
                min-height: 28px;
                min-width: 42px;
                flex-shrink: 0;
            }}

            .schedule-card {{
                padding: 8px;
            }}

            .modal-content {{
                margin: 2vh auto;
                padding: 12px;
                width: 98%;
                max-height: 90vh;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">"""

    if not schedules:
        html += """
        <div class="no-schedules">
            <h2>No schedules found</h2>
            <p>Run the admin CLI to collect ice rink schedules.</p>
        </div>"""
    else:
        for rink_name, rink_schedules in rinks.items():
            html += f"""
    <div class="rink-section">
        <h2 class="rink-header">{rink_name}</h2>
        <div class="schedule-grid">"""

            # Store modals to render outside the grid
            modals_html = ""

            for i, schedule in enumerate(rink_schedules):
                month = schedule.get('month', 'Unknown')
                year = schedule.get('year', 'Unknown')
                schedule_url = schedule.get('schedule_link', '#')
                parent_url = schedule.get('parent_page_link', '#')
                confidence = schedule.get('confidence', 'unknown')
                reasoning = schedule.get('reasoning', 'No reasoning provided')
                modal_id = f"modal-{rink_name.replace(' ', '')}-{i}"

                html += f"""
            <div class="schedule-card">
                <div class="schedule-header">
                    <div class="schedule-title">{month} {year}</div>
                    <div class="confidence {confidence}" onclick="openModal('{modal_id}')">
                        {confidence.title()}
                    </div>
                </div>
                <div class="links-container">
                    <a href="{schedule_url}" target="_blank" class="schedule-link primary">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
                        </svg>
                        Schedule
                    </a>
                    <a href="{parent_url}" target="_blank" class="schedule-link secondary">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8.707 1.5a1 1 0 0 0-1.414 0L.646 8.146a.5.5 0 0 0 .708.708L2 8.207V13.5A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5V8.207l.646.647a.5.5 0 0 0 .708-.708L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.707 1.5ZM13 7.207V13.5a.5.5 0 0 1-.5.5h-9a.5.5 0 0 1-.5-.5V7.207l5-5 5 5Z"/>
                        </svg>
                        Main Site
                    </a>
                </div>
            </div>"""

                # Add modal to modals collection
                modals_html += f"""
        <!-- Modal for {month} {year} reasoning -->
        <div id="{modal_id}" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('{modal_id}')">&times;</span>
                <h3>{rink_name} - {month} {year}</h3>
                <p><strong>Confidence:</strong> {confidence.title()}</p>
                <p><strong>Reasoning:</strong> {reasoning}</p>
            </div>
        </div>"""

            html += """
        </div>
    </div>"""

            # Add all modals for this rink outside the section
            html += modals_html

    html += f"""
    </div>

    <script>
        function openModal(modalId) {{
            document.getElementById(modalId).style.display = "block";
        }}

        function closeModal(modalId) {{
            document.getElementById(modalId).style.display = "none";
        }}

        // Close modal when clicking outside of it
        window.onclick = function(event) {{
            if (event.target.classList.contains('modal')) {{
                event.target.style.display = "none";
            }}
        }}

        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                const modals = document.querySelectorAll('.modal');
                modals.forEach(modal => {{
                    if (modal.style.display === 'block') {{
                        modal.style.display = 'none';
                    }}
                }});
            }}
        }});
    </script>
</body>
</html>"""

    return html

def main():
    """Main entry point"""
    print("🚀 SIRS Website Generator")
    print("=" * 40)

    # Load schedules data
    print("📋 Loading schedules data...")
    schedules = load_schedules()

    if not schedules:
        print("⚠️  No schedules found, generating empty website")
    else:
        print(f"✅ Loaded {len(schedules)} schedules")

    # Generate HTML
    print("🎨 Generating HTML...")
    html_content = generate_html(schedules)

    # Create docs directory for GitHub Pages
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"📁 Created {docs_dir} directory")

    # Write HTML file
    output_file = os.path.join(docs_dir, "index.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Website generated: {output_file}")
    print("🌐 Ready for GitHub Pages deployment!")

if __name__ == '__main__':
    main()