# GitHub 发布模式

## 适用条件

仅在仓库配置了 GitHub remote 时使用本模式。先确认 remote URL、仓库身份、默认分支和认证状态。remote 存在但暂时不可达时停止；不要改走本地无远端流程。

## 发布前发现

检查以下事实，不从项目名称或个人习惯推断：

- 默认分支及 develop/release 分支策略。
- 最近的 tag、Release 标题、notes 和资产命名。
- 项目版本的唯一来源及 lock 更新方式。
- 分支保护或 ruleset 声明的必要检查。
- tag workflow 的触发条件、权限和已有并发控制。
- Release 是否启用 immutable releases。

如果历史惯例互相冲突，列出候选方案并停止请求决定。

## 精确提交门禁

先冻结完整 `release_commit`，随后所有检查、tag 和构建都绑定它。必要门禁应按名称列出，不能使用“至少有一个绿色 workflow”。

验证每个必要检查：

- 确实针对 `release_commit`。
- 已完成且结论为成功。
- `skipped`、`neutral`、`stale`、`action_required` 或缺失不作为通过证明。
- 列表不能因默认分页或过小 limit 被静默截断。
- tag push 产生的重复跳过任务，不能替代该 SHA 上原有的成功测试。

如果 ruleset 已定义 required checks，以它为优先事实来源；否则从仓库 CI 文档和 workflow 建立明确清单，并向用户暴露该清单。

## Workflow 安全合同

审查或生成发布 workflow 时：

- 所有第三方 Actions 固定到完整 commit SHA，并在注释中保留语义版本。
- 默认 `permissions: contents: read`，只在需要发布的 job 提升最小权限。
- 不需要 Git push 时为 checkout 设置 `persist-credentials: false`。
- 固定 uv/Python 版本，不依赖隐式 latest。
- 为发布设置唯一 concurrency group；发布运行不应互相取消或覆盖。
- build job 不接收不必要的 release 写权限或生产 credential。
- tag 必须与项目版本一致且指向已验证的默认分支提交。
- 已存在的 tag、Release 或资产一律失败，不使用 force、clobber 或重打 tag。

## 创建 Release

推荐顺序：

1. 在默认分支精确提交上完成全部门禁。
2. 从干净 checkout 构建新制品和 checksums。
3. 创建 draft release。
4. 一次性上传完整资产并核对文件名、大小和 SHA-256。
5. 生成或关联 provenance/attestation（仓库支持时）。
6. 最后发布 draft，使 immutable release 能一次锁定完整资产集合。

不要把 GitHub 自动生成的 source zip/tarball 当成项目自定义离线 bundle，也不要依赖它保存自定义文件权限。

## 最终验证

发布后重新查询 GitHub，而不是只相信上传命令的退出码：

- tag 指向 `release_commit`。
- Release 已发布且不是意外 prerelease/draft。
- 资产集合和 manifest 完全匹配，没有缺失或额外文件。
- 使用 `gh release verify` 和 `gh release verify-asset`（功能可用时）验证 immutable release 及本地下载资产。
- 否则重新下载资产，按已发布 `SHA256SUMS` 校验。
- Release notes 描述真实变更，不编造功能或测试结果。

将仓库、Release URL、workflow run、tag、commit 和下载后 checksum 写入 handoff。
