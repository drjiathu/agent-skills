---
name: python-wheel-release
description: "为使用 pyproject.toml 构建的 Python 项目准备、验证并发布可追溯的 wheel release。用于版本升级、发布前检查、创建 tag/GitHub Release、生成无远端本地 release、构建通用 wheel 或平台离线 bundle，以及核对版本、提交、CI、checksum 和发布资产。支持 GitHub 远端与完全无远端两种模式；不负责把制品部署到生产 systemd。"
---

# Python Wheel Release

## 核心合同

- 只发布来自一个已冻结、可复现定位的 Git commit 的制品。
- 版本、tag、wheel metadata、manifest 和 release 名称必须一致。
- 使用本轮产生的新鲜验证证据；历史日志和“应该成功”不算证据。
- 验证最终交付位置中的真实制品，不以本地临时构建结果代替。
- 不覆盖、移动或复用已发布的 tag 和资产；发现冲突时停止。
- 不把 credential、生产配置、内部地址或用户私有路径写入共享制品。
- 发布不等于部署。完成后输出明确的 release handoff，交给部署流程。

## 授权边界

- “检查、评估、设计、准备方案”仅允许只读检查和本地临时构建。
- “准备 release”允许修改版本、lock 和发布材料，但不自动 push、tag 或发布。
- “创建、发布、推送 release”才允许执行相应远端写操作。
- 需要改变分支策略、覆盖已有 ref、跳过检查或扩大制品范围时停止并请求用户决定。

## 工作流

1. 检查仓库和项目：确认 Git 根目录、工作树、`pyproject.toml`、版本来源、构建后端、lock、受支持 Python、现有分支、tag、发布文档和验证命令。
2. 检测发布模式：
   - 配置了 GitHub remote：完整阅读 [references/github-mode.md](references/github-mode.md)。网络或认证失败不等于无远端。
   - 完全没有 remote：完整阅读 [references/local-mode.md](references/local-mode.md)。
3. 始终完整阅读 [references/artifact-contract.md](references/artifact-contract.md)，确定本次制品集合和 handoff。
4. 冻结发布身份：记录项目、版本、目标 tag、完整 commit SHA、来源分支、Python、构建工具和目标平台。后续不得隐式重新解析为另一个提交。
5. 验证源码状态：按项目规则完成版本更新和分支整合，在精确提交上运行项目声明的全部必要检查。不要把任意一个绿色 workflow 当成完整 CI 证明。
6. 从干净源码重新构建。对 uv 项目优先使用 `uv build --no-sources`；不信任旧 `dist/`。检查 wheel 内容、metadata、入口点和不应包含的文件。
7. 在不引用源码树的新环境中安装制品，运行 import、`--help`、`--version`、依赖一致性和项目发布检查。
8. 按所选模式发布或归档，并验证最终位置中的资产、checksum、manifest 和 tag/commit 关系。
9. 输出 release handoff 和逐项验证证据；只有全部强制项通过才能声明 release 完成。

## 必须停止

- 工作树包含来源不明或会进入制品的未提交改动。
- 版本、tag、wheel metadata 或 manifest 不一致。
- 目标 tag 或 release 已存在。
- 必要检查缺失、未在精确提交上运行、仍在进行或失败。
- remote 已配置但不可访问，或默认分支/发布惯例无法可靠判断。
- 构建依赖未锁定、构建使用意外本地 source，或最终制品无法在干净环境安装。
- checksum、attestation、下载后资产或 Git bundle 验证失败。
- 生成的归档包含 credential、真实配置或非预期文件。

## 完成报告

至少报告：发布模式、版本、tag、完整 commit、制品路径、SHA-256、manifest、必要检查结果、最终资产验证结果，以及任何未执行或需人工完成的事项。不要仅报告命令已执行。
