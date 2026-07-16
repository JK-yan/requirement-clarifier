#!/usr/bin/env python3
"""check_questionnaire.py — requirement-clarifier 确认单回执机检

用法:
  python3 scripts/check_questionnaire.py <回填后的确认单.md...>

定位: 阶段三"验收答案"的机械约束部分。业务回执先过本脚本,机器报完"哪些题没答、
缺什么落款",AI 再做判断题部分(成色分级、冲突检测、新需求剥离)。

机判六件事(格式契约见 templates/questionnaire-template.md):
1. 逐题作答检测: "### 问题 N" 块内有勾选(☑/☒/✔/✓/[x])或【作答区】有实质内容才算已答。
   未答 → WARN;题目标注"阻塞"未答 → FAIL。
2. 多选提示: 同题勾选 >1 项 → WARN(请确认该题是否允许多选)。
3. "我不清楚"台阶: 勾了"不清楚/不知道"但【作答区】未给知情人 → WARN(索要真正知情人)。
4. 第一部分核对: 无"无异议"且【作答区】空 → WARN(已确认事项未核对)。
5. 落款检查: 填写信息区的 填写人/日期 空缺 → FAIL(落款是溯源凭证);部门空缺 → WARN。
6. 模板残留: "出题规则(给生成方"未删除 → WARN(内部注释不应发给业务)。

存在 FAIL → 退出码 1。
"""
import re, sys
from pathlib import Path

CHECKED = re.compile(r'[☑☒✔✓]|\[[xX]\]')
UNCHECKED = "☐"
QHEAD = re.compile(r'^###\s*问题\s*(?P<no>\S+?)[:：]\s*(?P<title>.*)$')
ANSWER_MARK = "【作答区】"
DONT_KNOW = re.compile(r'不清楚|不知道|不了解')

def substantive(text: str) -> bool:
    """作答区内容去掉模板占位(<...>、下划线)后是否还有实质内容。"""
    t = re.sub(r'<[^>]*>|＿+|_{2,}', '', text)
    return bool(t.strip())

def field_value(section: str, key: str) -> str:
    m = re.search(rf'{key}\s*[:：]\s*([^\s:：]*)', section)
    if not m: return ""
    return re.sub(r'＿+|_{2,}', '', m.group(1)).strip()

def check_file(fp: str):
    text = Path(fp).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    warns, fails = [], []
    print(f"\n== 机检 {fp} ==")

    if "出题规则(给生成方" in text or "出题规则（给生成方" in text:
        warns.append("模板内部注释『出题规则(给生成方…)』未删除,不应出现在发给业务的正式单里")

    # 切分区段
    def section(name):
        m = re.search(rf'^##\s*{name}.*?$(.*?)(?=^##\s|\Z)', text, re.M | re.S)
        return m.group(1) if m else None

    part1 = section("第一部分")
    part2 = section("第二部分")
    signoff = section("填写信息")

    # 4. 第一部分核对
    if part1 is not None:
        ans = " ".join((seg.strip().splitlines() or [""])[0]
                       for seg in part1.split(ANSWER_MARK)[1:])
        if "无异议" not in part1 and not substantive(ans):
            warns.append("第一部分(已确认事项)未核对: 既无『无异议』也无异议说明")

    # 1-3. 逐题检测
    unanswered, n_q = [], 0
    if part2 is not None:
        blocks = re.split(r'(?=^###\s*问题)', part2, flags=re.M)
        for blk in blocks:
            m = QHEAD.match(blk.strip().splitlines()[0]) if blk.strip() else None
            if not m: continue
            n_q += 1
            no, title = m["no"], m["title"]
            checked_lines = [l for l in blk.splitlines() if CHECKED.search(l)]
            answer_text = "\n".join(seg for seg in blk.split(ANSWER_MARK)[1:])
            answered = bool(checked_lines) or substantive(answer_text)
            blocking = "阻塞" in blk
            if not answered:
                unanswered.append((no, title, blocking))
                (fails if blocking else warns).append(
                    f"问题 {no}『{title[:30]}』未作答" + ("(阻塞级)" if blocking else ""))
            if len(checked_lines) > 1:
                warns.append(f"问题 {no} 勾选了 {len(checked_lines)} 项,请确认该题是否允许多选")
            if any(DONT_KNOW.search(l) for l in checked_lines) and not substantive(answer_text):
                warns.append(f"问题 {no} 勾了『不清楚』但作答区未提供知情人,请索要真正知情人")
    if n_q == 0:
        warns.append("未识别到任何『### 问题 N』块 —— 回执格式与模板不符,机检未覆盖,请人工核对")

    # 5. 落款
    if signoff is not None:
        for key, must in (("填写人", True), ("日期", True), ("部门", False)):
            if not field_value(signoff, key):
                (fails if must else warns).append(
                    f"落款缺『{key}』" + ("(落款是溯源凭证,缺失则回答不可入账为【业务确认】)" if must else ""))
    else:
        fails.append("缺少『## 填写信息』落款区 —— 无落款的回答不得标【业务确认】")

    for msg in fails: print(f"  ✗ {msg}")
    for msg in warns: print(f"  △ {msg}")
    if not fails and not warns: print("  ✓ 全部题目已作答,落款完整")
    return n_q, len(unanswered), warns, fails

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    t_q = t_un = t_warn = t_fail = 0
    for fp in sys.argv[1:]:
        n_q, n_un, warns, fails = check_file(fp)
        t_q += n_q; t_un += n_un; t_warn += len(warns); t_fail += len(fails)
    print("\n== 摘要 ==")
    print(f"题目 {t_q} 道 / 未答 {t_un} 道 / {t_warn} WARN / {t_fail} FAIL")
    if t_fail:
        print("✗ 机检未通过: 阻塞级未答或落款缺失。追答/补落款后重跑;机检通过≠验收完成,"
              "AI 仍须做成色分级与冲突检测。")
        sys.exit(1)
    print("✓ 机检通过。接下来交给 AI: 成色分级、冲突检测、新需求剥离。")

if __name__ == "__main__":
    main()
