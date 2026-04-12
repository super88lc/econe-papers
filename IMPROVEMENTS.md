# Econe Papers 每日精选 v2.0 改进说明

## 改进内容

### 1. 过滤金融领域论文 ✅

**改进前：**
- 包含所有经济学和金融学论文（q-fin.* 分类）
- 没有二次过滤机制

**改进后：**
- 移除了所有量化金融分类（q-fin.EC, q-fin.GN, q-fin.MF, q-fin.PM, q-fin.RM, q-fin.ST, q-fin.TR）
- 保留了纯经济学分类：econ.GN, econ.EM, econ.TH, econ.CO, econ.HO, econ.IV, econ.ME, econ.MA, econ.PE, econ.WR
- 添加了金融关键词二次过滤（30+个关键词）
- 关键词覆盖：asset pricing, portfolio, stock market, trading strategy, 资产定价, 投资组合等

**代码位置：**
- `is_finance_paper()` 函数 - 双重检查机制
- `FINANCE_KEYWORDS` 列表 - 金融关键词库

---

### 2. 提供中文摘要翻译 ✅

**改进前：**
- 只显示英文摘要
- chineseAbstract 只是截取英文前200字

**改进后：**
- AI 完整翻译论文摘要（200-400字）
- 保留学术术语准确性
- Email 推送包含完整中文摘要
- 飞书推送包含中文摘要预览（120字）
- 新增中文标题翻译

**代码位置：**
- `analyze_and_translate()` 函数 - AI 翻译
- `send_email()` 函数 - Email 模板已更新
- `send_to_feishu()` 函数 - 飞书消息已更新

---

### 3. 改进评分系统 ✅

**改进前：**
- 简单的关键词匹配评分
- 大部分论文评分集中在 5.0-6.0 之间
- 评分维度：overall, novelty, quality, readability

**改进后：**
- **5 维度评分体系**（每项 1-5 分）：
  - `novelty` (创新性): 研究问题/方法是否有新意
  - `methodology` (方法论): 研究方法是否严谨先进
  - `empirical` (实证质量): 数据/实验/论证是否扎实
  - `impact` (影响力): 对学界或政策可能的影响
  - `readability` (可读性): 写作质量和易懂程度
- **综合评分** (overall): 1-10 分，加权计算

- **AI 评分 + 备用评分**：
  - 优先使用 MiniMax AI 进行深度分析评分
  - AI 失败时使用改进的备用算法（加入随机偏移确保区分度）
  - 每个论文 ID 作为随机种子，确保评分可重复

- **区分度保证**：
  - AI 提示词明确要求"确保评分有区分度"
  - 备用算法加入 ±0.5 的随机偏移
  - 预期结果：大部分论文评分在 4.0-9.0 之间分散

**代码位置：**
- `analyze_and_translate()` - AI 评分
- `calculate_fallback_scores()` - 备用评分算法
- `scoreReasoning` 字段 - 评分理由说明

---

## 新数据字段

每篇论文现在包含以下字段：

```json
{
  "id": "论文ID",
  "title": "英文标题",
  "chineseTitle": "中文标题",
  "authors": ["作者列表"],
  "abstract": "英文摘要",
  "chineseAbstract": "中文摘要（200-400字）",
  "categories": ["分类"],
  "published": "发布日期",
  "pdfUrl": "PDF链接",
  "researchField": "研究领域",
  "keywords": ["关键词列表"],
  "scores": {
    "overall": 7.5,
    "novelty": 4.0,
    "methodology": 4.0,
    "empirical": 4.0,
    "impact": 3.5,
    "readability": 4.0
  },
  "scoreReasoning": "评分理由",
  "summary": "一句话核心贡献"
}
```

---

## 使用方法

### 手动运行

```bash
cd ~/.openclaw/workspace/econe-papers/backend
source .venv/bin/activate
python3 daily_update_v2.py
```

### 定时任务（Cron）

```bash
# 编辑 crontab
crontab -e

# 添加每天上午9点运行
0 9 * * * /Users/apple/.openclaw/workspace/econe-papers/run_daily_update.sh >> /Users/apple/.openclaw/workspace/econe-papers/cron.log 2>&1
```

### 更新后的 Shell 脚本

`run_daily_update.sh` 已更新为使用 v2 版本：
- 加载 ~/.zshrc 环境变量
- 运行 daily_update_v2.py
- 自动推送到 GitHub（触发 Vercel 部署）

---

## 依赖要求

```bash
# 确保已安装
pip install requests beautifulsoup4

# 可选（用于更好的 XML 解析）
pip install lxml
```

---

## 环境变量配置

确保 `~/.zshrc` 中有：

```bash
export MINIMAX_API_KEY="your-api-key-here"
```

脚本会自动从环境变量或 ~/.zshrc 中读取 API Key。

---

## 邮件和飞书推送预览

### Email 模板改进：
- 显示中文标题 + 英文标题
- 完整中文摘要（200-400字）
- 5维度评分详情
- 评分理由说明
- 关键词标签
- 一句话核心贡献

### 飞书消息改进：
- 显示中文标题
- 中文摘要预览（120字）
- 5维度评分
- 一键查看原文链接

---

## 版本历史

- **v1.0**: 基础版本（抓取 + 简单评分 + Email推送）
- **v2.0**: 改进版本（过滤金融 + 中文翻译 + 多维度评分 + 飞书推送）

---

_Last updated: 2026-04-12_
