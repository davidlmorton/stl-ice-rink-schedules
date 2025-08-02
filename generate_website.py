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
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.5;
            max-width: 1000px;
            margin: 0 auto;
            padding: 15px;
            background-color: #f8f9fa;
        }}

        .rink-section {{
            margin-bottom: 25px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .rink-header {{
            background: #343a40;
            color: white;
            padding: 15px;
            margin: 0;
            font-size: 1.2em;
            font-weight: 500;
        }}

        .schedule-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
            padding: 20px;
        }}

        .schedule-card {{
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            transition: all 0.2s ease;
            background: #fafafa;
            position: relative;
        }}

        .schedule-card:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 12px rgba(0,0,0,0.15);
            border-color: #667eea;
        }}

        .schedule-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .schedule-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: #343a40;
            margin: 0;
        }}

        .confidence {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 500;
            cursor: help;
            position: relative;
        }}

        .confidence.high {{
            background: #d4edda;
            color: #155724;
        }}

        .confidence.medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .confidence.low {{
            background: #f8d7da;
            color: #721c24;
        }}

        .confidence:hover {{
            opacity: 0.8;
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}

        .modal-content {{
            background-color: white;
            margin: 15% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 500px;
            position: relative;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}

        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}

        .close:hover,
        .close:focus {{
            color: #000;
        }}

        .modal h3 {{
            margin-top: 0;
            color: #343a40;
        }}

        .modal p {{
            line-height: 1.6;
            color: #6c757d;
        }}

        .links-container {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .schedule-link {{
            display: inline-block;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            transition: background-color 0.2s ease;
        }}

        .schedule-link.primary {{
            background: #667eea;
        }}

        .schedule-link.primary:hover {{
            background: #5a6fd8;
        }}

        .schedule-link.secondary {{
            background: #6c757d;
        }}

        .schedule-link.secondary:hover {{
            background: #5a6268;
        }}

        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 6px;
            color: #6c757d;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .no-schedules {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .schedule-grid {{
                grid-template-columns: 1fr;
                padding: 15px;
                gap: 12px;
            }}

            .rink-header {{
                padding: 12px;
                font-size: 1.1em;
            }}

            .links-container {{
                flex-direction: column;
            }}

            .modal-content {{
                width: 95%;
                margin: 10% auto;
            }}
        }}

        @media (max-width: 480px) {{
            .schedule-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}

            .modal-content {{
                width: 95%;
                margin: 5% auto;
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>"""

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
        <h2 class="rink-header">🏟️ {rink_name}</h2>
        <div class="schedule-grid">"""

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
                        📄 Schedule
                    </a>
                    <a href="{parent_url}" target="_blank" class="schedule-link secondary">
                        🏟️ Main Site
                    </a>
                </div>
            </div>

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

    html += f"""
    <div class="footer">
        <p>🤖 Powered by SIRS Admin CLI with Claude AI</p>
        <p><small>Data collected automatically from ice rink websites</small></p>
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