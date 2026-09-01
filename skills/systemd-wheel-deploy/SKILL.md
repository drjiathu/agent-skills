---
name: systemd-wheel-deploy
description: "将已验证的 Python wheel release 事务式部署、升级或回滚到使用 systemd timers 与 oneshot services 的 Linux 生产环境。用于 release 目录和私有 venv 安装、current/previous 符号链接切换、unit/timer/credential 部署、生产上下文健康检查、失败回滚和部署恢复。要求输入不可变制品或 release handoff；不负责创建代码 release。"
---

# Systemd Wheel Deploy

## 核心合同

- 只部署已验证的 release 制品，不从可变 Git checkout 直接运行生产服务。
- 在最终且尚未激活的 release 路径创建 venv；Python venv 不可搬移。
- 配置、credential、状态和数据留在 release 目录之外，不随代码切换。
- 每个有副作用的动作后立即验证，并预先定义失败处理。
- 切换前重新确认 `current`、unit 和 timer 状态未被外部修改。
- 只恢复部署前实际启用或运行的 timer，不能假设全部相同。
- 代码回滚不等于数据、数据库或不可逆配置回滚。
- 未通过真实 systemd 运行上下文检查，不得声明部署成功。

## 授权边界

- “检查、设计、给出部署步骤”只执行只读检查。
- “部署、升级、回滚生产”允许执行项目既定流程，但 sudo、credential 安装、删除 release 或不可逆数据操作仍按实际权限和风险处理。
- 不擅自停止无关服务、终止运行中任务、修改秘密值或扩大目标主机范围。

## Reference 路由

- 每次部署都完整阅读 [references/activation-contract.md](references/activation-contract.md)。
- 涉及 unit、timer、credential、挂载点或生产健康检查时，完整阅读 [references/systemd-runtime.md](references/systemd-runtime.md)。
- 存在自动回滚、数据格式变化、配置兼容性、异常中断或恢复需求时，完整阅读 [references/rollback-recovery.md](references/rollback-recovery.md)。

## 状态机

```text
INSPECT → PREFLIGHT → STAGE → VERIFY-STAGING → QUIESCE
        → REVALIDATE → ACTIVATE → VERIFY-PRODUCTION
                                  ├─ success → RESTORE-SCHEDULE → COMMIT
                                  └─ failure → ROLLBACK → VERIFY-ROLLBACK
                                                → RESTORE-SCHEDULE
```

## 工作流

1. 解析 release handoff 或 manifest，验证版本、commit、平台、checksum 和制品完整性；拒绝来源不明的目录或旧构建缓存。
2. 发现实际部署合同：应用用户、release 根目录、`current`/`previous`、console scripts、配置、credentials、units、timers、状态目录、数据目录、挂载点和健康检查。
3. 获取项目部署锁，记录部署基线：符号链接真实目标、unit hashes、timer enabled/active 状态、运行中 oneshot 和旧版本。
4. 执行只读 preflight：权限、空间、挂载、Python/平台、配置兼容性、credential 元数据和回滚资格。失败则不产生生产变更。
5. 在最终 inactive release 路径创建私有 venv，安装依赖和 wheel；不移动已创建的 venv。
6. 通过最终路径和生产等价 systemd 上下文运行 staging 检查。失败则保留现场供诊断或安全清理，不修改 `current`。
7. 按基线暂停准确的 timers；等待或明确处理运行中 oneshot。备份将变化的 unit，并在第一次生产变更前写事务状态。
8. 立即重新验证基线。若 `current`、unit 或 timer 被外部改变，停止且不覆盖现场。
9. 安装/验证 unit，原子更新 `previous` 和 `current`，执行 `daemon-reload`，再运行真实生产检查。
10. 成功时恢复原 timer 状态并写成功 receipt；失败时恢复旧链接和 unit、验证旧版本，再恢复原 timer 状态并写失败 receipt。

## 必须停止

- release handoff、checksum、平台或版本验证失败。
- 当前生产状态与开始时记录的基线不一致。
- 目标 release 已存在但内容或 manifest 不同。
- 外部数据盘/NAS 未按预期挂载，或目标路径落到错误文件系统。
- 存在运行中任务且安全处理方式未定义。
- 新旧配置、credential 名称、数据格式或数据库变更不具备已证明的回滚兼容性。
- staging 或 post-activation 检查失败且旧版本也无法恢复健康。
- 无法确定哪些 timers 应恢复，或部署事务处于未解决的中间状态。

## 完成报告

至少报告：旧/新版本、commit、制品 SHA-256、`current`/`previous` 最终目标、unit 与 timer 状态、staging 和生产检查结果、receipt 位置、回滚资格及遗留事项。完成声明必须附带本轮真实命令证据。
