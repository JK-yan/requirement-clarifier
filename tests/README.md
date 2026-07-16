# 压测场景:判断题规则的回归测试

`verify_evidence.py` / `check_questionnaire.py` 管得住**机械约束**,但 skill 里最值钱的是**判断题规则**(信源分级、环境自检、回答验收)——它们无法用 regex 强制,只能用压力场景验证。本目录借用 [superpowers](https://github.com/obra/superpowers) 的思路:**写 skill 就是对流程文档做 TDD**。

## RED-GREEN 工作流

| TDD | 对应操作 |
|---|---|
| 测试先行(RED) | 把场景 prompt 喂给**未加载本 skill** 的新对话,记录它如何违规、用什么话术自我合理化 |
| 实现(GREEN) | 同一 prompt 喂给**加载了本 skill** 的新对话,对照判定清单逐项打分 |
| 重构 | 发现新的合理化话术 → 补进 SKILL.md 对应规则 → 重跑场景确认仍通过 |

**每次修改 SKILL.md 的判断题段落(铁律 3、阶段一分级、阶段三验收、模式 B 第 0 步),发版前至少重跑涉及的场景。** 判定清单里任何一项从过变不过,就是回归。

## 运行方式

- **基线(RED)**:新开一个不含本 skill 的会话(或明确指示"不要调用任何 skill"),粘贴场景文件中的『场景 prompt』,原样记录回答。
- **合规(GREEN)**:在装有本 skill 的环境新开会话,粘贴同一 prompt,按『判定清单』逐项勾选。
- 用 subagent 跑更省事:主会话把 prompt 派给一个干净子代理即可;注意基线子代理要禁用 skill 调用。

## 场景清单

| 文件 | 压的是哪条规则 | 典型违规 |
|---|---|---|
| [scenario-1-source-tiering.md](scenario-1-source-tiering.md) | 铁律 3 + 阶段一信源分级 | 拿开发者的架构理解覆盖需求方 Excel |
| [scenario-2-env-selfcheck.md](scenario-2-env-selfcheck.md) | 模式 B 第 0 步环境自检 | 无代码库时编造"现有页面"的字段和行为 |
| [scenario-3-dirty-receipt.md](scenario-3-dirty-receipt.md) | 阶段三验收答案 | 混入的新需求被无声合并;"看着办"被当成授权 |

## 判分标准

每个场景的判定清单为二值项(过/不过),**全过才算 GREEN**。部分通过说明规则文本有漏洞——把该次违规的原话记进场景文件的『已知合理化话术』,然后修 SKILL.md。
