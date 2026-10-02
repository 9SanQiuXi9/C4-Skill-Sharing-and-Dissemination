# 隐私扫描报告

> 扫描时间：2026-10-02 14:19:00

## 汇总

| 指标 | 数值 |
|------|------|
| 扫描文件数 | 4 |
| 跳过二进制文件 | 0 |
| 发现问题总数 | 24 |
| 🔴 高风险 | 12 |
| 🟡 中风险 | 8 |
| 🟢 低风险 | 4 |
| **综合风险等级** | **🔴 高风险** |

> 已加载白名单：`whitelist.yaml`

## 🔴 高风险项（12）

| 文件 | 行号 | 类型 | 匹配内容 | 建议 |
|------|------|------|----------|------|
| ai_log.md | 5 | API密钥/令牌 | `Key:***5pqr` | 立即删除并轮换密钥 |
| ai_log.md | 5 | 已知前缀的密钥 | `sk-a***5pqr` | 立即删除并在对应平台轮换密钥 |
| ai_log.md | 8 | GitHub个人链接 | `http***ner
` | 删除或替换为匿名仓库 |
| ai_log.md | 9 | 密码字段 | `pass***@ss!` | 立即删除 |
| ai_log.md | 13 | 社交媒体账号 | `微信: ***3abc` | 删除 |
| config_leak.py | 5 | API密钥/令牌 | `TOKE***7890` | 立即删除并轮换密钥 |
| config_leak.py | 6 | 密码字段 | `PASS***3456` | 立即删除 |
| config_leak.py | 14 | 身份证号 | `1101***1234` | 立即删除 |
| paper_with_issues.tex | 4 | 电子邮箱 | `zhan***u.cn` | 删除或替换为匿名邮箱 |
| paper_with_issues.tex | 8 | GitHub个人链接 | `http***ect
` | 删除或替换为匿名仓库 |
| paper_with_issues.tex | 14 | 电子邮箱 | `zhan***.com` | 删除或替换为匿名邮箱 |
| paper_with_issues.tex | 15 | 中国手机号 | `1381***5678` | 立即删除 |

## 🟡 中风险项（8）

| 文件 | 行号 | 类型 | 匹配内容 | 建议 |
|------|------|------|----------|------|
| ai_log.md | 8 | URL链接 | `http***nner` | 检查链接是否包含个人信息，学术引用URL可保留 |
| ai_log.md | 12 | Unix/Mac用户路径 | `/hom***ser/` | 替换为相对路径或 ~/ |
| config_leak.py | 4 | URL链接 | `http***m/v1` | 检查链接是否包含个人信息，学术引用URL可保留 |
| config_leak.py | 5 | 长数字串(疑似学号/工号) ⚠️需人工确认 | `1234***7890` | 确认是否为学号/工号，如是则删除 |
| config_leak.py | 13 | 长数字串(疑似学号/工号) ⚠️需人工确认 | `2024***0304` | 确认是否为学号/工号，如是则删除 |
| paper_with_issues.tex | 8 | URL链接 | `http***ject` | 检查链接是否包含个人信息，学术引用URL可保留 |
| paper_with_issues.tex | 10 | Windows用户路径 | `D:\U***san\` | 替换为相对路径或通用路径 |
| paper_with_issues.tex | 15 | 长数字串(疑似学号/工号) ⚠️需人工确认 | `1381***5678` | 确认是否为学号/工号，如是则删除 |

## 🟢 低风险项（4）

| 文件 | 行号 | 类型 | 匹配内容 | 建议 |
|------|------|------|----------|------|
| ai_log.md | 15 | TODO/FIXME标记 | `TO***` | 完成内容或删除标记 |
| ai_log.md | 16 | TODO/FIXME标记 | `FI***` | 完成内容或删除标记 |
| config_leak.py | 10 | TODO/FIXME标记 | `TO***` | 完成内容或删除标记 |
| paper_with_issues.tex | 12 | TODO/FIXME标记 | `TO***` | 完成内容或删除标记 |

---

*由 Submission Privacy Scanner 生成*

