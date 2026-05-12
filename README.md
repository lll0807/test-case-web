# Test-Case Web

一个用于 **Codex** 的技能包（Skill Pack），支持根据书面测试用例文档对网站或 Web 应用进行自动化 QA 测试，并生成带截图证据的结构化测试报告。

---

## 可用技能

| 技能 | 语言 | 描述 | 核心功能 |
|------|------|------|----------|
| [test-case-web](skills/en/test-case-web/SKILL.md) | English | Automated QA testing based on written test-case documents with screenshot evidence | Parse test docs, execute in Chrome, generate Markdown/HTML/JSON reports |
| [test-case-web-cn](skills/zh-cn/test-case-web-cn/SKILL.md) | 中文 | 根据书面测试用例文档执行网站自动化 QA 测试并生成带截图证据的报告 | 解析测试文档、Chrome 执行测试、生成 Markdown/HTML/JSON 报告 |

### 触发示例

**test-case-web / test-case-web-cn:**
- "根据这个测试用例文档测试这个网站"
- "按这个 markdown 测试 1.5 @ 按钮功能"
- "帮我 QA 这个页面，结果要带截图"
- "登录后继续跑这些网页用例，并生成测试报告"
- "根据测试文档验证这个 web app，并导出 html 报告"
- "@chrome 打开这个网站并按测试文档执行"

---

## 快速开始

### 安装

```bash
# 列出本仓库可安装的技能
npx skills add lll0807/test-case-web --list

# 安装英文版
npx skills add lll0807/test-case-web --skill test-case-web

# 安装中文版
npx skills add lll0807/test-case-web --skill test-case-web-cn

# 全局安装中文版
npx skills add lll0807/test-case-web --skill test-case-web-cn -g

# 安装到指定 Agent
npx skills add lll0807/test-case-web --skill test-case-web-cn -a claude-code

# 安装并跳过确认
npx skills add lll0807/test-case-web --skill test-case-web-cn -y
```

也可以手动复制技能到 Codex 配置目录：

```bash
# 中文版
cp -r skills/zh-cn/test-case-web-cn ~/.claude/skills/

# 英文版
cp -r skills/en/test-case-web ~/.claude/skills/
```

更多命令使用方式参考：https://github.com/vercel-labs/skills/blob/main/README.md

---

## 功能简介

本技能专为**自动化网页测试**场景设计，能够：

- 读取并解析用户提供的测试用例文档（Markdown、编号列表、QA 检查表等）
- 在 **Chrome** 浏览器中自动打开目标网站并执行测试
- 逐条执行测试用例，捕获截图作为证据
- 生成三种格式的测试报告：
  - `测试结果.md` / `Test Results.md` — 人工可读的 Markdown 报告
  - `测试结果.html` / `Test Results.html` — 带截图画廊的可视化网页报告
  - `results.json` — 机器可读的标准化结果

---

## 使用方法

### 1. 启用浏览器插件

告诉 Claude / Codex 你要使用内置浏览器功能，他会帮你安装相关插件。

### 2. 准备测试用例

把测试用例整理成 Markdown 表格，必须包含以下 5 列：

- `用例编号` / `Case ID`
- `测试标题` / `Title`
- `前置条件` / `Preconditions`
- `操作步骤` / `Steps`
- `预期结果` / `Expected Result`

示例：

```md
| 用例编号 | 测试标题 | 前置条件 | 操作步骤 | 预期结果 |
|---------|---------|---------|---------|---------|
| TC-01 | 检查按钮显示 | 打开首页 | 查看页面右上角 | 显示登录按钮 |
```

### 3. 发送测试指令

直接向 Claude / Codex 发送下面格式的请求：

```
请你调用 test-case-web 技能，根据{你的测试用例文档路径}，测试网站 https://your-site.com/。
```

#### 限定章节范围（推荐）

如果测试文档很大，可以只测试特定章节：

```
请你调用 test-case-web 技能，根据{你的测试用例文档路径}中的 1.5 章节用例。测试网站：https://your-site.com/
```

### 4. 处理登录

如果 Claude / Codex 提示需要登录：

1. 他会跳转出登录页面
2. 在登录页面中完成登录
3. 登录完成后，回复「我已经登录完成，请继续执行测试」，Claude / Codex 会继续执行

### 5. 等待执行结果

执行完成后，检查是否输出了以下内容：

- `results.json`
- `测试结果.md` / `Test Results.md`
- `测试结果.html` / `Test Results.html`
- `screenshots/`

### 6. 查看结果目录

标准目录结构：

```
qa-results/
  时间戳-主题/
    results.json
    测试结果.md
    测试结果.html
    screenshots/
```

---

## 输出产物

每次测试运行会创建一个带时间戳的目录：

```
qa-results/2026-05-11_14-30-00-at-button/
├── 测试结果.md        # Markdown 报告
├── 测试结果.html       # 可视化网页报告
├── results.json       # 结构化数据
└── screenshots/       # 截图证据
    ├── TC-V-1.5-01-01.png
    └── TC-V-1.5-01-02.png
```

### 截图命名规范

- `TC-V-<章节>-<用例序号>-<截图序号>.png`
- 示例：`TC-V-1.5-01-01.png`

---

## 测试用例状态

| 状态 | 含义 |
|------|------|
| `passed` | 实际行为与预期结果一致 |
| `failed` | 实际行为与预期结果不符 |
| `blocked` | 因阻塞（如缺陷、页面无法访问）无法完成 |
| `not_run` | 用户缩小范围或主动停止，未执行 |

---

## 工作流概览

```
1. 读取测试用例文档
        ↓
2. 在 Chrome 中打开目标网站
        ↓
3. 检查登录状态（如需登录 → 等待用户）
        ↓
4. 逐个执行测试用例
   ├─ 重述测试意图
   ├─ 将页面带入所需状态
   ├─ 执行最少必要操作
   ├─ 对比实际 vs 预期
   └─ 捕获截图证据
        ↓
5. 生成结构化结果 (results.json)
        ↓
6. 编写 Markdown 报告 (测试结果.md)
        ↓
7. 生成 HTML 可视化报告 (测试结果.html)
```

---

## 仓库结构

```
test-case-web/
├── README.md                     # 本文件
├── skills/
│   ├── en/
│   │   └── test-case-web/
│   │       ├── SKILL.md          # 英文技能定义
│   │       └── scripts/
│   │           └── generate_html_report.py
│   └── zh-cn/
│       └── test-case-web-cn/
│           ├── SKILL.md          # 中文技能定义
│           └── scripts/
│               └── generate_html_report.py
```

---

## 依赖要求

- **Codex** 环境
- **Chrome 浏览器**（用于实际的网页测试和截图）
- **Python 3.12+**

---

## 许可证

MIT
