#!/usr/bin/env python3
"""
SIRS Website Generator
Generates a static HTML website from the schedules JSON data
"""

import json
import os
from datetime import datetime

def get_cache_version():
    """Get a cache version based on current timestamp"""
    return str(int(datetime.now().timestamp()))

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

def generate_html(schedules, version):
    """Generate HTML content from schedules data with cache busting"""

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

    # Generate HTML with external assets and cache busting
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>St. Louis Ice Rink Schedules</title>

    <!-- Cache control meta tags -->
    <meta http-equiv="Cache-Control" content="max-age=31536000, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">

    <!-- External stylesheets and scripts with cache busting -->
    <link rel="stylesheet" href="styles.css?v={version}">
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

    <script src="script.js?v={version}"></script>
</body>
</html>"""

    return html

def main():
    """Main entry point"""
    print("🚀 SIRS Website Generator")
    print("=" * 40)

    # Get cache version
    print("🔢 Getting cache version...")
    version = get_cache_version()
    print(f"✅ Cache version: {version}")

    # Load schedules data
    print("📋 Loading schedules data...")
    schedules = load_schedules()

    if not schedules:
        print("⚠️  No schedules found, generating empty website")
    else:
        print(f"✅ Loaded {len(schedules)} schedules")

    # Generate HTML
    print("🎨 Generating HTML...")
    html_content = generate_html(schedules, version)

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