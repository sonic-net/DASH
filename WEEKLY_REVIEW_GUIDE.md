# Weekly Review Automation - Quick Start Guide

## What This Does

Automatically generates weekly activity reports tracking DASH, DPU, and SmartSwitch PRs across all sonic-net repositories.

**Matches your queries**:
- `org:sonic-net is:pr is:merged merged:2026-01-15..2026-01-27 (DPU OR DASH OR SmartSwitch) in:title,body`
- `org:sonic-net is:pr created:2026-01-15..2026-01-27 (DPU OR DASH OR SmartSwitch) in:title,body`

## How to Use

### 🚀 Quick Run (This Week)

**Using Bash** (easiest if you have GitHub CLI):
```bash
./scripts/generate_weekly_review.sh
```

**Using Python**:
```bash
export GITHUB_TOKEN='your_token'
python3 scripts/generate_weekly_review.py
```

### 📅 Specific Date Range

```bash
# Bash
./scripts/generate_weekly_review.sh 2026-01-15 2026-01-27

# Python
python3 scripts/generate_weekly_review.py 2026-01-15 2026-01-27
```

### 📄 View Output

```bash
# Reports saved to:
cat weekly_reviews/DASH_DPU_SmartSwitch_Review_2026-01-15_to_2026-01-27.md
```

## Setup (First Time Only)

### For Bash Script

1. **Install GitHub CLI**: https://cli.github.com/
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

2. **Authenticate**:
   ```bash
   gh auth login
   ```

3. **Run**:
   ```bash
   ./scripts/generate_weekly_review.sh
   ```

### For Python Script

1. **Install Python dependencies**:
   ```bash
   pip install PyGithub python-dateutil
   ```

2. **Get GitHub token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `public_repo`
   - Copy the token

3. **Set environment variable**:
   ```bash
   export GITHUB_TOKEN='ghp_xxxxxxxxxxxx'
   ```

4. **Run**:
   ```bash
   python3 scripts/generate_weekly_review.py
   ```

## Weekly Automation

### Option 1: Crontab (Recommended for Personal Use)

```bash
# Edit crontab
crontab -e

# Add this line to run every Tuesday at 2 PM
0 14 * * 2 cd /path/to/DASH && ./scripts/generate_weekly_review.sh
```

### Option 2: GitHub Actions (Recommended for Team Use)

The workflow `.github/workflows/weekly-review.yml` is included:

- **Runs**: Every Tuesday at 2 PM UTC
- **Output**: Creates PR with weekly review
- **Manual**: Can also trigger manually from Actions tab

To enable:
1. Workflow file is already committed
2. It will run automatically every Tuesday
3. Or trigger manually: GitHub → Actions → Weekly Review → Run workflow

## Output Format

Each report includes:

```markdown
# DASH/DPU/SmartSwitch Weekly Activity Review

## Executive Summary
- X PRs merged
- Y PRs created

## PRs Merged (Complete List)
| # | Repository | PR | Title | Merged | Link |
[Full table with all merged PRs]

## PRs Created (Complete List)
| # | Repository | PR | Title | Created | State | Link |
[Full table with all created PRs]

## Analysis
- Merge rate
- Most active repositories
- Key focus areas
```

## What Gets Tracked

**Keywords** (in PR title or body):
- DASH
- DPU
- Smart
- SmartSwitch
- 'Smart Switch'
- [ssw]

**Filters out**:
- PRs with `[action]` label (bot PRs)
- Submodule update PRs

**Repositories**: All sonic-net repositories

## Tips

1. **Weekly Routine**: Run every Tuesday to track last week's activity
2. **Date Range**: Use 12-day windows (covers weekends)
3. **Historical Tracking**: Save reports to track trends over time
4. **Compare**: Look at merge rates and repository activity patterns
5. **Custom Dates**: Generate reports for any timeframe you need

## Advanced Usage

### Generate Multiple Weeks

```bash
# Generate reviews for last 4 weeks
for i in {0..3}; do
  start=$(date -d "$((i*7+12)) days ago" +%Y-%m-%d)
  end=$(date -d "$((i*7)) days ago" +%Y-%m-%d)
  ./scripts/generate_weekly_review.sh $start $end
done
```

### Custom Keywords

Edit the script and modify the `KEYWORDS` variable:
```bash
KEYWORDS="DPU OR DASH OR SmartSwitch OR YourKeyword"
```

### Different Organization

Change the `ORG` variable to track a different organization:
```bash
ORG="your-org-name"
```

## Files Created

After running:
```
DASH/
├── scripts/
│   ├── generate_weekly_review.sh    (Bash version)
│   ├── generate_weekly_review.py    (Python version)
│   └── README.md                     (Detailed docs)
├── weekly_reviews/                   (Output directory)
│   └── DASH_DPU_SmartSwitch_Review_YYYY-MM-DD_to_YYYY-MM-DD.md
└── WEEKLY_REVIEW_GUIDE.md            (This file)
```

## Next Steps

1. ✅ Choose your preferred method (Bash or Python)
2. ✅ Complete setup (install tools, authenticate)
3. ✅ Run first report to test
4. ✅ Set up weekly automation (cron or GitHub Actions)
5. ✅ Integrate into your weekly workflow

---

For detailed documentation, see: `scripts/README.md`
