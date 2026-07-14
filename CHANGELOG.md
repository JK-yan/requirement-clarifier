# Changelog

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
