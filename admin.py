#!/usr/bin/env python3
"""
SIRS Admin CLI - Schedule Information Retrieval System
Finds ice rink schedule links using Crawl4AI and Claude AI
"""

import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Load environment variables
load_dotenv()

class IceScheduleFinder:
    def __init__(self):
        print("🚀 Initializing SIRS Admin CLI with Crawl4AI...")
        self.claude_client = None
        self.init_claude()
        print("✅ SIRS Admin CLI ready")

    def init_claude(self):
        """Initialize Claude AI client"""
        print("🤖 Setting up Claude AI...")
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("❌ ANTHROPIC_API_KEY not found in environment variables")

        self.claude_client = anthropic.Anthropic(api_key=api_key)
        print("✅ Claude AI ready")

    def load_sites_config(self, config_file="sites.json"):
        """Load sites configuration"""
        print(f"📋 Loading sites configuration from {config_file}...")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded {len(config.get('sites', []))} sites")
            return config.get('sites', [])
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {config_file}: {e}")
            return []

    async def crawl_site_with_crawl4ai(self, site):
        """Use Crawl4AI to scrape and clean site content for LLM analysis"""
        site_name = site.get('name', 'Unknown')
        url = site.get('url', '')

        print(f"\n🔍 Crawling {site_name} with Crawl4AI...")
        print(f"    URL: {url}")

        if not url:
            print("❌ No URL provided for site")
            return None

        try:
            # Configure browser for crawling
            browser_config = BrowserConfig(
                headless=True,
                verbose=True
            )

            # Configure crawl settings with smart content filtering
            crawl_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,  # Always get fresh content for schedules
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(
                        threshold=0.20,  # Lower threshold to keep more content
                        threshold_type="fixed",
                        min_word_threshold=0
                    )
                ),
                wait_for_timeout=5000,  # Wait 5 seconds for content to load
                page_timeout=15000,  # Increase page timeout
                remove_overlay_elements=True,  # Remove popup overlays
                screenshot=False,  # Don't need screenshots for schedules
                js_code=[
                    "window.scrollTo(0, document.body.scrollHeight);",  # Scroll to load content
                    "await new Promise(resolve => setTimeout(resolve, 3000));"  # Wait 3 more seconds
                ],
                verbose=True
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config
                )

                if result.success:
                    # Get LLM-optimized content
                    clean_markdown = result.markdown.fit_markdown  # Pre-filtered for LLMs
                    raw_html = result.html

                    # Extract all links found by Crawl4AI
                    all_links = []
                    if result.links:
                        internal_links = result.links.get('internal', [])
                        external_links = result.links.get('external', [])
                        all_links = internal_links + external_links

                    print(f"✅ Crawl4AI successfully processed {site_name}")
                    print(f"    Content: {len(clean_markdown)} clean markdown chars")
                    print(f"    Links: {len(all_links)} total links found")

                    return {
                        'url': url,
                        'title': result.metadata.get('title', ''),
                        'clean_markdown': clean_markdown,
                        'raw_html': raw_html,
                        'all_links': all_links,
                        'metadata': result.metadata
                    }
                else:
                    print(f"❌ Crawl4AI failed for {site_name}: {result.error_message}")
                    return None

        except Exception as e:
            print(f"❌ Error crawling {site_name} with Crawl4AI: {e}")
            return None

    def ask_claude_to_find_schedules(self, site_name, crawl_data):
        """Use Claude to analyze Crawl4AI content and find relevant schedule links"""
        if not crawl_data:
            return []

        print(f"🤖 Asking Claude to analyze Crawl4AI content for {site_name}...")

        current_date = datetime.now()
        current_month = current_date.strftime('%B')
        current_year = current_date.year
        next_month_date = datetime(current_year if current_date.month < 12 else current_year + 1,
                                 current_date.month + 1 if current_date.month < 12 else 1, 1)
        next_month = next_month_date.strftime('%B')
        next_year = next_month_date.year

        # Use the clean markdown that Crawl4AI already optimized for LLMs
        clean_content = crawl_data['clean_markdown'][:15000]  # Generous limit since content is pre-filtered

        # Debug: Show what content we're actually sending to Claude
        print(f"🔍 DEBUG: Site name: '{site_name}'")
        print(f"🔍 DEBUG: Content length: {len(clean_content)} chars")

        if "kirkwood" in site_name.lower():
            print(f"🔍 DEBUG: Kirkwood content sample (chars 3000-4000):")
            print(f"    {clean_content[3000:4000]}")
            print(f"🔍 DEBUG: Links containing 'mailto', 'august', or 'coates':")
            for i, link in enumerate(crawl_data['all_links']):
                if isinstance(link, dict) and 'url' in link:
                    url = link['url']
                elif isinstance(link, str):
                    url = link
                else:
                    continue

                if url and ('mailto' in url.lower() or 'august' in url.lower() or 'coates' in url.lower()):
                    print(f"    Found: {url}")

        if "creve coeur" in site_name.lower():
            print(f"🔍 DEBUG: Creve Coeur content first 1000 chars:")
            print(f"    {clean_content[:1000]}")
            print(f"🔍 DEBUG: All links (first 20):")
            for i, link in enumerate(crawl_data['all_links'][:20]):
                if isinstance(link, dict) and 'url' in link:
                    url = link['url']
                    text = link.get('text', '')
                elif isinstance(link, str):
                    url = link
                    text = ''
                else:
                    continue
                print(f"    {i+1}. {url} (text: '{text}')")

            print(f"🔍 DEBUG: Links containing 'imagerepository', 'document', or ID numbers:")
            for i, link in enumerate(crawl_data['all_links']):
                if isinstance(link, dict) and 'url' in link:
                    url = link['url']
                elif isinstance(link, str):
                    url = link
                else:
                    continue

                if url and ('imagerepository' in url.lower() or 'document' in url.lower() or '13239' in url or '13287' in url):
                    print(f"    Found: {url}")

        prompt = f"""You are analyzing LLM-optimized webpage content from {site_name} to help users find current ice rink schedule information. The content has been pre-processed by Crawl4AI to remove irrelevant elements.

CURRENT DATE: {current_date.strftime('%B %d, %Y')}
TARGET MONTHS: {current_month} {current_year} and {next_month} {next_year}

WEBPAGE DATA:
URL: {crawl_data['url']}
Title: {crawl_data['title']}

CRAWL4AI CLEANED CONTENT:
{clean_content}

EXTRACTED LINKS:
{json.dumps(crawl_data['all_links'][:50], indent=2)}

TASK: Find ANY links or references that help users access current ice rink schedule information for {current_month} {current_year} and {next_month} {next_year}.

SPECIAL ATTENTION FOR CREVE COEUR SCHEDULE PATTERNS:
- Look for "ImageRepository/Document?documentID=" URLs (common for schedule images)
- Document IDs like 13239, 13287 may reference current schedules
- Text like "July 2025 Public" or "August 2025 Public" indicates schedule content
- PDF documents, calendar pages, schedule viewers
- Any reference to current month ice times, public skating, hockey schedules

SEARCH PRIORITY:
1. Direct links to schedule documents (PDFs, ImageRepository URLs, calendar pages)
2. Pages that mention current month schedules
3. General ice arena information pages (as fallback)

FOCUS ON GENERAL ICE SCHEDULES ONLY:
- Public skating schedules and times
- Hockey schedules (league play, drop-in hockey)
- Open ice sessions
- General ice arena operating hours
- Monthly ice time calendars
- Freestyle/figure skating session times (when part of general schedule)

DO NOT INCLUDE LESSONS/PROGRAMS:
- Skating lessons or learn-to-skate programs
- Hockey camps or clinics
- Figure skating lessons or camps
- Youth programs or workshops
- Registration pages for lessons/programs
- Class schedules for instructional programs

WHAT TO INCLUDE:
- Direct URLs to schedule documents (PDFs, images, HTML pages)
- ImageRepository document links with document IDs
- Calendar or schedule viewer pages showing ice times
- Any page where users can VIEW current general ice schedules
- Month-specific schedule references for general ice use
- Parent pages that contain or link to general schedules

WHAT TO AVOID:
- General navigation links
- Registration-only pages
- Social media links
- Obviously unrelated content
- mailto: email links (these are contact info, not schedules)
- Contact information or phone numbers
- Staff directory pages
- Lesson/program registration systems
- Instructional program schedules

REQUIREMENTS FOR VALID SCHEDULE LINKS:
- Must be a clickable URL (http/https) that leads to viewable schedule content
- Must NOT be email addresses (mailto:) or phone numbers
- Must actually display or contain schedule information users can view

Focus on being helpful to users who need current ice rink schedules for {current_month} and {next_month}.

Respond with valid JSON only:

{{
  "schedules": [
    {{
      "schedule_link": "<direct_url_to_schedule_document_or_page>",
      "parent_page_link": "<url_of_page_that_contains_or_references_this_schedule>",
      "ice_rink_name": "{site_name}",
      "year": <year>,
      "month": "<month_name>",
      "schedule_type": "<type_of_schedule>",
      "confidence": "high|medium|low",
      "reasoning": "<explanation_of_why_this_helps_users_find_schedules>"
    }}
  ]
}}

Extract every relevant schedule URL from the cleaned content and links. Include both direct schedule links AND the parent pages that reference them."""

        try:
            message = self.claude_client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text.strip()
            print(f"🤖 Claude analysis complete")

            # Parse Claude's JSON response
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    claude_analysis = json.loads(json_text)

                    if 'schedules' in claude_analysis:
                        schedules = claude_analysis['schedules']
                        print(f"✅ Claude identified {len(schedules)} relevant schedules")
                        for i, schedule in enumerate(schedules, 1):
                            print(f"   {i}. {schedule.get('month', 'Unknown')} {schedule.get('year', 'Unknown')} - {schedule.get('schedule_type', 'Unknown type')} - {schedule.get('confidence', 'unknown')} confidence")
                            print(f"      Schedule Link: {schedule.get('schedule_link', '')}")
                            print(f"      Parent Page: {schedule.get('parent_page_link', '')}")
                        return schedules
                    else:
                        print("❌ Claude response missing 'schedules' field")
                        return []
                else:
                    print("❌ No valid JSON found in Claude response")
                    return []

            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"📄 Raw Claude response: {response_text}")
                return []

        except Exception as e:
            print(f"❌ Error calling Claude: {e}")
            return []

    def filter_best_schedules_per_month(self, all_schedules):
        """Second pass: Use Claude to select the very best schedule link for each (location, month) combination"""
        if not all_schedules:
            return []

        print(f"\n🔍 Second Pass: Filtering {len(all_schedules)} schedules to find the best link per location per month...")

        # Group schedules by ice_rink_name + month-year
        location_month_groups = {}
        for schedule in all_schedules:
            ice_rink = schedule.get('ice_rink_name', 'Unknown')
            month = schedule.get('month', 'Unknown')
            year = schedule.get('year', 'Unknown')
            key = f"{ice_rink} - {month} {year}"

            if key not in location_month_groups:
                location_month_groups[key] = []
            location_month_groups[key].append(schedule)

        print(f"📅 Found schedules for {len(location_month_groups)} location-month combination(s):")
        for key in sorted(location_month_groups.keys()):
            print(f"    • {key} ({len(location_month_groups[key])} schedules)")

        filtered_schedules = []

        for location_month, schedules in location_month_groups.items():
            if len(schedules) == 1:
                # Only one schedule for this location-month, but still check parent_link != schedule_link
                schedule = schedules[0]
                if schedule.get('parent_page_link') != schedule.get('schedule_link'):
                    filtered_schedules.append(schedule)
                    print(f"✅ {location_month}: Only 1 schedule found, keeping it")
                else:
                    print(f"⚠️  {location_month}: Skipping - parent_link same as schedule_link")
                continue

            print(f"\n🤖 Analyzing {len(schedules)} schedules for {location_month}...")

            # Create prompt for Claude to choose the best schedule
            schedules_json = json.dumps(schedules, indent=2)

            prompt = f"""You are analyzing multiple schedule links found for {location_month} ice rink schedules. Your job is to select the SINGLE BEST link that will help users find current ice skating schedules.

SCHEDULES TO ANALYZE:
{schedules_json}

SELECTION CRITERIA (in order of importance):
1. MUST EXCLUDE: Links where parent_page_link is the same as schedule_link (these are usually navigation pages, not direct schedule documents)
2. PREFER: Direct links to schedule documents (PDFs, ImageRepository documents, calendar viewers)
3. PREFER: Links with "high" confidence over "medium" or "low"
4. PREFER: Links that specifically mention the target month in their reasoning or URL
5. PREFER: Links to actual schedule documents over general information pages
6. AVOID: General navigation links, contact pages, or registration systems

TASK: Select the single best schedule link for {location_month}. If all links have parent_page_link = schedule_link, return null.

Respond with valid JSON only:
{{
  "selected_schedule": <full_schedule_object_or_null>,
  "reasoning": "<explanation_of_why_this_is_the_best_choice>",
  "rejected_count": <number_of_schedules_rejected>
}}"""

            try:
                message = self.claude_client.messages.create(
                    model="claude-opus-4-5-20251101",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                response_text = message.content[0].text.strip()

                # Parse Claude's JSON response
                try:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1

                    if json_start != -1 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        analysis = json.loads(json_text)

                        selected = analysis.get('selected_schedule')
                        reasoning = analysis.get('reasoning', 'No reasoning provided')
                        rejected_count = analysis.get('rejected_count', 0)

                        if selected:
                            filtered_schedules.append(selected)
                            print(f"✅ {location_month}: Selected best schedule (rejected {rejected_count})")
                            print(f"   📄 Link: {selected.get('schedule_link', '')}")
                            print(f"   🧠 Reasoning: {reasoning}")
                        else:
                            print(f"❌ {location_month}: No valid schedules found (rejected {rejected_count})")
                            print(f"   🧠 Reasoning: {reasoning}")

                    else:
                        print(f"❌ {location_month}: No valid JSON in Claude response")

                except json.JSONDecodeError as e:
                    print(f"❌ {location_month}: JSON parsing error: {e}")

            except Exception as e:
                print(f"❌ {location_month}: Error calling Claude for filtering: {e}")

        print(f"\n📊 Second pass complete: {len(all_schedules)} → {len(filtered_schedules)} schedules")
        return filtered_schedules

    def add_static_schedules(self, schedules):
        """Add hard-coded schedule links that never change"""
        print(f"\n📌 Adding static/hard-coded schedule links...")

        current_date = datetime.now()
        current_month = current_date.strftime('%B')
        current_year = current_date.year
        next_month_date = datetime(current_year if current_date.month < 12 else current_year + 1,
                                 current_date.month + 1 if current_date.month < 12 else 1, 1)
        next_month = next_month_date.strftime('%B')
        next_year = next_month_date.year

        static_schedules = [
            {
                "schedule_link": "https://centene.finnlyconnect.com/registration/activityitem/4762",
                "parent_page_link": "https://www.centenecommunityicecenter.com/ice-skating/public-skating-1",
                "ice_rink_name": "Centene Community Ice Center",
                "year": current_year,
                "month": current_month,
                "schedule_type": "Public Skating Registration",
                "confidence": "high",
                "reasoning": "Hard-coded static link that never changes - direct registration page for public skating"
            },
            {
                "schedule_link": "https://centene.finnlyconnect.com/registration/activityitem/4762",
                "parent_page_link": "https://www.centenecommunityicecenter.com/ice-skating/public-skating-1",
                "ice_rink_name": "Centene Community Ice Center",
                "year": next_year,
                "month": next_month,
                "schedule_type": "Public Skating Registration",
                "confidence": "high",
                "reasoning": "Hard-coded static link that never changes - direct registration page for public skating"
            }
        ]

        # Add static schedules to the results
        schedules.extend(static_schedules)
        print(f"✅ Added {len(static_schedules)} static schedule(s) for Centene Community Ice Center")

        return schedules

    async def process_all_sites(self):
        """Process all sites and collect schedule information using Crawl4AI"""
        print("\n" + "=" * 80)
        print("🚀 SIRS Admin CLI - Starting schedule collection with Crawl4AI")
        print("=" * 80)

        # Load sites configuration
        sites = self.load_sites_config()
        if not sites:
            print("❌ No sites to process")
            return []

        all_schedules = []

        for i, site in enumerate(sites, 1):
            print(f"\n📍 Processing site {i}/{len(sites)}")

            # Use Crawl4AI to get clean, LLM-optimized content
            crawl_data = await self.crawl_site_with_crawl4ai(site)

            if crawl_data:
                # Use Claude to analyze the clean content and find schedules
                schedules = self.ask_claude_to_find_schedules(
                    site.get('name', 'Unknown'),
                    crawl_data
                )
                all_schedules.extend(schedules)
            else:
                print(f"⚠️  Could not crawl content for {site.get('name', 'Unknown')}")

        print(f"\n" + "=" * 80)
        print(f"✅ First pass complete! Found {len(all_schedules)} total schedules")
        print("=" * 80)

        # Second pass: Filter to best schedule per month
        if all_schedules:
            filtered_schedules = self.filter_best_schedules_per_month(all_schedules)

            # Add static/hard-coded schedules
            final_schedules = self.add_static_schedules(filtered_schedules)

            print(f"\n" + "=" * 80)
            print(f"🎯 Final results: {len(final_schedules)} high-quality schedules (including static links)")
            print("=" * 80)
            return final_schedules
        else:
            # Even if no dynamic schedules found, still add static ones
            static_only = self.add_static_schedules([])
            return static_only

    def save_results(self, schedules, output_file="schedules.json"):
        """Save results to JSON file"""
        print(f"\n💾 Saving results to {output_file}...")

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "total_schedules": len(schedules),
            "description": "High-quality ice rink schedules selected via two-pass AI filtering plus static hard-coded links",
            "filtering_notes": "Second pass removed duplicates and selected best link per (location, month) combination where parent_page_link != schedule_link. Static schedules added for reliable links that never change.",
            "schedules": schedules
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"✅ Results saved to {output_file}")

async def main():
    """Main entry point"""
    finder = IceScheduleFinder()

    try:
        # Process all sites and collect schedules
        schedules = await finder.process_all_sites()

        # Save results
        if schedules:
            finder.save_results(schedules)

            # Print summary
            print(f"\n📊 FINAL SUMMARY (Two-Pass Filtered Results):")
            for schedule in schedules:
                print(f"   • {schedule.get('ice_rink_name', 'Unknown')} - {schedule.get('month', '?')} {schedule.get('year', '?')} - {schedule.get('schedule_type', 'Unknown')}")
                print(f"     📄 Schedule: {schedule.get('schedule_link', '')}")
                print(f"     🏠 Parent: {schedule.get('parent_page_link', '')}")
                print(f"     🎯 Confidence: {schedule.get('confidence', 'unknown')}")
        else:
            print("\n⚠️  No schedules found")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
