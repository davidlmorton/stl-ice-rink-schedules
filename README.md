# SIRS - St. Louis Ice Rink Schedules

**A clean, AI-powered system for automatically finding and organizing ice rink schedules in the St. Louis area.**

## Overview

SIRS (St. Louis Ice Rink Schedules) consists of two simple components:

1. **Admin CLI** (`admin.py`) - Scrapes ice rink websites and uses Claude AI to identify current schedule PDFs
2. **Website Generator** (`generate_website.py`) - Creates a static website from the collected schedule data

## Quick Start

### 1. Setup

```bash
# Install dependencies with pipenv
pipenv install

# Add your Claude API key to .env
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 2. Configure Sites

Edit `sites.json` to add ice rink websites:

```json
{
  "sites": [
    {
      "name": "Your Ice Rink",
      "url": "https://example.com/ice-arena"
    }
  ]
}
```

### 3. Collect Schedules

```bash
pipenv run python admin.py
```

The admin CLI will:
- Scrape each site for potential schedule documents
- Use Claude AI to identify the most current schedules
- Output results to `schedules.json`

### 4. Generate Website

```bash
pipenv run python generate_website.py
```

This creates a static website in the `docs/` folder, ready for GitHub Pages.

The generator automatically handles cache-busting by using timestamps to version CSS/JS assets, ensuring browsers always load your latest changes while maintaining efficient caching.

## How It Works

1. **Crawl4AI** intelligently crawls ice rink websites with smart content filtering optimized for AI analysis
2. **Claude AI** analyzes the clean, structured content to identify current schedule links with confidence ratings
3. **JSON output** contains: ice rink name, year, month, schedule type, confidence level, and reasoning
4. **Static website** provides a mobile-friendly interface with clickable confidence badges and dual links (Schedule + Main Site)

## Output Format

The admin CLI outputs JSON with this structure:

```json
{
  "timestamp": "2025-07-19T17:42:17.863219",
  "total_schedules": 1,
  "schedules": [
    {
      "schedule_link": "https://example.com/schedule.pdf",
      "parent_page_link": "https://example.com/ice-arena",
      "ice_rink_name": "Kirkwood Ice Arena",
      "year": 2025,
      "month": "July",
      "schedule_type": "Public Skating",
      "confidence": "high",
      "reasoning": "Document references July calendar, matches current date"
    }
  ]
}
```

## Using pipenv

This project uses **pipenv** for dependency management [[memory:3761798]]. All commands should be run using `pipenv run`:

```bash
# Install dependencies
pipenv install

# Run the admin CLI
pipenv run python admin.py

# Generate the website
pipenv run python generate_website.py

# Enter the virtual environment shell (optional)
pipenv shell
```

The `Pipfile` contains unpinned dependencies, while `Pipfile.lock` contains the exact pinned versions for reproducible builds.

## Cache-Busting & Updates

The website generator automatically handles browser caching issues:

- **External Assets**: CSS and JavaScript are in separate files for better cache management
- **Version-Based URLs**: Assets include timestamp query parameters (e.g., `styles.css?v=1703532123`)
- **Automatic Updates**: Every time you regenerate the site, browsers will fetch the latest assets
- **Smart Caching**: Long-term caching for performance with automatic invalidation on updates

**Workflow for updates:**
```bash
# 1. Make your changes and collect new schedules
pipenv run python admin.py

# 2. Generate the updated website
pipenv run python generate_website.py

# 3. Commit and push your changes
git add . && git commit -m "Update schedules"
git push

# 4. GitHub Pages automatically deploys with cache-busting
```

Users will automatically get fresh content without needing to hard-refresh their browsers.

## Features

- **Simple**: No flags, no complex options - just run and go
- **Intelligent Crawling**: Crawl4AI with smart content filtering and async processing
- **Verbose**: Detailed output for easy debugging
- **Configurable**: Add any ice rink website to `sites.json`
- **AI-Powered**: Claude intelligently identifies current schedules with confidence ratings
- **Clean Output**: Professional static website ready for deployment
- **Mobile-Friendly**: Responsive design with modal dialogs for detailed reasoning
- **Dual Links**: Easy access to both schedule documents and main ice rink sites
- **Alphabetical Organization**: Rinks sorted alphabetically for easy navigation
- **Cache-Busting**: Automatic browser cache invalidation on updates without losing caching benefits

## Requirements

- Python 3.8+
- Chrome browser (for Crawl4AI web crawling)
- Anthropic Claude API key
- pipenv for dependency management

## Files

- `admin.py` - Main admin CLI for collecting schedules
- `generate_website.py` - Static website generator
- `sites.json` - Configuration file for ice rink websites
- `schedules.json` - Output data from admin CLI
- `docs/index.html` - Generated static website (with cache-busting)
- `docs/styles.css` - External stylesheet (auto-generated)
- `docs/script.js` - External JavaScript (auto-generated)
- `Pipfile` - Python dependencies
- `Pipfile.lock` - Locked dependency versions
- `.env` - Environment variables (API keys)

## License

MIT License - see LICENSE file
