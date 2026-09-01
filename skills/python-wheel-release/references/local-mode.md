# 无远端本地发布模式

## 适用条件

只有 `git remote` 完全为空时才使用本模式。已配置 remote 的认证失败、DNS 故障、网络中断或 GitHub 不可用不构成无远端仓库。

本地发布的目标是同时得到：

- 默认分支上的明确 release commit。
- 不可移动的 annotated tag。
- 可安装的 release 制品与 checksum。
- 可恢复完整可达 Git refs 的 Git bundle。
- 位于另一块磁盘或另一台主机的独立副本。

## 分支与版本顺序

先发现仓库实际分支策略。如果同时存在 `develop` 和 `main` 且项目没有相反规则，使用：

1. 在干净 `develop` 更新项目版本和 lock。
2. 运行必要检查并提交版本变更。
3. 将 `develop` 按仓库既定 merge 策略整合进 `main`，不发明新的 merge 方式。
4. 在新的 `main` 提交上重新运行必要检查。
5. 冻结完整 commit SHA，创建 annotated release tag。
6. 从该 tag/commit 的干净源码构建制品。

如果仓库没有 `develop`、没有 `main`、处于 detached HEAD 或分支历史已分叉，不要擅自创建或重写分支；先报告实际状态并取得决定。

## Tag 合同

- 使用 annotated tag 保存 tagger、日期和 release 说明。
- 项目已具备可靠签名配置时可以创建 signed tag，但不临时生成或搬运签名密钥。
- tag 名必须与项目版本一致并明确指向冻结提交。
- tag 已存在时停止；不 force retag。
- tag 后若发现错误，发布一个新的修订版本，而不是复用原 tag 名。

## Git 备份

在工作树干净且 tag 已确认后创建完整 bundle，例如：

```text
git bundle create <project>-<tag>.bundle --all
git bundle verify <project>-<tag>.bundle
```

`--all` 备份所有可达 refs 和对象，但不包含未提交工作树、index、stash、仓库配置、hooks 或 Git 之外的数据。因此：

- 创建前必须处理未提交状态。
- 单独保存 release 制品、manifest、checksums 和必要的非敏感运维模板。
- credential 和真实生产配置不进入 bundle 或 release 包。

## 独立副本

本机上的 Git 仓库、release bundle 和 `current` 目录不构成灾难恢复。至少将以下文件复制到独立故障域：

```text
<project>-<tag>.bundle
<project>-<tag>-<platform>.tar.gz（若有）
wheel
RELEASE.json
SHA256SUMS
```

复制完成后在目标位置重新验证 checksum 和 `git bundle verify`。未完成独立副本时，可以报告“本地制品已生成”，但不能报告“本地 release 已具备恢复能力”。

## 恢复演练

首次采用本模式或备份格式变化时，在临时目录执行一次：

- 从 Git bundle clone。
- 检查 release tag 和 commit。
- 校验 release 制品。
- 在干净环境安装 wheel 并运行基本入口。

恢复演练不得覆盖当前工作仓库或生产 release。
