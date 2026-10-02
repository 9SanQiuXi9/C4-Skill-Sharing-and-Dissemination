# C4 教学说明：Submission Privacy Scanner

## 快速上手（3 分钟）

### 第一步：安装

1. 获取技能包 `submission-privacy-scanner/` 文件夹
2. 确保已安装 Python 3.8+
3. 安装依赖：
   ```bash
   pip install pyyaml chardet
   ```

### 第二步：第一次扫描

```bash
python scripts/privacy_scanner.py ./你的提交目录/
```

你会看到一份 Markdown 格式的报告，按风险等级列出所有发现的问题。

### 第三步：处理问题

根据报告逐项处理：
- 🔴 高风险：必须处理（删除或替换）
- 🟡 中风险：建议处理（确认是否真的需要保留）
- 🟢 低风险：可以处理（完善文档内容）

## 常见问题

### Q1：扫描结果太多，很多是误报怎么办？

使用白名单功能。编辑 `references/whitelist.yaml`：

```yaml
whitelist:
  patterns:
    - "https://arxiv\\.org/.*"     # 排除所有 arxiv 链接
    - ".*@university\\.edu\\.cn$"   # 排除学校邮箱
  skip_categories:
    - placeholder                   # 不检查 TODO/FIXME
```

### Q2：我不想装 Python，能直接用吗？

可以。把技能包安装到 AI 环境中，直接说"扫描这个目录的隐私信息"。AI 会调用脚本并帮你解读结果。但脚本本身需要 Python 环境来运行。

### Q3：能不能检测 PDF 或 Word 文件？

目前不支持二进制文件（PDF/DOCX/PNG 等）。脚本会跳过这些文件，但在报告中提醒你手动检查：
- PDF：打开文档属性，删除个人信息
- Word：文件 → 信息 → 检查文档 → 删除元数据

未来版本可能加入 PDF 元数据扫描。

### Q4：我想添加新的检测规则怎么做？

编辑 `references/patterns.yaml`，按现有格式添加：

```yaml
- id: my_custom_rule
  name: "自定义检测"
  category: contact
  risk: medium
  regex: '你的正则表达式'
  description: "检测什么"
  suggestion: "怎么处理"
```

不需要修改任何代码，脚本会自动加载新规则。

### Q5：扫描会不会修改我的文件？

不会。脚本是只读的，只读取文件内容并生成报告，不会修改任何原始文件。

## 优化技巧

### 技巧 1：先快速扫描高风险

```bash
python scripts/privacy_scanner.py ./submission/ --risk-filter high
```

如果高风险为 0，基本可以放心提交。

### 技巧 2：用 JSON 输出做自动化

```bash
python scripts/privacy_scanner.py ./submission/ --json --output result.json
```

可以在脚本中解析 JSON 结果，集成到 CI/CD 流程中。

### 技巧 3：为不同场景准备不同白名单

- 论文提交：排除学术 URL，保留路径检查
- 代码提交：排除 TODO，保留密钥检查
- 一般文档：全量检查

准备多个 whitelist 文件，用 `--whitelist` 参数切换。

## 典型踩坑

1. **编码问题**：如果文件是 GBK 编码，脚本会自动检测，但偶尔会误判。如果遇到乱码，可以在文件开头加 BOM 标记强制 UTF-8。

2. **大目录很慢**：如果目录中有大量文件，可以用 `--max-depth 2` 限制扫描深度，避免扫描过深的子目录。

3. **Jupyter Notebook**：.ipynb 文件是 JSON 格式，脚本会扫描但可能产生大量误报（因为 JSON 结构中有很多看起来像隐私的字符串）。建议重点关注 output 单元格中的内容。
