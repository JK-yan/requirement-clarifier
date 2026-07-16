#!/usr/bin/env python3
"""verify_evidence.py v2 — requirement-clarifier 证据核验 harness

用法:
  python3 scripts/verify_evidence.py <产出markdown...> [--root 项目根] [--strict]

机判四件事:
1. 证据引用 `> 证据: <路径>:<行号> | "<原文片段>"`
   文件/行号存在、片段可 grep(引用行±25行=PASS;仅别处=WARN 行号漂移;找不到=FAIL 疑似幻觉;
   无片段=FAIL 视同假设)。路径以项目根为基准;根下找不到时沿引用文件目录向上回退解析,
   命中则 WARN 提示改为根基准。
2. 零引用警告: 整份文件 0 条引用 → 显著 WARN(该文件未受证据保护,来源性内容视同【假设】)。
   "干脆不引用"不再是无声通过。
3. 无主数值探测: 含金额/天数/期数/日期/时刻/百分比的行,若无保护标记
   (【】标签 / 证据引用 / 演示|示例 / 待确认 / Q·BQ编号 / 标题·引用行) → WARN;--strict 下计为 FAIL。
4. 覆盖行统计: 文件宣称"逐维度/盲区"时,逐维度结论行(含 适用/不适用)不足 8 行 → WARN。

另: 统计三档溯源标签,集中列出全部【假设】。存在 FAIL → 退出码 1。
"""
import argparse, re, sys
from pathlib import Path

CITE = re.compile(
    r'^>\s*证据[:：]\s*(?P<path>[^\s|｜]+?):(?P<l1>\d+)(?:-(?P<l2>\d+))?'
    r'(?:\s*[|｜]\s*["“](?P<snip>.+?)["”])?\s*$')
LABELS = ("【业务确认】", "【开发拟定】", "【假设】", "【假设·未取证】")
BARENUM = re.compile(r'\d+(?:\.\d+)?\s*(?:万|元|块|期|天|个月|小时|%|％)|\d{4}[-/年]\d{1,2}|\d{1,2}:\d{2}')
PROTECT = re.compile(r'【|证据[:：]|演示|示例|待确认|待定|存疑|Q\d|BQ\d|维度')

def norm(s): return re.sub(r'\s+', '', s)

def check_citation(root: Path, path: str, l1: int, snip, base: Path = None):
    f, basis_warn = root / path, ""
    if not f.is_file() and base is not None:
        cur = base
        while True:
            cand = cur / path
            if cand.is_file():
                try: rel = cand.relative_to(root)
                except ValueError: rel = cand
                f, basis_warn = cand, f"路径基准非项目根(实际 {rel}),建议改根基准"
                break
            if cur == root or cur.parent == cur: break
            cur = cur.parent
    if not f.is_file(): return "FAIL", f"文件不存在: {path}"
    try: lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e: return "FAIL", f"无法读取 {path}: {e}"
    if l1 < 1 or l1 > len(lines): return "FAIL", f"{path} 共 {len(lines)} 行, 引用第 {l1} 行"
    if snip is None: return "FAIL", "证据未附原文片段, 无法自证 —— 视同【假设】"
    target = norm(snip)
    if not target: return "FAIL", "片段为空"
    lo, hi = max(0, l1 - 26), min(len(lines), l1 + 25)
    if target in norm("".join(lines[lo:hi])):
        return ("WARN", basis_warn) if basis_warn else ("PASS", "")
    if target in norm("".join(lines)):
        return "WARN", f"片段在 {path} 中存在但不在第 {l1} 行附近(行号漂移?)"
    return "FAIL", f"片段在 {path} 中不存在 —— 疑似幻觉引用"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+"); ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="无主数值计为 FAIL")
    a = ap.parse_args(); root = Path(a.root).resolve()
    n_pass = n_warn = n_fail = 0
    assumptions, label_count = [], {k: 0 for k in LABELS}

    for fp in a.files:
        text = Path(fp).read_text(encoding="utf-8", errors="replace")
        print(f"\n== 核验 {fp} (root={root}) ==")
        cites_here, bare, in_code = 0, [], False
        for i, line in enumerate(text.splitlines(), 1):
            st = line.strip()
            if st.startswith("```"): in_code = not in_code; continue
            m = CITE.match(st)
            if m:
                cites_here += 1
                status, msg = check_citation(root, m["path"], int(m["l1"]), m["snip"],
                                             base=Path(fp).resolve().parent)
                print(f"  {dict(PASS='✓',WARN='△',FAIL='✗')[status]} L{i} {m['path']}:{m['l1']}"
                      + (f" — {msg}" if msg else ""))
                n_pass += status=="PASS"; n_warn += status=="WARN"; n_fail += status=="FAIL"
            elif (not in_code and st and not st.startswith(("#", ">", "|--", "---"))
                  and BARENUM.search(st) and not PROTECT.search(st)):
                bare.append((i, st[:60]))
            for lab in LABELS:
                if lab in line:
                    label_count[lab] += line.count(lab)
                    if lab == "【假设】": assumptions.append(f"{fp}:L{i} {st[:80]}")
        if cites_here == 0:
            print(f"  ⚠⚠ 零引用: 本文件没有任何证据引用 —— 未受证据保护,其中来源性陈述一律视同【假设】")
            n_warn += 1
        if bare:
            tag = "✗" if a.strict else "△"
            print(f"  {tag} 无主数值 {len(bare)} 处(无标签/无引用/非演示的具体数字):")
            for ln, s in bare[:8]: print(f"     L{ln}: {s}")
            if a.strict: n_fail += len(bare)
            else: n_warn += len(bare)
        if ("逐维度" in text or "盲区" in text):
            dim = len(re.findall(r"^\s*(?:\d+[.、]|[-|*]).*(?:适用|不适用)", text, re.M))
            if dim < 8:
                print(f"  △ 宣称逐维度但结论行仅 {dim} 行(<8),疑似总结段落替代")
                n_warn += 1

    print("\n== 摘要 ==")
    print(f"证据: {n_pass} PASS / {n_warn} WARN / {n_fail} FAIL")
    print("溯源标签: " + "  ".join(f"{k}×{v}" for k, v in label_count.items()))
    if assumptions:
        print("⚠ 以下【假设】不得作为开发依据:")
        for x in assumptions: print("   - " + x)
    if n_fail:
        print("✗ 存在核验失败: 修正引用/补标签, 或将对应结论降级【假设】。"); sys.exit(1)
    print("✓ 证据核验通过。")

if __name__ == "__main__":
    main()
