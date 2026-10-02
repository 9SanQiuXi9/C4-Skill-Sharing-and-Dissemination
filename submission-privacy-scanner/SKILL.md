---
name: submission-privacy-scanner
description: >
  扫描提交文件中的隐私信息（邮箱、手机号、身份证号、URL、API密钥、本地路径、占位符等），
  生成结构化风险报告。适用于论文、作业、挑战文件提交前的隐私检查。
  触发短语：扫描隐私、检查隐私、提交前检查、privacy scan、check submission、
  隐私扫描、脱敏检查、PII check、submission check、提交安全检查
---

# Submission Privacy Scanner（提交隐私扫描器）

## Purpose

提交文件（论文、作业、挑战材料）前，自动扫描其中的隐私敏感信息，
输出一份按风险等级排序的检查报告，帮助用户在提交前完成脱敏。

**输入**：一个文件路径或目录路径
**输出**：Markdown 格式的隐私风险报告（含汇总统计 + 逐条详情 + 处理建议）

## Workflow

### Step 1 — 确认扫描目标与白名单

向用户确认：
- 扫描路径是什么？（文件或目录）
- 是否有需要加白名单的内容？（如"这个邮箱是我的笔名邮箱，不算泄露"）
- 输出格式偏好？（终端显示 / 保存为文件 / JSON）

**首次扫描时主动询问**：
> "在扫描之前，有没有某些内容是你故意放的、不算隐私泄露？
> 比如某个邮箱、某个 GitHub 链接。我可以加到白名单里，扫描时自动跳过。"

如果用户提供了白名单内容，更新 `references/whitelist.yaml` 后再扫描。

### Step 2 — 运行扫描脚本

执行 Python 扫描脚本：

```bash
python scripts/privacy_scanner.py <目标路径>
```

常用参数：
- `--output report.md`：保存报告到文件
- `--json`：输出 JSON 格式（便于程序处理）
- `--risk-filter high`：只显示高风险项
- `--patterns custom_patterns.yaml`：使用自定义检测规则
- `--whitelist my_whitelist.yaml`：使用自定义白名单
- `--max-depth 5`：限制目录扫描深度

脚本会自动加载 `references/whitelist.yaml`（如果存在），无需手动指定。

### Step 3 — 解读报告

扫描脚本输出的是**候选问题列表**，你需要逐条做上下文判断：

1. **真阳性**：确实是隐私泄露 → 标记为"需处理"
2. **误报**：看起来像但不是问题 → 标记为"可忽略"并说明原因
   - 例：`2026-10-02` 不是电话号码
   - 例：`https://arxiv.org/abs/xxxx` 是合法学术引用
   - 例：`C:\Users\Public\` 不泄露隐私

3. **需确认**：无法自动判断 → 标记为"需人工确认"并给出判断依据
   - 例：8-12 位数字串可能是学号，也可能是普通编号
   - 例：`\author{张三}` — 需要确认"张三"是否为笔名

### Step 4 — 生成最终报告

在脚本输出的基础上，叠加你的上下文判断，生成最终报告：

```markdown
# 隐私扫描最终报告

## 汇总
- 扫描文件数：X
- 脚本检出：Y 条
- 人工复核后：Z 条真实问题（A 高 / B 中 / C 低）

## 🔴 需处理
（逐条列出，含处理建议）

## 🟡 建议处理
（逐条列出）

## ✅ 已排除的误报
（简要说明排除了什么、为什么排除）

## 📋 处理清单
- [ ] 具体操作 1
- [ ] 具体操作 2
```

### Step 5 — 协助修复（可选）

如果用户要求，可以直接帮助修复：
- 替换真实姓名为笔名
- 删除 URL 中的个人标识
- 清除 TODO/FIXME 标记
- 将绝对路径替换为相对路径

修复后重新扫描一次，确认所有问题已解决。

## Detection Categories

| 类别 | 检测内容 | 风险等级 |
|------|----------|----------|
| 联系方式 | 邮箱、手机号、固定电话 | 高/中 |
| 身份信息 | 身份证号、学号/工号、LaTeX作者字段 | 高/中 |
| 网络痕迹 | URL、GitHub链接、社交媒体账号 | 高/中 |
| 密钥令牌 | API Key、Token、密码、私钥 | 高 |
| 路径泄露 | Windows/Unix 含用户名的本地路径 | 中 |
| 占位符残留 | TODO/FIXME、模板占位符 | 低/中 |

## Edge Cases

1. **二进制文件**（PDF/DOCX/PNG）：脚本自动跳过，但报告中提醒用户手动检查元数据
2. **大文件**（>1MB）：脚本自动处理，但可能较慢
3. **编码问题**：脚本自动检测文件编码（支持 UTF-8/GBK/GB2312 等）
4. **空目录**：报告"无可扫描文件"
5. **误报处理**：用户可指定白名单，或在 `patterns.yaml` 中添加 `exclude_regex`
6. **LaTeX 编译产物**（.aux, .log）：可能包含路径泄露，建议纳入扫描范围
7. **Jupyter Notebook**（.ipynb）：JSON 格式，脚本可扫描但输出可能含大量误报

## Customization

用户可以通过编辑 `references/patterns.yaml` 来自定义检测规则：
- 添加新的正则模式
- 调整风险等级
- 添加排除规则（`exclude_regex`）
- 修改处理建议

## Whitelist（白名单）

白名单让用户声明"这些不算泄露"，扫描时自动跳过，避免误报干扰。

白名单文件 `references/whitelist.yaml` 支持四种粒度：

```yaml
whitelist:
  # 1. 精确匹配：这些字符串不会被报告
  exact:
    - "sanqiuXi@gmail.com"
    - "https://github.com/sanqiuXi/public-repo"

  # 2. 模式匹配（正则）
  patterns:
    - ".*@myproject\\.org$"
    - "https://arxiv\\.org/.*"

  # 3. 整类跳过（跳过整个检测类别）
  skip_categories:
    - placeholder    # 不检查 TODO/FIXME

  # 4. 跳过指定文件（正则匹配文件路径）
  skip_files:
    - "whitelist\\.yaml$"
    - ".*\\.test\\..*"
```

**AI 交互流程**：
1. 首次扫描时主动询问用户是否有白名单
2. 用户说"xxx 不算泄露" → 自动写入 whitelist.yaml
3. 后续扫描自动加载白名单
4. 报告中显示"白名单过滤了 N 条"，让用户知道跳过了什么

## Examples

### 示例 1：扫描单个文件
```
用户：帮我检查一下 paper.tex 有没有隐私信息
→ 运行：python scripts/privacy_scanner.py paper.tex
→ 解读结果并生成报告
```

### 示例 2：扫描整个提交目录
```
用户：扫描一下我的 C2 提交文件夹 D:\WORK2\C2_submission
→ 运行：python scripts/privacy_scanner.py D:\WORK2\C2_submission --output report.md
→ 逐条复核，生成最终报告
```

### 示例 3：只检查高风险项
```
用户：快速看一下有没有高危的隐私泄露
→ 运行：python scripts/privacy_scanner.py . --risk-filter high
→ 只展示高风险项
```

### 示例 4：使用白名单
```
用户：扫描我的提交文件，但 sanqiuXi@gmail.com 是我的笔名邮箱，不算泄露
→ 更新 references/whitelist.yaml，加入 "sanqiuXi@gmail.com"
→ 运行：python scripts/privacy_scanner.py ./submission
→ 报告中该邮箱不会出现，底部显示"白名单过滤了 1 条"
```
