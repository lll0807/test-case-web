from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


STATUS_LABELS = {
    "passed": "通过",
    "failed": "失败",
    "blocked": "阻塞",
    "not_run": "未执行",
}


STATUS_COLORS = {
    "passed": "#1f7a3d",
    "failed": "#b42318",
    "blocked": "#b54708",
    "not_run": "#475467",
}


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def render_case(case: dict) -> str:
    status = case.get("status", "not_run")
    label = STATUS_LABELS.get(status, status)
    color = STATUS_COLORS.get(status, "#475467")

    screenshots = case.get("screenshots") or []
    screenshot_html = []
    for shot in screenshots:
        shot_esc = esc(shot)
        screenshot_html.append(
            f"""
            <figure class="shot">
              <a href="{shot_esc}" target="_blank" rel="noopener noreferrer">
                <img src="{shot_esc}" alt="{esc(case.get('id', '用例'))} 截图" />
              </a>
              <figcaption>{shot_esc}</figcaption>
            </figure>
            """
        )

    return f"""
    <section class="case">
      <div class="case-header">
        <div>
          <h3>{esc(case.get("id", ""))} {esc(case.get("title", ""))}</h3>
        </div>
        <span class="badge" style="background:{color};">{esc(label)}</span>
      </div>
      <div class="meta-grid">
        <div><strong>前置条件</strong><p>{esc(case.get("preconditions", ""))}</p></div>
        <div><strong>操作步骤</strong><p>{esc(case.get("steps", ""))}</p></div>
        <div><strong>预期结果</strong><p>{esc(case.get("expected", ""))}</p></div>
        <div><strong>实际结果</strong><p>{esc(case.get("actual", ""))}</p></div>
      </div>
      <div class="notes">
        <strong>备注</strong>
        <p>{esc(case.get("notes", ""))}</p>
      </div>
      <div class="shots-grid">
        {''.join(screenshot_html) or '<p class="empty">未记录截图。</p>'}
      </div>
    </section>
    """


def render_html(data: dict) -> str:
    summary = data.get("summary", {})
    cases = data.get("cases", [])
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>测试结果</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8fafc;
      --panel: #ffffff;
      --text: #101828;
      --muted: #475467;
      --border: #d0d5dd;
      --shadow: 0 10px 30px rgba(16, 24, 40, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 32px;
      background: linear-gradient(180deg, #f8fafc 0%, #eef4ff 100%);
      color: var(--text);
      font: 14px/1.6 "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    .wrap {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    .hero, .case {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
    }}
    .hero {{
      padding: 28px;
      margin-bottom: 24px;
    }}
    h1, h2, h3, p {{
      margin: 0;
    }}
    h1 {{
      font-size: 30px;
      line-height: 1.2;
      margin-bottom: 10px;
    }}
    .intro {{
      color: var(--muted);
      margin-bottom: 18px;
    }}
    .run-meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .meta-card, .summary-card {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px 16px;
      background: #fcfcfd;
    }}
    .meta-card strong, .summary-card strong {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 22px 0 0;
    }}
    .summary-card span {{
      font-size: 28px;
      font-weight: 700;
    }}
    .section-title {{
      margin: 28px 0 16px;
      font-size: 20px;
    }}
    .case {{
      padding: 22px;
      margin-bottom: 18px;
    }}
    .case-header {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
      margin-bottom: 16px;
    }}
    .case-header h3 {{
      font-size: 18px;
      line-height: 1.35;
    }}
    .badge {{
      color: white;
      font-weight: 700;
      padding: 6px 10px;
      border-radius: 999px;
      white-space: nowrap;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }}
    .meta-grid div, .notes {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px 16px;
      background: #fcfcfd;
    }}
    .meta-grid strong, .notes strong {{
      display: block;
      margin-bottom: 6px;
    }}
    .shots-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin-top: 16px;
    }}
    .shot {{
      margin: 0;
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      background: #fff;
    }}
    .shot a {{
      display: block;
      text-decoration: none;
    }}
    .shot img {{
      display: block;
      width: 100%;
      height: auto;
      background: #f2f4f7;
    }}
    .shot figcaption {{
      padding: 10px 12px;
      color: var(--muted);
      border-top: 1px solid var(--border);
      word-break: break-all;
      font-size: 12px;
    }}
    .empty {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>测试结果</h1>
      <p class="intro">基于测试用例文档执行的网页测试报告，包含逐条结果与截图证据。</p>
      <div class="run-meta">
        <div class="meta-card"><strong>任务名称</strong>{esc(data.get("run_name", ""))}</div>
        <div class="meta-card"><strong>目标地址</strong>{esc(data.get("target_url", ""))}</div>
        <div class="meta-card"><strong>测试文档</strong>{esc(data.get("source_document", ""))}</div>
        <div class="meta-card"><strong>测试章节</strong>{esc(data.get("section", ""))}</div>
        <div class="meta-card"><strong>生成时间</strong>{esc(data.get("generated_at", ""))}</div>
      </div>
      <div class="summary-grid">
        <div class="summary-card"><strong>通过</strong><span>{summary.get("passed", 0)}</span></div>
        <div class="summary-card"><strong>失败</strong><span>{summary.get("failed", 0)}</span></div>
        <div class="summary-card"><strong>阻塞</strong><span>{summary.get("blocked", 0)}</span></div>
        <div class="summary-card"><strong>未执行</strong><span>{summary.get("not_run", 0)}</span></div>
      </div>
    </section>
    <h2 class="section-title">逐条结果</h2>
    {''.join(render_case(case) for case in cases)}
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML QA report from results.json")
    parser.add_argument("results_json", help="Path to results.json")
    parser.add_argument(
        "--output",
        help="Output HTML path. Defaults to 测试结果.html next to results.json",
    )
    args = parser.parse_args()

    results_path = Path(args.results_json).resolve()
    output_path = Path(args.output).resolve() if args.output else results_path.with_name("测试结果.html")

    data = json.loads(results_path.read_text(encoding="utf-8"))
    output_path.write_text(render_html(data), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
