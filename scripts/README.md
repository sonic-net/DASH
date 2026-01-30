# Weekly DASH/DPU/SmartSwitch Review Automation

This directory contains automation scripts to generate weekly activity reviews for DASH, DPU, and SmartSwitch development across the sonic-net organization.

## Quick Start

### Option 1: Using Bash Script (Requires GitHub CLI)

```bash
# Install GitHub CLI first: https://cli.github.com/
gh auth login

# Generate review for last 12 days
./scripts/generate_weekly_review.sh

# Generate review for specific date range
./scripts/generate_weekly_review.sh 2026-01-15 2026-01-27
```

### Option 2: Using Python Script (Requires Python + PyGithub)

```bash
# Install dependencies
pip install PyGithub python-dateutil

# Set GitHub token
export GITHUB_TOKEN='your_github_token_here'

# Generate review for last 12 days
python3 scripts/generate_weekly_review.py

# Generate review for specific date range
python3 scripts/generate_weekly_review.py 2026-01-15 2026-01-27
```

## Features

Both scripts generate reports with:

- ✅ **PRs Merged** in timeframe (with complete table)
- ✅ **PRs Created** in timeframe (with complete table)
- ✅ Repository activity breakdown
- ✅ Merge rate analysis
- ✅ Clickable links to each PR
- ✅ Automatic keyword filtering (DASH, DPU, SmartSwitch, [ssw])

## Output

Reports are saved to: `weekly_reviews/DASH_DPU_SmartSwitch_Review_[start]_to_[end].md`

Example: `weekly_reviews/DASH_DPU_SmartSwitch_Review_2026-01-15_to_2026-01-27.md`

## Automation Options

### Option A: Run Weekly via Cron (Local/Server)

Add to crontab (`crontab -e`):

```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/DASH && ./scripts/generate_weekly_review.sh
```

For Python version:
```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/DASH && GITHUB_TOKEN=xxx python3 scripts/generate_weekly_review.py
```

### Option B: Run Weekly via GitHub Actions

Create `.github/workflows/weekly-review.yml` (see example below) to automatically generate and commit weekly reviews.

### Option C: Run Manually as Needed

Simply run the script whenever you need a report:
```bash
./scripts/generate_weekly_review.sh 2026-01-15 2026-01-27
```

## GitHub Queries Used

The scripts execute these two queries:

**Query 1 - Merged PRs**:
```
org:sonic-net is:pr is:merged merged:YYYY-MM-DD..YYYY-MM-DD 
(DPU OR DASH OR SmartSwitch) in:title,body 
NOT [action] in:title NOT submodule in:title
```

**Query 2 - Created PRs**:
```
org:sonic-net is:pr created:YYYY-MM-DD..YYYY-MM-DD 
(DPU OR DASH OR SmartSwitch) in:title,body 
NOT [action] in:title NOT submodule in:title
```

## Requirements

### For Bash Script (`generate_weekly_review.sh`)
- GitHub CLI (`gh`) - https://cli.github.com/
- `jq` (JSON processor)
- `bc` (calculator for merge rate)

### For Python Script (`generate_weekly_review.py`)
- Python 3.7+
- PyGithub: `pip install PyGithub`
- python-dateutil: `pip install python-dateutil`
- GitHub Personal Access Token (in `GITHUB_TOKEN` env var)

## GitHub Token Setup

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "DASH Weekly Review"
4. Select scopes: `public_repo` (or `repo` for private repos)
5. Generate and copy the token
6. Set environment variable:
   ```bash
   export GITHUB_TOKEN='your_token_here'
   ```

For permanent setup, add to `~/.bashrc` or `~/.zshrc`:
```bash
export GITHUB_TOKEN='your_token_here'
```

## Customization

Edit the scripts to customize:

- **Keywords**: Change the `KEYWORDS` variable
- **Organization**: Change `ORG` variable to query different orgs
- **Date range**: Default is 12 days, modify as needed
- **Output directory**: Change `OUTPUT_DIR` to save reports elsewhere
- **Filters**: Modify the query strings to add/remove filters

## Troubleshooting

### "Command not found: gh"
Install GitHub CLI: https://cli.github.com/manual/installation

### "Not authenticated with GitHub CLI"
Run: `gh auth login` and follow prompts

### "ModuleNotFoundError: No module named 'github'"
Install PyGithub: `pip install PyGithub`

### "API rate limit exceeded"
Set GITHUB_TOKEN environment variable with a valid GitHub token

### "Permission denied"
Make scripts executable: `chmod +x scripts/generate_weekly_review.sh scripts/generate_weekly_review.py`

## Example Workflow

Typical weekly workflow:

```bash
# Monday morning - generate last week's review
cd /path/to/DASH
./scripts/generate_weekly_review.sh

# View the generated report
cat weekly_reviews/DASH_DPU_SmartSwitch_Review_*.md | head -100

# Open in editor for review
code weekly_reviews/DASH_DPU_SmartSwitch_Review_2026-01-15_to_2026-01-27.md

# Optionally commit to repo for historical tracking
git add weekly_reviews/
git commit -m "Add weekly review for Jan 15-27, 2026"
```

## Files in This Directory

- `generate_weekly_review.sh` - Bash script using GitHub CLI
- `generate_weekly_review.py` - Python script using PyGithub API
- `README.md` - This file

## Output Directory

The `weekly_reviews/` directory (created automatically) contains:
- Weekly review markdown files
- Historical reviews for tracking trends over time
- Can be committed to git or kept local

**Note**: The `weekly_reviews/` directory is added to `.gitignore` by default to avoid cluttering the repository. Remove from `.gitignore` if you want to commit historical reviews.

## Support

For issues or questions:
- File an issue: https://github.com/sonic-net/DASH/issues
- Review existing documentation in the main DASH repository

---

*Created: January 2026*  
*Maintainer: DASH Project Team*
