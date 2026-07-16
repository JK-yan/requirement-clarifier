# Changelog

## [2.0.0] - 2026-07-16

### Changed

- 同步 skill 核心文件到 v2.0：重构并精简 `SKILL.md` 正文，将铁律升级为"五条铁律"。
- 持久文件结构增加 `parking.md`（需求停车场）。
- `references/chain-audit-checklist.md` 新增 sub-agent 探索回收契约，要求子代理必须带回 `file:line + 原文片段`。
- `scripts/verify_evidence.py` 增加 `【假设·未取证】` 标签识别。
- `templates/questionnaire-template.md` 新增出题规则（依赖剪枝、建议选项分级）。
- 更新 `SKILL.md` frontmatter 版本号为 `2.0.0`。

## [1.12.0] - 2026-07-14

### 初始开源版本

- 将 requirement-clarifier skill 开源到 GitHub。
- 采用 PolyForm Noncommercial License 1.0.0（非商用许可证）。
- 包含核心工作流：新需求澄清、需求变更、上下文维护、链路审计。
- 新增 `scripts/validate_skill.py` 用于 frontmatter 校验。
- 新增 `.github/workflows/release.yml`，发布时自动打包 `.skill` 文件并上传到 GitHub Release。
- 包含盲区检查清单与链路审计清单。
- 包含开发规格、确认单、问卷、上下文模板。
- 明确声明支持所有兼容 OpenCode / Claude Code skill 规范的 AI Agent 平台。
