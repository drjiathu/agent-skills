# systemd 运行时合同

## Unit 发现与验证

检查仓库候选 unit 与主机已安装 unit 的有效合并结果，包括 drop-in。至少验证：

- `User=`、`Group=`、`WorkingDirectory=`。
- `ExecStart=` 指向 `current/.venv/bin/<console-script>`。
- `EnvironmentFile=`、`LoadCredential=` 和目录生命周期。
- `Type=oneshot`、timeout、restart 策略和退出码传播。
- timer 的 `OnCalendar=`、时区、`Persistent=`、`AccuracySec=`、随机延迟和目标 unit。

使用 `systemd-analyze verify` 检查 unit 语法，使用 `systemd-analyze calendar` 验证日历表达式。不要以语法通过替代实际运行检查。

## Credential

- 敏感值通过 `LoadCredential=`/`LoadCredentialEncrypted=` 或项目既定安全接口提供。
- 应用从 `$CREDENTIALS_DIRECTORY` 中的命名文件读取，不硬编码 `/run/credentials/<unit>`。
- 不在 unit、EnvironmentFile、命令参数、release bundle、部署 receipt 或日志中记录明文。
- preflight 只检查 credential 文件存在性、owner、mode、unit 映射和应用可解析性，不打印内容。
- credential 名称变化属于部署合同变化；旧版本回滚需要的映射必须仍然可用。

## 数据与挂载

对 SSD、NAS、网络文件系统或单独数据盘：

- 验证路径位于预期 mount，而不只是目录存在。
- 验证文件系统类型、可用空间、owner 和应用用户读写能力。
- 合适时在 unit 使用 `RequiresMountsFor=` 建立启动依赖。
- 即使配置了 `RequiresMountsFor=`，production check 仍确认实际 mount，防止数据写入系统盘上的空挂载目录。

只读检查不得创建大文件；需要写权限探测时使用项目批准的微小临时文件并确保清理。

## 生产等价检查

staging check 应通过 transient unit 或与正式 unit 等价的 systemd 上下文运行，覆盖：

- 实际 User/Group。
- 最终 release WorkingDirectory 和 console script。
- EnvironmentFile。
- RuntimeDirectory/StateDirectory。
- 与目标实例相同的 credentials。
- mount、代理和网络可达性。

健康检查应尽量非破坏性。若检查会写数据库、覆盖文件或触发业务通知，必须提前说明并取得相应授权。

## Hardening

运行 `systemd-analyze security` 作为审计输入，逐项评估：

```text
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=
ReadOnlyPaths=
ReadWritePaths=
RestrictSUIDSGID=true
```

不要为了分数盲目启用。先列出应用真正需要读取、写入和联网的资源，再逐项收紧并通过正式检查验证。

## Timer 状态

部署前为每个确切 timer 保存：

```text
LoadState
UnitFileState
ActiveState
SubState
NextElapseUSecRealtime
```

恢复规则：

- 原来 enabled 且 active：恢复 enabled/active。
- 原来 enabled 但 inactive：不要擅自 start。
- 原来 disabled：保持 disabled。
- 原来 masked：保持 masked，除非本次变更明确解除并获授权。
- 新增 timer：作为显式发布变化单独确认。

不要用宽泛 glob 操作其他项目 unit。

## Journald 验收

检查本次 invocation 的日志和 unit 结果，而不是被历史成功记录误导：

- `Result`、`ExecMainStatus` 与退出码一致。
- oneshot 成功后 `inactive/dead` 可以是正常状态。
- 日志包含版本、任务和脱敏结果，不包含 credential 或完整请求对象。
- 失败 unit 是否需要 `reset-failed` 由运维语义决定；清除 failed 状态不等于任务成功。
