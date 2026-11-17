#!/usr/bin/env python3
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
md_file = ROOT / "docs" / "BDS_PROJECT_COMPLETE_GUIDE.md"
html_file = ROOT / "docs" / "BDS_PROJECT_COMPLETE_GUIDE.html"

with open(md_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
out.append("<!DOCTYPE html>")
out.append("<html lang='en'>")
out.append("<head>")
out.append("<meta charset='UTF-8'>")
out.append("<title>TraceHunt - BDS Project & Viva Defense Guide</title>")
out.append("""<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
  body {
    font-family: 'Inter', -apple-system, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 30px;
    background: #ffffff;
  }
  h1 { color: #0f172a; border-bottom: 3px solid #3b82f6; padding-bottom: 12px; font-size: 26px; }
  h2 { color: #1e3a8a; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 20px; }
  h3 { color: #2563eb; margin-top: 24px; font-size: 16px; }
  h4 { color: #475569; margin-top: 18px; font-size: 14px; }
  table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 13px; }
  th, td { border: 1px solid #cbd5e1; padding: 10px 14px; text-align: left; }
  th { background: #f1f5f9; font-weight: 600; color: #0f172a; }
  tr:nth-child(even) { background: #f8fafc; }
  pre {
    background: #0f172a;
    color: #e2e8f0;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
  }
  code {
    font-family: 'JetBrains Mono', monospace;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }
  pre code { background: transparent; color: inherit; padding: 0; }
  blockquote {
    border-left: 4px solid #3b82f6;
    background: #eff6ff;
    padding: 12px 18px;
    margin: 16px 0;
    color: #1e40af;
    border-radius: 0 6px 6px 0;
  }
  hr { border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }
  .badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    background: #dbeafe;
    color: #1e40af;
    font-size: 11px;
    font-weight: 600;
  }
  @media print {
    body { max-width: 100%; margin: 20px; padding: 0; }
    pre { white-space: pre-wrap; font-size: 11px; }
  }
</style>""")
out.append("</head><body>")

in_code = False
code_buf = []

for line in lines:
    raw = line.rstrip()
    if raw.startswith("```"):
        if in_code:
            out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
            code_buf = []
            in_code = False
        else:
            in_code = True
        continue
    if in_code:
        code_buf.append(raw)
        continue
    if raw.startswith("# "):
        out.append(f"<h1>{html.escape(raw[2:])}</h1>")
    elif raw.startswith("## "):
        out.append(f"<h2>{html.escape(raw[3:])}</h2>")
    elif raw.startswith("### "):
        out.append(f"<h3>{html.escape(raw[4:])}</h3>")
    elif raw.startswith("#### "):
        out.append(f"<h4>{html.escape(raw[5:])}</h4>")
    elif raw.startswith("> "):
        out.append(f"<blockquote>{html.escape(raw[2:])}</blockquote>")
    elif raw.startswith("---"):
        out.append("<hr/>")
    elif raw.startswith("* ") or raw.startswith("- "):
        out.append(f"<li>{html.escape(raw[2:])}</li>")
    elif raw.strip():
        out.append(f"<p>{html.escape(raw)}</p>")

out.append("</body></html>")

with open(html_file, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Created:", html_file)
