<div align="center">

# 🐙 GitHub Dashboard

**通过 GitHub API 生成个人数据可视化 SVG 图表，打造动态 GitHub Profile 数据名片**

[English](#english) | 中文

[![Python](https://img.shields.io/badge/Python-3.11+-3572A5?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Auto_Update-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

</div>

---

## ✨ 功能特性

| 图表 | 说明 |
|:---:|:---|
| 🔥 贡献热力图 | 类似 GitHub 的年度贡献日历，支持多年切换 |
| 🥧 语言分布图 | 环形图展示编程语言使用占比，GitHub 官方语言配色 |
| 📈 活跃度趋势图 | 折线图展示每周贡献趋势，自动标注峰值 |
| 📊 仓库排行榜 | 水平条形图展示 Star 最多的仓库 |
| 🏷️ 个人信息卡片 | 汇总头像、Bio、关键统计数字、连续贡献天数 |

**其他特性**：深色/浅色主题 · GitHub Actions 每日自动更新 · 本地缓存减少 API 调用 · Web 预览界面

## 📸 效果预览

```
┌─────────────────────────────────────────────────────────────┐
│  👤 Profile Card          │  🔥 Contribution Heatmap        │
│  Avatar + Name + Stats    │  ■■■□□■■□□■■■■□□■■□□■■■■□□■■  │
├───────────────────────────┼─────────────────────────────────┤
│  🥧 Language Distribution │  📈 Activity Trend              │
│  ████████ Python 50%      │  ╱╲    ╱╲                       │
│  █████ JavaScript 30%     │ ╱  ╲╱╱  ╲╱╲                    │
│  ███ Other 20%            │╱          ╲                     │
├───────────────────────────┴─────────────────────────────────┤
│  📊 Top Repositories                                        │
│  awesome-project  ████████████████████████████ ★ 150        │
│  web-app          ████████████████ ★ 80                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- GitHub Personal Access Token

### 安装

```bash
git clone https://github.com/HaibaraAi-deep/github-dashboard.git
cd github-dashboard
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_USERNAME=your_github_username
```

> **Token 权限**：`public_repo` + `read:user`

### 生成图表

```bash
# 生成全部图表
python -m src.main --username your_username all

# 仅生成热力图
python -m src.main --username your_username heatmap

# 仅生成语言分布图
python -m src.main --username your_username languages
```

## 🖥️ Web 预览

```bash
python app.py
```

访问 `http://localhost:5000`，在浏览器中输入用户名即可实时预览图表。

## ⚙️ 命令行参数

| 参数 | 缩写 | 默认值 | 说明 |
|------|:---:|:------:|------|
| `--username` | `-u` | 环境变量 | GitHub 用户名 |
| `--token` | `-t` | 环境变量 | GitHub Personal Access Token |
| `--output` | `-o` | `./output` | 输出目录 |
| `--year` | `-y` | 当前年份 | 贡献数据年份 |
| `--top-n` | `-n` | `10` | 排行榜显示数量 |
| `--no-forks` | | `False` | 排除 Fork 仓库 |
| `--theme` | | `dark` | 主题 (`dark` / `light`) |
| `--cache-ttl` | | `3600` | 缓存有效期（秒） |
| `--dry-run` | | `False` | 仅获取数据，不生成图表 |
| `--push` | | `False` | 自动提交推送生成的文件 |
| `--verbose` | `-v` | `False` | 详细日志输出 |

## 📌 嵌入 Profile README

```markdown
# Hi, I'm 👋

<img align="right" src="./output/profile-card.svg" width="400">

## GitHub Activity

<img src="./output/heatmap.svg" alt="Contribution Heatmap">

## Tech Stack

<img src="./output/languages.svg" alt="Language Distribution">
```

## ⏰ GitHub Actions 自动更新

项目已包含 GitHub Actions 工作流配置，每日 UTC 00:00 自动执行：

1. 拉取最新数据
2. 生成 SVG 图表
3. 自动提交推送到仓库

也可在 Actions 页面手动触发。

## 📁 项目结构

```
github-dashboard/
├── src/
│   ├── main.py                  # CLI 入口
│   ├── config.py                # 配置管理
│   ├── collectors/              # 数据采集
│   │   ├── base.py              # 采集器基类
│   │   ├── rest_collector.py    # REST API
│   │   └── graphql_collector.py # GraphQL API
│   ├── processors/              # 数据处理
│   │   ├── user_processor.py
│   │   ├── repo_processor.py
│   │   ├── language_processor.py
│   │   └── contribution_processor.py
│   ├── renderers/               # 可视化渲染
│   │   ├── base_renderer.py
│   │   ├── heatmap.py
│   │   ├── language_chart.py
│   │   ├── activity_chart.py
│   │   ├── repo_ranking.py
│   │   └── profile_card.py
│   └── utils/                   # 工具模块
│       ├── cache.py
│       ├── rate_limiter.py
│       └── git_helper.py
├── templates/                   # Web 预览模板
├── output/                      # 生成的 SVG
├── tests/                       # 测试
├── app.py                       # Web 预览服务
└── .github/workflows/           # GitHub Actions
```

## 🧪 运行测试

```bash
python -m pytest tests/ -v
```

## 🛠️ 技术栈

| 用途 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| HTTP 请求 | requests |
| GraphQL | gql |
| SVG 生成 | svgwrite |
| 图表渲染 | matplotlib |
| 数据处理 | pandas |
| CLI 框架 | click |
| Web 预览 | Flask |
| 配置管理 | python-dotenv |
| 自动化 | GitHub Actions |

## 👥 贡献者

<a href="https://github.com/HaibaraAi-deep/github-dashboard/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HaibaraAi-deep/github-dashboard" />
</a>

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<a id="english"></a>

<div align="center">

# 🐙 GitHub Dashboard

**Generate personal data visualization SVG charts via GitHub API, create a dynamic GitHub Profile data card**

中文 | [English](#english)

[![Python](https://img.shields.io/badge/Python-3.11+-3572A5?style=flat-square&logo=github-actions&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Auto_Update-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

</div>

---

## ✨ Features

| Chart | Description |
|:---:|:---|
| 🔥 Contribution Heatmap | GitHub-style annual contribution calendar with multi-year support |
| 🥧 Language Distribution | Donut chart showing programming language usage with GitHub official colors |
| 📈 Activity Trend | Line chart showing weekly contribution trends with peak annotations |
| 📊 Repository Ranking | Horizontal bar chart showing top-starred repositories |
| 🏷️ Profile Card | Summary card with avatar, bio, key stats, and contribution streaks |

**Additional Features**: Dark/Light themes · GitHub Actions daily auto-update · Local caching to reduce API calls · Web preview interface

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token

### Installation

```bash
git clone https://github.com/HaibaraAi-deep/github-dashboard.git
cd github-dashboard
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Edit the `.env` file:

```
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_USERNAME=your_github_username
```

> **Token Permissions**: `public_repo` + `read:user`

### Generate Charts

```bash
# Generate all charts
python -m src.main --username your_username all

# Generate heatmap only
python -m src.main --username your_username heatmap

# Generate language distribution only
python -m src.main --username your_username languages
```

## 🖥️ Web Preview

```bash
python app.py
```

Visit `http://localhost:5000` and enter a username to preview charts in real-time.

## ⚙️ CLI Options

| Option | Short | Default | Description |
|--------|:---:|:-------:|-------------|
| `--username` | `-u` | env var | GitHub username |
| `--token` | `-t` | env var | GitHub Personal Access Token |
| `--output` | `-o` | `./output` | Output directory |
| `--year` | `-y` | current year | Year for contribution data |
| `--top-n` | `-n` | `10` | Number of items in ranking |
| `--no-forks` | | `False` | Exclude forked repositories |
| `--theme` | | `dark` | Theme (`dark` / `light`) |
| `--cache-ttl` | | `3600` | Cache TTL in seconds |
| `--dry-run` | | `False` | Fetch data only, skip chart generation |
| `--push` | | `False` | Auto commit and push generated files |
| `--verbose` | `-v` | `False` | Verbose logging |

## 📌 Embed in Profile README

```markdown
# Hi, I'm 👋

<img align="right" src="./output/profile-card.svg" width="400">

## GitHub Activity

<img src="./output/heatmap.svg" alt="Contribution Heatmap">

## Tech Stack

<img src="./output/languages.svg" alt="Language Distribution">
```

## ⏰ GitHub Actions Auto-Update

The project includes a GitHub Actions workflow that runs daily at UTC 00:00:

1. Fetch latest data
2. Generate SVG charts
3. Auto commit and push to repository

Can also be triggered manually from the Actions page.

## 📁 Project Structure

```
github-dashboard/
├── src/
│   ├── main.py                  # CLI entry point
│   ├── config.py                # Configuration management
│   ├── collectors/              # Data collection
│   │   ├── base.py              # Base collector
│   │   ├── rest_collector.py    # REST API
│   │   └── graphql_collector.py # GraphQL API
│   ├── processors/              # Data processing
│   │   ├── user_processor.py
│   │   ├── repo_processor.py
│   │   ├── language_processor.py
│   │   └── contribution_processor.py
│   ├── renderers/               # Visualization rendering
│   │   ├── base_renderer.py
│   │   ├── heatmap.py
│   │   ├── language_chart.py
│   │   ├── activity_chart.py
│   │   ├── repo_ranking.py
│   │   └── profile_card.py
│   └── utils/                   # Utility modules
│       ├── cache.py
│       ├── rate_limiter.py
│       └── git_helper.py
├── templates/                   # Web preview templates
├── output/                      # Generated SVGs
├── tests/                       # Tests
├── app.py                       # Web preview server
└── .github/workflows/           # GitHub Actions
```

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 🛠️ Tech Stack

| Purpose | Technology |
|---------|-----------|
| Language | Python 3.11+ |
| HTTP Requests | requests |
| GraphQL | gql |
| SVG Generation | svgwrite |
| Chart Rendering | matplotlib |
| Data Processing | pandas |
| CLI Framework | click |
| Web Preview | Flask |
| Configuration | python-dotenv |
| Automation | GitHub Actions |

## 👥 Contributors

<a href="https://github.com/HaibaraAi-deep/github-dashboard/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HaibaraAi-deep/github-dashboard" />
</a>

## 📄 License

This project is licensed under the [MIT License](LICENSE).
