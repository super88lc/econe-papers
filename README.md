# ArXiv 论文抓取 + AI 分析

每日自动抓取 arXiv.org 经济学论文，AI 筛选分类，展示精选论文。

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/econe-papers.git
cd econe-papers
```

### 2. 安装后端依赖
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4
```

### 3. 配置环境变量
复制 `.env.example` 为 `.env` 并填入你的 API Key：
```bash
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 4. 运行抓取脚本
```bash
source .venv/bin/activate
python3 scrape_arxiv.py --max 50 --analyze 10
```

### 5. 前端开发
```bash
cd web
npm install
npm run dev
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MINIMAX_API_KEY` | ✅ | MiniMax API Key（用于 AI 分析） |

## 部署

### Vercel 部署
1. 在 Vercel 创建新项目，导入 GitHub 仓库
2. 在 Vercel 环境变量中添加 `MINIMAX_API_KEY`
3. 部署！

### GitHub Actions 定时抓取
在 GitHub 仓库设置 Secrets：
- `MINIMAX_API_KEY`

## 项目结构

```
econe-papers/
├── SPEC.md              # 项目规格文档
├── backend/
│   ├── scrape_arxiv.py  # 抓取脚本
│   ├── papers.json      # 论文数据
│   └── .venv/           # Python 虚拟环境
└── web/
    ├── src/
    │   ├── app/         # Next.js 页面
    │   ├── components/ # React 组件
    │   ├── lib/        # 数据和工具
    │   └── types/      # TypeScript 类型
    └── package.json
```
