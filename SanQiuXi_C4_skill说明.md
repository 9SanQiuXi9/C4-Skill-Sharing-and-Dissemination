# C4 Skill 说明：Submission Privacy Scanner（提交隐私扫描器）

## 解决什么问题

提交作业、论文、挑战材料之前，你有没有遇到过这些情况：

- 论文里忘了把真实姓名换成笔名
- AI 日志里残留了 API Key 没删
- 文件里不小心贴了个人 GitHub 链接或手机号
- LaTeX 编译日志暴露了本地用户名路径
- 文档里还有 `TODO: 填写姓名` 没处理

这些都是真实的隐私泄露风险。手动一个个文件翻查既慢又容易漏。

**Submission Privacy Scanner** 就是为了解决这个问题：自动扫描文件中的隐私敏感信息，生成一份按风险等级排序的检查报告，让你在提交前一次性解决所有隐患。

## 使用场景

| 场景 | 说明 |
|------|------|
| 论文提交前 | 扫描 .tex/.md 文件，检查作者信息、邮箱、路径泄露 |
| 挑战文件打包前 | 扫描整个提交目录，确保 AI 日志、代码里没有密钥或个人链接 |
| 日常文档脱敏 | 分享文档给别人前，快速检查有没有不该出现的内容 |
| 批量检查 | 助教/老师扫描全班提交物，快速定位需要退回修改的文件 |

## 输入输出

- **输入**：一个文件路径或目录路径
- **输出**：Markdown 格式的隐私风险报告（含汇总统计 + 逐条详情 + 处理建议）

## 检测范围

| 类别 | 检测内容 | 风险等级 |
|------|----------|----------|
| 联系方式 | 邮箱、手机号、固定电话 | 高/中 |
| 身份信息 | 身份证号、学号/工号、LaTeX作者字段 | 高/中 |
| 网络痕迹 | URL、GitHub个人链接、社交媒体账号 | 高/中 |
| 密钥令牌 | API Key、Token、密码、私钥 | 高 |
| 路径泄露 | Windows/Unix 含用户名的本地路径 | 中 |
| 占位符残留 | TODO/FIXME、模板占位符 | 低/中 |

## 核心特性

### 1. 脚本 + AI 混合检测

- Python 脚本负责正则扫描，保证不遗漏（确定性检测）
- AI 负责上下文判断，降低误报（如区分学术引用 URL 和个人链接）

### 2. 白名单机制

用户可以声明"这些不算泄露"，扫描时自动跳过：

- **精确匹配**：指定具体的邮箱、链接
- **模式匹配**：用正则匹配一类内容（如所有 arxiv 链接）
- **整类跳过**：直接跳过某个检测类别（如不检查 TODO）
- **跳过文件**：指定某些文件不扫描

### 3. 可扩展的检测规则

所有检测模式存储在 `patterns.yaml` 中，用户可以：
- 添加新的检测规则
- 调整风险等级
- 添加排除规则
- 无需修改脚本代码

## 使用步骤

### 环境准备

需要 Python 3.8+ 和两个依赖：

```bash
pip install pyyaml chardet
```

### 基本用法

```bash
# 扫描单个文件
python scripts/privacy_scanner.py paper.tex

# 扫描整个目录
python scripts/privacy_scanner.py ./submission_folder/

# 保存报告到文件
python scripts/privacy_scanner.py ./submission/ --output report.md

# 只看高风险项
python scripts/privacy_scanner.py ./submission/ --risk-filter high

# JSON 格式输出
python scripts/privacy_scanner.py ./submission/ --json
```

### 使用白名单

编辑 `references/whitelist.yaml`，填入你要排除的内容：

```yaml
whitelist:
  exact:
    - "my-public@email.com"
  patterns:
    - "https://arxiv\\.org/.*"
  skip_categories:
    - placeholder
```

然后正常扫描即可，脚本会自动加载白名单。

### 通过 AI 使用（推荐）

安装 .skill 文件后，直接对话：

> "帮我扫描一下 ./submission/ 有没有隐私信息"

AI 会：
1. 先问你有没有白名单
2. 运行扫描脚本
3. 对结果做上下文判断（区分真阳性和误报）
4. 生成最终报告 + 处理清单

## 真实案例

### 案例：扫描一个包含多种问题的提交目录

测试目录包含 4 个文件：论文草稿、AI日志、配置文件、参考文献。

**扫描结果**：

| 指标 | 数值 |
|------|------|
| 扫描文件数 | 4 |
| 发现问题总数 | 24 |
| 高风险 | 12 |
| 中风险 | 8 |
| 低风险 | 4 |

**检出内容示例**：
- 论文中的真实邮箱和手机号
- AI 日志中未删除的 API Key
- 配置文件中的硬编码密码
- 多个文件中的本地用户名路径
- 各处残留的 TODO/FIXME 标记

**加白名单后**：
设置跳过 placeholder 类别 + 排除学术 URL 后，问题数从 24 降到 19，报告更聚焦于真正需要处理的问题。

## 技能包结构

```
submission-privacy-scanner/
├── SKILL.md                    # 主指令文件
├── scripts/
│   └── privacy_scanner.py      # Python 扫描脚本
├── references/
│   ├── patterns.yaml           # 检测模式注册表
│   └── whitelist.yaml          # 白名单配置
└── test_files/                 # 测试用例
    ├── paper_with_issues.tex
    ├── ai_log.md
    ├── config_leak.py
    └── clean_references.bib
```
