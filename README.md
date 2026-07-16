# Requirement Clarifier（需求澄清器）

一个适用于 OpenCode、Claude Code 及所有兼容 OpenCode / Claude Code skill 规范的 AI Agent 的需求澄清 skill。

它帮助开发者把业务方口述的、零散混乱的需求，转化为可直接落地的开发规格，并在项目里持续沉淀业务上下文。

## 适用平台

本 skill 采用通用 skill 目录结构，兼容以下平台：

- [OpenCode](https://opencode.ai)
- [Claude Code](https://claude.ai/code)
- 任何支持 `SKILL.md` + `references/` + `templates/` + `scripts/` 目录结构的 AI Agent 平台

## 核心能力

1. 用系统化的盲区清单挑出业务没讲清、但开发动手前必须确认的漏洞。
2. 对业务回答做三色分级（【业务确认】/【开发拟定】/【假设】）与冲突检测。
3. 处理开发中途的需求变更。
4. 逆向现有 Excel / 老系统的公式为规则文档，并交规则 owner 验真。
5. 维护 `docs/requirements/` 下的业务上下文，越用越懂这个业务。
6. 产出开发规格和业务能看懂的可填写确认单。
7. 有代码库时主动审计操作 × 状态的组合链路，把代码里没人定义过的规则暴露成待确认问题。

## 安装

### 方式一：clone 到 skill 目录（推荐）

**OpenCode / Claude Code：**

```bash
git clone https://github.com/JK-yan/requirement-clarifier.git \
  ~/.config/opencode/skills/requirement-clarifier
```

其他平台请参照各自文档中的 skill 安装目录。

### 方式二：自动更新（可选）

Claude Code 和 OpenCode 原生不直接订阅 GitHub 仓库更新，可通过以下方式自动拉取最新版本。

#### A. Claude Code：使用 claude-skill-manager

```bash
git clone https://github.com/ashimoon/claude-skill-manager.git ~/.claude/skills/claude-skill-manager
```

在 Claude Code 中对话：

```text
Install this skill: https://github.com/JK-yan/requirement-clarifier
Update requirement-clarifier
Update all my skills
```

`claude-skill-manager` 会记住来源，每次执行 `Update ...` 时从 GitHub 拉取并让你审阅 diff。

#### B. OpenCode：使用 opencode-remote-config 插件

在 `~/.config/opencode/remote-config.json` 中添加：

```json
{
  "repositories": [
    {
      "url": "https://github.com/JK-yan/requirement-clarifier.git",
      "ref": "main",
      "skills": { "include": ["requirement-clarifier"] }
    }
  ]
}
```

安装并启用 `opencode-remote-config` 插件后，启动 OpenCode 会自动同步仓库更新。

#### C. 通用定时任务（不依赖插件）

```bash
# 安装 skill
git clone https://github.com/JK-yan/requirement-clarifier.git \
  ~/.config/opencode/skills/requirement-clarifier

# 每天 09:00 自动拉取更新
(crontab -l 2>/dev/null; echo "0 9 * * * cd ~/.config/opencode/skills/requirement-clarifier && git pull -q") | crontab -
```

### 方式三：导入 .skill 包

从 GitHub Releases 下载 `requirement-clarifier.skill` 文件，按各平台指引导入。

## 快速开始

在 Agent 对话中输入：

> "业务方说想加一个审批功能，让我理一下需求。"

Agent 会按 skill 指示：

1. 将原始需求归档到 `docs/requirements/raw/`
2. 对照 `docs/requirements/context.md` 翻译业务黑话
3. 读取盲区清单，产出可填写的问题清单
4. 你带回业务回答后，生成 `docs/requirements/specs/<功能>.md` 和最终确认单

## 工作模式

| 模式 | 触发语 | 输出 |
|---|---|---|
| A. 新需求澄清 | "帮我理一下这个需求" | 问题清单 + 开发规格 + 确认单 |
| B. 需求变更 | "业务说要改 XX" | 影响分析 + 更新规格 + 返工代价确认单 |
| C. 上下文维护 | "记一下，'单子'指采购单" | 更新 `context.md` |
| D. 链路审计 | "审计一下 XX 链路有没有坑" | 组合矩阵 + 问题清单 + 修复项 |

## 示例

### 新需求澄清

```text
用户：业务方在群里说"想加一个审批功能，越快越好"，让我把需求整理一下。

Agent（本 skill 触发后）：
1. 把聊天记录归档到 raw/2026-07-14-审批功能-聊天记录.md
2. 对照 context.md 确认"审批"在业务方语境中具体指什么
3. 产出问题清单：
   - 谁能发起审批？谁能审批？谁能看审批记录？
   - 审批不通过时，状态是"驳回"还是"打回修改"？
   - 是否需要支持多级审批？
   - 审批记录要保留多久？
4. 你带回业务回答后，生成 specs/审批功能.md 和确认单
```

### 需求变更

```text
用户：业务又说审批通过之后还要再加一个财务复核。

Agent：
1. 先判定变更来源是否与前一轮相同
2. 定位 specs/审批功能.md 中受影响的条目
3. 分析返工量
4. 生成变更确认单，让业务知情拍板
```

### 链路审计

```text
用户：帮我看看订单模块还有没有类似的坑。

Agent：
1. 盘点订单实体的状态、操作入口、不变量
2. 运行组合矩阵，检查七种缺陷模式
3. 技术加固类直接给修复项；规则未定义类转成业务问题清单
```

## 目录结构

```
requirement-clarifier/
├── SKILL.md                      # skill 主文件（触发规则 + 工作流）
├── scripts/
│   └── verify_evidence.py        # 证据核验 harness
├── references/
│   ├── blindspot-checklist.md    # 开发盲区检查清单
│   └── chain-audit-checklist.md  # 链路组合审计清单
├── templates/
│   ├── context-template.md       # 业务上下文模板
│   ├── spec-template.md          # 开发规格模板
│   ├── confirmation-template.md  # 最终确认单模板
│   └── questionnaire-template.md # 中途可填写确认单模板
├── LICENSE                       # PolyForm Noncommercial License
├── README.md                     # 本文件
├── CONTRIBUTING.md               # 贡献指南
└── CHANGELOG.md                  # 版本记录
```

## 打包与发布

### 本地打包

`.skill` 文件本质上是 zip 压缩包，可直接打包：

```bash
zip -r requirement-clarifier.skill . \
  -x ".git/*" ".github/*" "__pycache__/*" "*.pyc" ".DS_Store" ".gitignore"
```

打包前建议先运行校验脚本：

```bash
python3 scripts/validate_skill.py .
```

### GitHub Actions 自动发布

本仓库已配置 `.github/workflows/release.yml`。当你在 GitHub 创建一个新 Release 时，Actions 会自动：

1. 运行 `scripts/validate_skill.py` 校验 frontmatter。
2. 打包 `requirement-clarifier.skill`。
3. 把 `.skill` 文件上传到该 Release 的附件中。

使用步骤：

1. 推送代码到 GitHub。
2. 进入 **Releases** → **Draft a new release**。
3. 选择 tag（如 `v2.0.0`），填写标题和说明。
4. 发布后，Actions 会自动完成打包和上传。

## 证据纪律

所有引用来源的产出都应使用自证引用格式：

```markdown
> 证据: docs/requirements/raw/2026-07-14-prd.md:12 | "业务方原话片段"
```

交付前运行：

```bash
python3 scripts/verify_evidence.py <产出文件> --root .
```

在严格模式下，无主数值会判 FAIL：

```bash
python3 scripts/verify_evidence.py <产出文件> --root . --strict
```

## 许可证

本项目采用 [PolyForm Noncommercial License 1.0.0](LICENSE)。

- 允许学习、修改、个人使用、内部使用、非商业项目使用。
- **禁止用于商业目的**，包括但不限于作为付费服务、嵌入商业产品、用于商业工作流。

如需商用授权，请联系作者。

## 贡献

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

提交 PR 前请确保：

- 没有提交 `__pycache__/` 等不应进入仓库的文件。
- 脚本 `python3 scripts/verify_evidence.py --help` 能正常运行。
- 新增文件在 `SKILL.md` 的参考文件部分有引用。
