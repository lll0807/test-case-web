---
name: test-case-web-cn
description: Execute website test cases from a provided test-case document and produce evidence-backed QA reports. Use this whenever the user asks to test, verify, validate, QA, regress, or check a website/web app based on a test-case document, markdown test plan, QA checklist, or numbered cases. This skill is especially important when the user mentions a specific section like "1.5", "登录", "上传", "@ 按钮", "按文档测试", or wants screenshots and a final report.
---

# Test-Case Web

## 使用场景

Use this skill when the user wants you to test a website against a written test-case document and preserve evidence.

This workflow is designed for authenticated, stateful browser testing. Always prefer `@chrome` and the Chrome skill unless the user explicitly asks for a different browser surface. Many real QA flows depend on the user's existing session, SSO, enterprise login, or multi-tab behavior.

Do not default to the in-app browser for this workflow. If Chrome is available, use it.

## 不要使用

Do not use this skill for:
- Code review of specific changes (use code-reviewer instead)
- Inspecting a single commit in detail
- Git operations other than log extraction (branching, merging, etc.)
- Non-git-related report generation

## 使用说明

Follow these steps in order.

### 1. Read the test-case source

Start from the document the user provided. If they named a subsection such as `1.5` or a heading such as `@ 按钮功能`, scope the run to that section first.

Extract, for each test case:

- case id
- title
- preconditions
- steps
- expected result

If the document encoding is messy, recover what you can from nearby headings and table structure instead of stopping immediately.

If the user did not name a section and the document is large, identify the major sections and test only the requested area. If the request is ambiguous, ask one concise clarification question.

### 2. Open the target site in Chrome

Use `@chrome` / Chrome-backed browser automation, not the in-app browser, unless the user explicitly asks otherwise.

Treat this as a hard default:

- always open the target site in the user's real Chrome environment
- keep the working tab available for the user to see and interact with
- do not hide the critical login page in a background-only flow when the user needs to act on it

Open the requested site and inspect whether the flow is already authenticated.

If login is required:

- tell the user clearly that login is needed
- tell the user that the page has been opened in Chrome for them
- keep the browser on the right page
- keep the tab open as a visible handoff for the user
- wait for the user to finish logging in
- after the user confirms they are logged in, resume from the same Chrome session

Do not attempt to bypass login. Do not ask the user to repeat work you can preserve through the existing Chrome tab.

When login or manual action is needed, treat the Chrome tab as a handoff artifact rather than a hidden implementation detail.

### 3. Execute test cases one by one

For each test case:

1. Restate the test intent to yourself from the document.
2. Bring the page into the needed state.
3. Execute only the minimum actions required.
4. Compare actual behavior against the expected result.
5. Capture evidence before moving on.

For every executed test case, capture at least:

- one screenshot that supports the final verdict

Capture additional screenshots when:

- the case fails
- the state changes across steps
- the bug is easier to understand with before/after evidence

Use screenshot filenames that preserve execution order and case traceability:

- `TC-V-1.5-01-01.png`
- `TC-V-1.5-01-02.png`

If a case cannot be completed because of a blocker, still capture a screenshot and mark the case as `blocked`.

### 4. Record structured results as you go

Create `results.json` incrementally during the run. Use this schema:

```json
{
  "run_name": "at-button",
  "target_url": "https://example.com",
  "source_document": "/absolute/path/to/cases.md",
  "section": "1.5 @ 按钮功能",
  "generated_at": "2026-05-11T14:30:00+08:00",
  "cases": [
    {
      "id": "TC-V-1.5-01",
      "title": "全能参考模式显示 @ 按钮",
      "preconditions": "选中全能参考模式",
      "steps": "查看网络搜索按钮右侧",
      "expected": "显示 @ 按钮",
      "actual": "在全能参考模式下，网络搜索按钮右侧显示引用参考按钮。",
      "status": "passed",
      "notes": "",
      "screenshots": [
        "screenshots/TC-V-1.5-01-01.png"
      ]
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "blocked": 0,
    "not_run": 0
  }
}
```

Allowed case status values:

- `passed`
- `failed`
- `blocked`
- `not_run`

Use `not_run` only when the user explicitly narrows scope after extraction or stops the run.

### 5. Write `测试结果.md`

After execution, write a concise but complete Markdown report.

Use this structure:

```md
# 测试结果

## 测试范围
- 目标网站：
- 测试文档：
- 测试章节：
- 测试时间：

## 汇总
- Passed:
- Failed:
- Blocked:
- Not Run:

## 逐条结果

### TC-XXX
- 标题：
- 预期：
- 实际：
- 结果：Passed / Failed / Blocked / Not Run
- 证据：
  - [截图1](./screenshots/TC-XXX-01.png)
```

Requirements:

- every executed case must appear
- every case must link to its screenshots
- failed cases should explain the mismatch clearly
- blocked cases should explain the blocker clearly

### 6. Generate `测试结果.html`

After `results.json` is complete, use the bundled script:

`scripts/generate_html_report.py`

The script converts `results.json` into `测试结果.html` with:

- summary cards
- a per-case result table
- per-case screenshot gallery
- color-coded status badges

Do not hand-write the HTML unless the script is missing or broken. If the script fails, fix the input or the script and rerun it.

## Practical testing guidance

### Login handling

When login interrupts the run:

- preserve the current Chrome tab
- leave the relevant Chrome tab open for the user instead of closing or omitting it
- tell the user exactly what you need: for example, "请先在 Chrome 中完成登录，我登录后继续测试。"
- make it explicit that the page is open in Chrome and waiting for them
- once they confirm, rediscover or reclaim the active site tab and continue

If the user says they cannot see the page, re-open or reclaim the correct Chrome tab and keep it as the active handoff tab before asking them to continue.

### Evidence quality

Prefer screenshots that make the verdict obvious:

- the relevant control is visible
- the active mode or selected filter is visible
- the expected or unexpected state is visible

Avoid screenshots that require the reader to guess what was being tested.

### Scope control

If the document contains many sections, do not silently test everything. Respect the user's requested section first.

### Reporting honesty

Do not mark a test as passed unless the observed behavior matches the expected result.

If the browser automation path becomes unstable, record a blocker with evidence instead of inventing certainty.

## Suggested trigger examples

This skill should trigger for requests like:

- "根据这个测试用例文档测试这个网站"
- "按这个 markdown 测试 1.5 @ 按钮功能"
- "帮我 QA 这个页面，结果要带截图"
- "登录后继续跑这些网页用例，并生成测试报告"
- "根据测试文档验证这个 web app，并导出 html 报告"
- "@chrome 打开这个网站并按测试文档执行"

## Bundled files

- `scripts/generate_html_report.py`: convert `results.json` to `测试结果.html`
