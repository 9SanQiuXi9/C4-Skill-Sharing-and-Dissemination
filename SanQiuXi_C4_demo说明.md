# C4 Demo：Submission Privacy Scanner 演示

## 演示场景

模拟一个学生准备提交 C2 论文，扫描提交目录中的隐私问题。

## 演示步骤

### Step 1：准备提交目录

提交目录结构：
```
submission/
├── paper.tex          # 论文主文件
├── references.bib     # 参考文献
├── ai_log.md          # AI 使用日志
└── method.md          # 方法说明
```

### Step 2：运行扫描

```bash
python scripts/privacy_scanner.py ./submission/
```

### Step 3：查看报告

```markdown
# 隐私扫描报告

> 扫描时间：2026-10-02 14:30:00

## 汇总

| 指标 | 数值 |
|------|------|
| 扫描文件数 | 4 |
| 跳过二进制文件 | 0 |
| 发现问题总数 | 18 |
| 🔴 高风险 | 8 |
| 🟡 中风险 | 6 |
| 🟢 低风险 | 4 |
| **综合风险等级** | **🔴 高风险** |

## 🔴 高风险项（8）

| 文件 | 行号 | 类型 | 匹配内容 | 建议 |
|------|------|------|----------|------|
| paper.tex | 3 | 电子邮箱 | `author***@gmail.com` | 删除或替换为匿名邮箱 |
| paper.tex | 15 | 中国手机号 | `1381***5678` | 立即删除 |
| paper.tex | 22 | GitHub个人链接 | `https://github.com/username/repo` | 删除或替换为匿名仓库 |
| ai_log.md | 8 | API密钥/令牌 | `sk-pro***abcd` | 立即删除并轮换密钥 |
| ai_log.md | 12 | 密码字段 | `pass***1234` | 立即删除 |
| ai_log.md | 18 | 社交媒体账号 | `微信: mywxid123` | 删除 |
| method.md | 5 | 身份证号 | `11010***1234` | 立即删除 |
| method.md | 30 | LaTeX作者字段 | `\author{Real Name}` | 确认是否为笔名 |

## 🟡 中风险项（6）

| 文件 | 行号 | 类型 | 匹配内容 | 建议 |
|------|------|------|----------|------|
| paper.tex | 10 | URL链接 | `https://my-personal-site.com` | 检查是否包含个人信息 |
| paper.tex | 25 | Windows用户路径 | `C:\Users\username\Documents\` | 替换为相对路径 |
| ai_log.md | 5 | URL链接 | `https://github.com/username/project` | 删除个人链接 |
| ai_log.md | 20 | Unix/Mac用户路径 | `/home/username/projects/` | 替换为相对路径 |
| method.md | 8 | 长数字串(疑似学号/工号) ⚠️需人工确认 | `20240***0304` | 确认是否为学号 |
| method.md | 15 | URL链接 | `https://personal-blog.example.com` | 检查是否为个人链接 |

## 🟢 低风险项（4）

| 文件 | 行号 | 类型 | 匹配内容 | 建议 |
|------|------|------|----------|------|
| paper.tex | 40 | TODO/FIXME标记 | `TODO: add more references` | 完成内容或删除标记 |
| ai_log.md | 25 | TODO/FIXME标记 | `FIXME: clean up log` | 完成内容或删除标记 |
| method.md | 12 | TODO/FIXME标记 | `TODO: verify equation` | 完成内容或删除标记 |
| method.md | 35 | 模板占位符 | `[your name here]` | 替换为实际内容 |
```

### Step 4：AI 解读（如果使用 AI 模式）

AI 会对扫描结果做上下文判断：

```markdown
# 隐私扫描最终报告

## 汇总
- 扫描文件数：4
- 脚本检出：18 条
- 人工复核后：15 条真实问题（7 高 / 5 中 / 3 低）

## 🔴 需处理（7 条）
1. paper.tex:3 — 真实邮箱，替换为匿名邮箱
2. paper.tex:15 — 手机号，立即删除
3. paper.tex:22 — 个人 GitHub 链接，删除
4. ai_log.md:8 — API Key 未删除，立即删除并轮换
5. ai_log.md:12 — 密码未删除，立即删除
6. ai_log.md:18 — 微信号，删除
7. method.md:5 — 身份证号，立即删除

## 🟡 建议处理（5 条）
1. paper.tex:25 — 本地路径泄露用户名，改为相对路径
2. ai_log.md:5 — 个人 GitHub 链接，删除
3. ai_log.md:20 — 本地路径，改为相对路径
4. method.md:8 — 疑似学号，确认后删除
5. method.md:35 — 模板占位符未替换

## ✅ 已排除的误报（3 条）
1. paper.tex:10 — `my-personal-site.com` 是项目官网，不是个人隐私
2. method.md:15 — `personal-blog.example.com` 是示例域名，不是真实链接
3. method.md:30 — `\author{Real Name}` 中的 "Real Name" 是占位符，不是真实姓名

## 📋 处理清单
- [ ] 删除 paper.tex 中的邮箱和手机号
- [ ] 删除 paper.tex 中的 GitHub 链接
- [ ] 删除 ai_log.md 中的 API Key 和密码
- [ ] 删除 ai_log.md 中的微信号
- [ ] 删除 method.md 中的身份证号
- [ ] 将所有绝对路径替换为相对路径
- [ ] 替换 method.md 中的模板占位符
- [ ] 完成后重新扫描确认
```

### Step 5：加白名单后重新扫描

用户设置白名单：
```yaml
whitelist:
  exact:
    - "project@official.org"
  patterns:
    - ".*arxiv\\.org.*"
  skip_categories:
    - placeholder
```

重新扫描后，报告更聚焦：
- 问题数从 18 降到 12
- TODO/FIXME 不再出现
- 学术 URL 不再出现
- 报告底部显示"白名单过滤了 6 条"

## 演示结论

Submission Privacy Scanner 能够：
1. 自动检测 6 大类隐私问题
2. 通过白名单减少误报
3. 生成清晰的风险报告和处理清单
4. 帮助用户在提交前完成脱敏
