#!/usr/bin/env python3
"""
Submission Privacy Scanner
Scans files and directories for privacy-sensitive information before submission.
"""

import os
import re
import sys
import json
import argparse
import io
from pathlib import Path
from datetime import datetime

try:
    import chardet
except ImportError:
    chardet = None

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


BINARY_EXTENSIONS = {
    '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac', '.ogg',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt',
    '.woff', '.woff2', '.ttf', '.eot',
    '.pyc', '.pyo', '.class', '.o', '.obj',
}

SCAN_EXTENSIONS = {
    '.md', '.tex', '.txt', '.py', '.js', '.ts', '.java', '.c', '.cpp',
    '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.sh', '.bash',
    '.yaml', '.yml', '.json', '.csv', '.tsv', '.xml', '.html', '.css',
    '.sql', '.r', '.R', '.m', '.ipynb', '.toml', '.ini', '.cfg',
    '.conf', '.log', '.env', '.bat', '.ps1', '.lua', '.pl', '.swift',
    '.kt', '.scala', '.jl', '.hs', '.elm', '.clj', '.lisp', '.vim',
    '.dockerfile', '.makefile', '.cmake', '.bib', '.aux', '.sty',
    '.cls', '.bst',
}

RISK_LABELS = {'high': '高风险', 'medium': '中风险', 'low': '低风险'}
RISK_ICONS = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}


