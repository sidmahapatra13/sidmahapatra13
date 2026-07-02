#!/usr/bin/env python3
"""
Generate a top-languages SVG card for GitHub profile README.
Fetches language data from GitHub API and creates a compact bar chart.
"""

import os
import json
import urllib.request
from collections import defaultdict

# Configuration
USERNAME = "sidmahapatra13"
OUTPUT_FILE = "assets/top-langs.svg"
MAX_LANGS = 5

# Language colors (GitHub's official colors)
LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "R": "#198CE7",
    "Scala": "#c22d40",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
    "Vue": "#41b883",
    "Svelte": "#ff3e00",
    "Lua": "#000080",
    "Haskell": "#5e5086",
    "Elixir": "#6e4a7e",
    "Clojure": "#db5855",
    "Julia": "#a270ba",
    "Zig": "#ec915c",
    "Nim": "#ffc200",
    "OCaml": "#3be133",
    "Perl": "#0298c3",
    "Assembly": "#6E4C13",
    "MATLAB": "#e16737",
    "Objective-C": "#438eff",
}

DEFAULT_COLOR = "#8b8b8b"


def fetch_json(url):
    """Fetch JSON from URL with optional GitHub token."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_all_repos_languages(username):
    """Aggregate language bytes across all user repos."""
    lang_bytes = defaultdict(int)
    page = 1
    
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        repos = fetch_json(url)
        
        if not repos:
            break
        
        for repo in repos:
            if repo.get("fork"):
                continue
            
            try:
                langs = fetch_json(repo["languages_url"])
                for lang, bytes_count in langs.items():
                    lang_bytes[lang] += bytes_count
            except Exception:
                continue
        
        page += 1
    
    return dict(lang_bytes)


def create_svg(lang_data, max_langs=5):
    """Create a compact top-languages SVG card."""
    # Sort and take top N
    sorted_langs = sorted(lang_data.items(), key=lambda x: x[1], reverse=True)[:max_langs]
    total = sum(v for _, v in sorted_langs)
    
    if total == 0:
        sorted_langs = [("None", 1)]
        total = 1
    
    # SVG dimensions
    width = 495
    bar_height = 28
    padding_top = 55
    padding_bottom = 20
    height = padding_top + (bar_height + 10) * len(sorted_langs) + padding_bottom
    
    # Start building SVG
    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <style>
      .text {{ font: 600 16px 'Segoe UI', Ubuntu, sans-serif; fill: #e6edf3; }}
      .label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: #8b949e; }}
      .pct {{ font: 600 12px 'Segoe UI', Ubuntu, sans-serif; fill: #e6edf3; }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" rx="8" fill="#0d1117"/>
  <text x="24" y="35" class="text">📊 Top Languages</text>''')
    
    y = padding_top
    bar_width = width - 140  # Space for labels
    
    for i, (lang, bytes_count) in enumerate(sorted_langs):
        pct = (bytes_count / total) * 100
        color = LANGUAGE_COLORS.get(lang, DEFAULT_COLOR)
        filled_width = max(4, (pct / 100) * bar_width)
        
        svg_parts.append(f'''
  <text x="24" y="{y + 18}" class="label">{lang}</text>
  <rect x="130" y="{y + 4}" width="{bar_width}" height="{bar_height - 8}" rx="4" fill="#21262d"/>
  <rect x="130" y="{y + 4}" width="{filled_width:.1f}" height="{bar_height - 8}" rx="4" fill="{color}"/>
  <text x="{width - 24}" y="{y + 18}" class="pct" text-anchor="end">{pct:.1f}%</text>''')
        
        y += bar_height + 10
    
    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    print(f"Fetching languages for {USERNAME}...")
    lang_data = get_all_repos_languages(USERNAME)
    
    print(f"Found {len(lang_data)} languages")
    for lang, bytes_count in sorted(lang_data.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {lang}: {bytes_count:,} bytes")
    
    print(f"\nGenerating SVG...")
    svg = create_svg(lang_data, MAX_LANGS)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(svg)
    
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
