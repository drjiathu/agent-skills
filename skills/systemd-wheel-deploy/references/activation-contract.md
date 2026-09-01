# Release 激活合同

## 发现而非硬编码

从仓库部署文档、unit、release manifest 和当前主机只读状态发现：

- 应用用户和组。
- 应用根目录、`releases/`、`current`、`previous`。
- Python 版本和 console scripts。
- 配置、credential、状态、日志和数据路径。
- unit、timer、drop-in 与健康检查。
- 外部挂载和网络依赖。

共享 skill 不固定用户名、`/home` 路径、项目名或 unit 名。发现结果必须在第一项生产变更前展示。

## Release 目录

推荐布局：

```text
<app-root>/
├── releases/
│   ├── <old-version>/
│   └── <new-version>/
├── current -> releases/<active-version>
└── previous -> releases/<rollback-version>
```

在最终 `<new-version>` 路径创建 `.venv`，可用私有标记文件表示尚未激活。不要在临时目录创建 venv 后移动整个目录，因为 console script shebang 和 venv 配置包含绝对路径。

目标 release 已存在时：

- manifest 和所有 hashes 完全一致：可作为幂等重试候选，但仍重新检查。
- 任一内容不同：停止，不覆盖原目录，也不把同一版本解释为新制品。

## 部署基线

获取项目级部署锁后记录：

- `current` 和 `previous` 的链接文本与 canonical target。
- 将要覆盖的 unit/drop-in 的路径、owner、mode 和 SHA-256。
- 每个相关 timer 的 enabled、active 和 next 状态。
- 相关 oneshot 的 ActiveState/SubState/MainPID。
- 当前 release manifest 和生产检查状态。

在切换前立即重新读取。任何外部变化都使本次基线失效；停止并保留现场，不猜测谁的修改应获胜。

## Staging 安装

1. 校验制品后再解包；先检查路径穿越和非预期文件。
2. 创建目标 release 目录、owner 和严格权限。
3. 在最终路径创建私有 venv。
4. 在线模式按标准 lock 安装；离线模式只从 wheelhouse 按 hashes 安装。
5. 使用 `--no-deps` 安装应用 wheel（依赖已由 lock 同步时）。
6. 运行依赖检查、import、console script `--help`/`--version`。
7. 确认输出版本等于 manifest，且解释器/entry point 均位于新 release。

systemd 运行时直接调用 venv 内 console script，不调用 uv，也不依赖激活 shell。

## Quiesce

- 只暂停与本次应用相关且部署前处于 active 的 timers。
- 保存 enabled 与 active 的区别；`disable`、`stop` 和 `mask` 不是同义操作。
- 等待已运行 oneshot 自然结束，除非用户明确授权且项目定义了安全中断协议。
- 设置合理等待上限；超时后停止，不在未知写入状态切换代码。

## 原子激活

在同一文件系统和符号链接所在目录内创建临时链接，再使用原子 rename 替换：

1. 将 `previous` 指向部署开始时捕获的旧 `current` target。
2. 将 `current` 指向完整的新 release 目录。
3. 立即验证两个 canonical targets。
4. 安装并校验 unit 后执行 `daemon-reload`。
5. 运行正式 post-activation checks。

不要让 `current` 暂时不存在，也不要修改旧 release 内容。

## 成功提交

- 删除“未激活”标记，写部署 receipt。
- 按部署前状态恢复 timer，不额外启用新 timer，除非本次发布明确新增且用户已授权。
- 观察一次必要的运行或执行非破坏性烟雾检查。
- 至少保留旧 release 一个完整业务周期；清理属于独立操作，不在部署成功后立即执行。