def load_patterns(patterns_path):
    with open(patterns_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    categories = data.get('categories', {})
    compiled = []
    for p in data.get('patterns', []):
        entry = {
            'id': p['id'],
            'name': p['name'],
            'category': p['category'],
            'risk': p['risk'],
            'regex': re.compile(p['regex'], re.IGNORECASE),
            'description': p.get('description', ''),
            'suggestion': p.get('suggestion', ''),
            'context_required': p.get('context_required', False),
            'exclude_regex': [re.compile(e, re.IGNORECASE)
                              for e in p.get('exclude_regex', [])],
        }
        compiled.append(entry)
    return compiled, categories


def load_whitelist(whitelist_path):
    if not whitelist_path or not os.path.exists(whitelist_path):
        return None
    with open(whitelist_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not data or 'whitelist' not in data:
        return None
    wl = data['whitelist']
    return {
        'exact': set(wl.get('exact', []) or []),
        'patterns': [re.compile(p, re.IGNORECASE)
                     for p in (wl.get('patterns', []) or [])],
        'skip_categories': set(wl.get('skip_categories', []) or []),
        'skip_files': [re.compile(p, re.IGNORECASE)
                       for p in (wl.get('skip_files', []) or [])],
    }


def is_whitelisted(match_text, category, file_rel_path, whitelist):
    if whitelist is None:
        return False
    if category in whitelist['skip_categories']:
        return True
    if match_text in whitelist['exact']:
        return True
    for pat in whitelist['patterns']:
        if pat.search(match_text):
            return True
    for pat in whitelist['skip_files']:
        if pat.search(file_rel_path):
            return True
    return False


def detect_encoding(file_path):
    if chardet is None:
        return 'utf-8'
    with open(file_path, 'rb') as f:
        raw = f.read(min(os.path.getsize(file_path), 100000))
    result = chardet.detect(raw)
    return result.get('encoding') or 'utf-8'


def read_file_lines(file_path):
    try:
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.readlines()
    except Exception:
        return None


def mask_content(match_text, show_chars=4):
    if len(match_text) <= show_chars * 2:
        return match_text[:2] + '***'
    return match_text[:show_chars] + '***' + match_text[-show_chars:]


def is_excluded(match_text, exclude_patterns):
    for pat in exclude_patterns:
        if pat.search(match_text):
            return True
    return False


def scan_file(file_path, patterns, whitelist, base_dir=None):
    lines = read_file_lines(file_path)
    if lines is None:
        return {'status': 'error', 'message': '无法读取文件'}

    findings = []
    whitelisted_count = 0
    rel_path = str(file_path)
    if base_dir:
        try:
            rel_path = str(file_path.relative_to(base_dir))
        except ValueError:
            pass

    for line_num, line in enumerate(lines, start=1):
        for pat in patterns:
            for m in pat['regex'].finditer(line):
                matched = m.group(0)
                if is_excluded(matched, pat['exclude_regex']):
                    continue
                if is_whitelisted(matched, pat['category'], rel_path, whitelist):
                    whitelisted_count += 1
                    continue
                findings.append({
                    'file': rel_path,
                    'line': line_num,
                    'col': m.start() + 1,
                    'pattern_id': pat['id'],
                    'pattern_name': pat['name'],
                    'category': pat['category'],
                    'risk': pat['risk'],
                    'matched_raw': matched,
                    'matched_display': mask_content(matched),
                    'context': line.strip()[:120],
                    'description': pat['description'],
                    'suggestion': pat['suggestion'],
                    'context_required': pat['context_required'],
                })

    return {'status': 'ok', 'findings': findings,
            'whitelisted': whitelisted_count}


def collect_files(target_path, max_depth=10):
    target = Path(target_path)
    if target.is_file():
        return [target]

    files = []
    for root, dirs, filenames in os.walk(target):
        depth = len(Path(root).relative_to(target).parts)
        if depth >= max_depth:
            dirs.clear()
            continue
        for fn in filenames:
            fp = Path(root) / fn
            ext = fp.suffix.lower()
            if ext in BINARY_EXTENSIONS:
                continue
            if ext in SCAN_EXTENSIONS or ext == '':
                files.append(fp)
    return sorted(files)


def generate_report(all_findings, files_scanned, skipped_binary,
                    whitelisted_total, whitelist_path, output_path=None):
    high = [f for f in all_findings if f['risk'] == 'high']
    medium = [f for f in all_findings if f['risk'] == 'medium']
    low = [f for f in all_findings if f['risk'] == 'low']

    if not all_findings:
        overall_risk = '✅ 安全'
    elif high:
        overall_risk = '🔴 高风险'
    elif medium:
        overall_risk = '🟡 中等风险'
    else:
        overall_risk = '🟢 低风险'

    lines = []
    lines.append('# 隐私扫描报告\n')
    lines.append(f'> 扫描时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

    lines.append('## 汇总\n')
    lines.append('| 指标 | 数值 |')
    lines.append('|------|------|')
    lines.append(f'| 扫描文件数 | {files_scanned} |')
    lines.append(f'| 跳过二进制文件 | {skipped_binary} |')
    lines.append(f'| 发现问题总数 | {len(all_findings)} |')
    lines.append(f'| 🔴 高风险 | {len(high)} |')
    lines.append(f'| 🟡 中风险 | {len(medium)} |')
    lines.append(f'| 🟢 低风险 | {len(low)} |')
    if whitelisted_total > 0:
        lines.append(f'| ✅ 白名单过滤 | {whitelisted_total} |')
    lines.append(f'| **综合风险等级** | **{overall_risk}** |')
    lines.append('')

    if whitelist_path:
        lines.append(f'> 已加载白名单：`{os.path.basename(whitelist_path)}`\n')

    if not all_findings:
        lines.append('未发现隐私风险问题，文件可以安全提交。\n')
    else:
        for risk_level, group in [('high', high), ('medium', medium),
                                   ('low', low)]:
            if not group:
                continue
            icon = RISK_ICONS[risk_level]
            label = RISK_LABELS[risk_level]
            lines.append(f'## {icon} {label}项（{len(group)}）\n')
            lines.append('| 文件 | 行号 | 类型 | 匹配内容 | 建议 |')
            lines.append('|------|------|------|----------|------|')
            for f in sorted(group, key=lambda x: (x['file'], x['line'])):
                ctx = ' ⚠️需人工确认' if f['context_required'] else ''
                lines.append(
                    f"| {f['file']} | {f['line']} "
                    f"| {f['pattern_name']}{ctx} "
                    f"| `{f['matched_display']}` | {f['suggestion']} |"
                )
            lines.append('')

    if skipped_binary > 0:
        lines.append('## ⚠️ 未扫描的二进制文件\n')
        lines.append('以下二进制文件未被扫描，建议手动检查：')
        lines.append('- PDF：检查文档属性 → 删除个人信息')
        lines.append('- Office 文件：检查元数据中的作者信息')
        lines.append('- 图片：检查 EXIF 数据中的位置和设备信息')
        lines.append('')

    lines.append('---\n')
    lines.append('*由 Submission Privacy Scanner 生成*\n')

    report = '\n'.join(lines)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Submission Privacy Scanner - 提交前隐私检查工具'
    )
    parser.add_argument('target', help='要扫描的文件或目录路径')
    parser.add_argument('--patterns', '-p', default=None,
                        help='自定义检测模式文件路径（YAML格式）')
    parser.add_argument('--whitelist', '-w', default=None,
                        help='白名单文件路径（YAML格式）')
    parser.add_argument('--output', '-o', default=None,
                        help='报告输出路径（默认输出到终端）')
    parser.add_argument('--json', action='store_true',
                        help='以 JSON 格式输出结果')
    parser.add_argument('--max-depth', type=int, default=10,
                        help='最大目录扫描深度（默认 10）')
    parser.add_argument('--risk-filter', choices=['high', 'medium', 'low'],
                        default=None, help='只显示指定风险等级的问题')

    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: 路径不存在: {args.target}", file=sys.stderr)
        sys.exit(1)

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    patterns_path = (args.patterns
                     or str(project_dir / 'references' / 'patterns.yaml'))
    whitelist_path = (args.whitelist
                      or str(project_dir / 'references' / 'whitelist.yaml'))

    if not os.path.exists(patterns_path):
        print(f"Error: 模式文件不存在: {patterns_path}", file=sys.stderr)
        sys.exit(1)

    patterns, categories = load_patterns(patterns_path)
    whitelist = load_whitelist(whitelist_path)

    if target.is_file():
        files = [target]
        base_dir = target.parent
    else:
        files = collect_files(target, args.max_depth)
        base_dir = target

    binary_count = 0
    if target.is_dir():
        for root, dirs, filenames in os.walk(target):
            for fn in filenames:
                fp = Path(root) / fn
                if fp.suffix.lower() in BINARY_EXTENSIONS:
                    binary_count += 1

    all_findings = []
    whitelisted_total = 0
    scanned = 0
    for fp in files:
        result = scan_file(fp, patterns, whitelist, base_dir)
        if result['status'] == 'ok':
            scanned += 1
            all_findings.extend(result['findings'])
            whitelisted_total += result.get('whitelisted', 0)
        elif result['status'] == 'error':
            print(f"Warning: {result['message']}: {fp}", file=sys.stderr)

    if args.risk_filter:
        all_findings = [f for f in all_findings if f['risk'] == args.risk_filter]

    wl_display = whitelist_path if whitelist else None

    if args.json:
        output = {
            'scan_time': datetime.now().isoformat(),
            'target': str(target),
            'files_scanned': scanned,
            'binary_skipped': binary_count,
            'whitelisted': whitelisted_total,
            'total_findings': len(all_findings),
            'findings': [
                {k: v for k, v in f.items() if k != 'matched_raw'}
                for f in all_findings
            ],
        }
        text = json.dumps(output, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            print(text)
    else:
        report = generate_report(all_findings, scanned, binary_count,
                                 whitelisted_total, wl_display, args.output)
        if not args.output:
            print(report)
        else:
            print(f"报告已保存到: {args.output}")

    return 1 if any(f['risk'] == 'high' for f in all_findings) else 0


if __name__ == '__main__':
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                      errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8',
                                      errors='replace')
    sys.exit(main())
