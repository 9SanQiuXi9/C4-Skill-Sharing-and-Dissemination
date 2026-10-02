# Submission Privacy Scanner — C4 技能分享与传播

## 项目概述

**Submission Privacy Scanner**（提交隐私扫描器）是一个 Qoder Skill，用于在提交文件（论文、作业、挑战材料）前自动扫描其中的隐私敏感信息，输出按风险等级排序的检查报告。

## 功能特性

- **6 大检测类别**: 联系方式、身份信息、网络痕迹、密钥令牌、路径泄露、占位符残留
- **20+ 检测规则**: YAML 驱动，无需改代码即可扩展
- **白名单机制**: 4 级粒度（精确匹配、正则模式、跳过类别、跳过文件）
- **多编码支持**: 自动检测 UTF-8/GBK/GB2312 等编码
- **多格式支持**: .md, .tex, .py, .bib, .yaml, .json 等 40+ 种文件类型
- **风险分级**: 高/中/低三级，优先处理高危项

## 项目结构

```
C4/
├── SanQiuXi_C4_AAR.md              # 七维复盘
── SanQiuXi_C4_skill说明.md         # 技能说明文档
├── SanQiuXi_C4_教学说明.md          # 教学文档（含 FAQ）
├── SanQiuXi_C4_demo说明.md          # Demo 说明
├── SanQiuXi_C4_AI日志.md            # AI 使用日志
├── SanQiuXi_C4_submission-privacy-scanner.skill  # 技能包（tar.gz）
── demo_report.md                   # 扫描报告（Markdown）
├── demo_report_汇总与高风险.png      # Demo 截图 1
├── demo_report_中低风险.png          # Demo 截图 2
└── submission-privacy-scanner/      # 技能源码
    ├── SKILL.md                     # 技能指令文件
    ├── scripts/
    │   └── privacy_scanner.py       # 核心扫描脚本
    ├── references/
    │   ├── patterns.yaml            # 检测规则
    │   └── whitelist.yaml           # 白名单模板
    └── test_files/                  # 测试文件
        ├── paper_with_issues.tex
        ├── ai_log.md
        ├── config_leak.py
        └── clean_references.bib
```

## 快速开始

### 安装依赖

```bash
python -m venv .venv
.venv/bin/pip install pyyaml chardet
```

### 运行扫描

```bash
python submission-privacy-scanner/scripts/privacy_scanner.py <目标路径>
```

### 生成报告到文件

```bash
python submission-privacy-scanner/scripts/privacy_scanner.py <目标路径> --output report.md
```

### 只检查高风险项

```bash
python submission-privacy-scanner/scripts/privacy_scanner.py <目标路径> --risk-filter high
```

## 导入为 Qoder Skill

将 `SanQiuXi_C4_submission-privacy-scanner.skill` 文件导入 Qoder，即可通过自然语言触发扫描：

> "帮我检查一下这个文件夹有没有隐私信息"
> "提交前帮我扫一下"

## 技术栈

- **语言**: Python 3
- **依赖**: PyYAML, chardet
- **检测方式**: 正则表达式（确定性扫描）+ 人工/AI 上下文判断
- **配置格式**: YAML

## 交付物清单

| 文件 | 说明 |
|------|------|
| .skill 技能包 | 可导入的完整技能 |
| 技能说明.md | 功能介绍、使用方法 |
| 教学说明.md | 教学文档，含 FAQ |
| demo说明.md | Demo 演示说明 |
| AI日志.md | AI 协作日志（4 次迭代） |
| AAR.md | 七维复盘 |
| 扫描报告 + 截图 | 实际运行效果 |
