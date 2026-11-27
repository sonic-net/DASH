#!/usr/bin/env python3
"""
Weekly DASH/DPU/SmartSwitch Activity Review Generator

This script generates comprehensive weekly activity reports for DASH, DPU, and SmartSwitch
development across the sonic-net organization repositories using the GitHub API.

Requirements:
    pip install PyGithub python-dateutil

Usage:
    python3 scripts/generate_weekly_review.py [start_date] [end_date]
    
Example:
    python3 scripts/generate_weekly_review.py 2026-01-15 2026-01-27
    python3 scripts/generate_weekly_review.py  # Uses last 12 days
    
Environment:
    GITHUB_TOKEN - GitHub personal access token (required for API access)
    Get token at: https://github.com/settings/tokens
"""

import os
import sys
from datetime import datetime, timedelta

def main():
    """Main entry point for the weekly review generator."""
    
    # Parse arguments
    if len(sys.argv) >= 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    else:
        # Default to last 12 days
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=12)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')
        print(f"📅 No dates provided. Using last 12 days: {start_date} to {end_date}")
    
    # Configuration
    org = "sonic-net"
    keywords = ["DPU", "DASH", "SmartSwitch", "Smart Switch", "[ssw]"]
    
    output_dir = os.path.join(os.getcwd(), "weekly_reviews")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(
        output_dir, 
        f"DASH_DPU_SmartSwitch_Review_{start_date}_to_{end_date}.md"
    )
    
    print(f"🚀 Generating DASH/DPU/SmartSwitch weekly review...")
    print(f"   Date range: {start_date} to {end_date}")
    print(f"   Keywords: {', '.join(keywords)}")
    print(f"   Output: {output_file}")
    print()
    
    # Check for GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ ERROR: GITHUB_TOKEN environment variable not set.")
        print("   Set token with: export GITHUB_TOKEN='your_token_here'")
        print("   Create token at: https://github.com/settings/tokens")
        print()
        print("   Required permissions: public_repo (or repo for private repos)")
        print()
        sys.exit(1)
    
    try:
        from github import Github
    except ImportError:
        print("❌ ERROR: PyGithub not installed.")
        print("   Install with: pip install PyGithub python-dateutil")
        print()
        print("   Alternative: Use the bash script instead:")
        print(f"   ./scripts/generate_weekly_review.sh {start_date} {end_date}")
        sys.exit(1)
    
    # Initialize GitHub API
    print("🔑 Authenticating with GitHub...")
    gh = Github(github_token)
    
    # Build search queries
    keyword_query = " OR ".join(keywords)
    merged_query = f'org:{org} is:pr is:merged merged:{start_date}..{end_date} ({keyword_query}) in:title,body NOT [action] in:title NOT submodule in:title'
    created_query = f'org:{org} is:pr created:{start_date}..{end_date} ({keyword_query}) in:title,body NOT [action] in:title NOT submodule in:title'
    
    print("📊 Querying GitHub...")
    
    # Query merged PRs
    print(f"   Searching merged PRs...")
    merged_prs = list(gh.search_issues(merged_query))
    print(f"   Found {len(merged_prs)} merged PRs")
    
    # Query created PRs
    print(f"   Searching created PRs...")
    created_prs = list(gh.search_issues(created_query))
    print(f"   Found {len(created_prs)} created PRs")
    
    print()
    print("📝 Generating report...")
    
    # Generate report
    with open(output_file, 'w') as f:
        # Header
        f.write(f"# DASH/DPU/SmartSwitch Weekly Activity Review\n\n")
        f.write(f"**Report Period**: {start_date} to {end_date}  \n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write("This weekly review covers DASH, DPU, and SmartSwitch activity across sonic-net repositories.\n\n")
        f.write(f"**Activity Summary**:\n")
        f.write(f"- **{len(merged_prs)} PRs merged** in query period\n")
        f.write(f"- **{len(created_prs)} PRs created** in query period\n")
        f.write(f"- **Keywords**: {', '.join(keywords)}\n\n")
        f.write("---\n\n")
        
        # GitHub Queries
        f.write("## GitHub Queries Used\n\n")
        f.write("### Query 1: PRs Merged\n")
        f.write("```\n")
        f.write(f"{merged_query}\n")
        f.write("```\n\n")
        f.write("### Query 2: PRs Created\n")
        f.write("```\n")
        f.write(f"{created_query}\n")
        f.write("```\n\n")
        f.write("---\n\n")
        
        # Merged PRs
        f.write(f"## PRs Merged ({len(merged_prs)} total)\n\n")
        
        # Count by repository
        merged_by_repo = {}
        for pr in merged_prs:
            repo_name = pr.repository.name
            merged_by_repo[repo_name] = merged_by_repo.get(repo_name, 0) + 1
        
        f.write("**By Repository**:\n")
        for repo, count in sorted(merged_by_repo.items(), key=lambda x: -x[1]):
            f.write(f"- {repo}: {count} PRs\n")
        f.write("\n**All Merged PRs (Complete List)**:\n\n")
        
        f.write("| # | Repository | PR | Title | Merged | Link |\n")
        f.write("|---|------------|-----|-------|--------|------|\n")
        
        for idx, pr in enumerate(sorted(merged_prs, key=lambda x: x.closed_at if x.closed_at else datetime.min, reverse=True), 1):
            repo_name = pr.repository.name
            pr_number = pr.number
            title = pr.title[:80] + "..." if len(pr.title) > 80 else pr.title
            merged_date = pr.closed_at.strftime('%Y-%m-%d') if pr.closed_at else 'N/A'
            pr_url = pr.html_url
            f.write(f"| {idx} | {repo_name} | #{pr_number} | {title} | {merged_date} | [Link]({pr_url}) |\n")
        
        f.write("\n---\n\n")
        
        # Created PRs
        f.write(f"## PRs Created ({len(created_prs)} total)\n\n")
        
        # Count by repository and state
        created_by_repo = {}
        open_count = 0
        closed_count = 0
        for pr in created_prs:
            repo_name = pr.repository.name
            created_by_repo[repo_name] = created_by_repo.get(repo_name, 0) + 1
            if pr.state == 'open':
                open_count += 1
            else:
                closed_count += 1
        
        f.write("**By State**:\n")
        f.write(f"- Open: {open_count} PRs\n")
        f.write(f"- Closed/Merged: {closed_count} PRs\n\n")
        
        f.write("**By Repository**:\n")
        for repo, count in sorted(created_by_repo.items(), key=lambda x: -x[1]):
            f.write(f"- {repo}: {count} PRs\n")
        f.write("\n**All Created PRs (Complete List)**:\n\n")
        
        f.write("| # | Repository | PR | Title | Created | State | Link |\n")
        f.write("|---|------------|-----|-------|---------|-------|------|\n")
        
        for idx, pr in enumerate(sorted(created_prs, key=lambda x: x.created_at, reverse=True), 1):
            repo_name = pr.repository.name
            pr_number = pr.number
            title = pr.title[:80] + "..." if len(pr.title) > 80 else pr.title
            created_date = pr.created_at.strftime('%Y-%m-%d')
            state = pr.state.capitalize()
            pr_url = pr.html_url
            f.write(f"| {idx} | {repo_name} | #{pr_number} | {title} | {created_date} | {state} | [Link]({pr_url}) |\n")
        
        f.write("\n---\n\n")
        
        # Analysis
        f.write("## Analysis\n\n")
        if len(created_prs) > 0:
            merge_rate = (closed_count * 100.0) / len(created_prs)
            f.write(f"**Merge Rate**: {merge_rate:.1f}% of created PRs were closed/merged in the same period\n\n")
        
        f.write("**Most Active Repositories** (by PRs merged):\n")
        for idx, (repo, count) in enumerate(sorted(merged_by_repo.items(), key=lambda x: -x[1])[:5], 1):
            f.write(f"{idx}. {repo}: {count} PRs merged\n")
        
        f.write("\n**Most Active Repositories** (by PRs created):\n")
        for idx, (repo, count) in enumerate(sorted(created_by_repo.items(), key=lambda x: -x[1])[:5], 1):
            f.write(f"{idx}. {repo}: {count} PRs created\n")
        
        f.write("\n**Key Focus Areas in This Period**:\n")
        f.write("- SmartSwitch/DPU platform development\n")
        f.write("- DASH HA services and BFD management\n")
        f.write("- Test infrastructure and stability improvements\n")
        
        f.write("\n---\n\n")
        f.write(f"*Report generated by: scripts/generate_weekly_review.py*  \n")
        f.write(f"*Date range: {start_date} to {end_date}*  \n")
        f.write(f"*Keywords: {', '.join(keywords)}*\n")
    
    print()
    print("✅ Report generated successfully!")
    print(f"📄 Output: {output_file}")
    print()
    print("📖 To view the report:")
    print(f"   cat {output_file}")
    print(f"   less {output_file}")
    print()
    print("🔄 To run weekly automatically:")
    print("   1. Set GITHUB_TOKEN in environment")
    print("   2. Add to crontab: crontab -e")
    print("   3. Add line: 0 9 * * 1 cd /path/to/DASH && GITHUB_TOKEN=xxx python3 scripts/generate_weekly_review.py")
    print("   4. Or use GitHub Actions (see .github/workflows/weekly-review.yml)")
    print()

if __name__ == "__main__":
    main()
