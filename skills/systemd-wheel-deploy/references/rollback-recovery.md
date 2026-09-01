# 回滚与恢复合同

## 先分类回滚资格

部署前把变化分为：

1. 仅代码/依赖变化：通常可通过链接和 unit 回滚。
2. 配置 schema 变化：只有旧版本仍能读取当前配置时才能自动回滚。
3. credential 名称或协议变化：必须保留旧版本需要的安全映射。
4. 文件/消息/数据库格式变化：需要前后向兼容、快照或单独恢复计划。
5. 不可逆迁移或外部副作用：禁止宣称自动回滚。

如果无法证明兼容，部署可以在用户批准的维护方案下继续，但必须禁用“失败自动回滚”的承诺并先建立数据恢复点。

## 事务状态

在第一次生产变更前持久化一份不含秘密的事务记录：

```json
{
  "project": "project-name",
  "transaction_id": "timestamp-or-uuid",
  "phase": "quiesced",
  "from_version": "1.2.2",
  "to_version": "1.2.3",
  "release_commit": "full-sha",
  "artifact_sha256": "sha256",
  "current_before": "canonical-path",
  "previous_before": "canonical-path-or-null",
  "unit_backups": [],
  "timers_before": {},
  "checks": {},
  "started_at": "RFC3339"
}
```

每个关键阶段原子更新 `phase`。receipt 路径、owner 和 mode 应由项目部署合同决定；不放在可随 release 删除的目录。

## 自动回滚顺序

post-activation 检查失败且具备自动回滚资格时：

1. 保持相关 timers 暂停，防止新版本再次触发。
2. 将 `current` 原子恢复为捕获的旧 target。
3. 恢复旧 unit/drop-in 的精确内容、owner 和 mode。
4. 执行 `daemon-reload`。
5. 通过旧 release 的真实 systemd 上下文运行回滚检查。
6. 只有旧版本健康后才按基线恢复 timers。
7. 写失败 receipt，保留新 release 和诊断证据，不立即删除。

如果旧版本检查也失败，停止自动操作，保持调度暂停并报告双重故障；不要循环切换版本。

## 异常中断恢复

新部署开始前先查找未提交事务：

- `phase` 在 preflight/staged 且 `current` 未变：可以验证后安全重试或清理 inactive release。
- timers 已暂停但 `current` 未变：按记录恢复原 timer 状态，再决定是否重试。
- `current` 已变但未完成生产检查：先检查当前版本，不直接假设成功或失败。
- 外部人员修改了链接、unit 或 timer：停止，保留事务与备份，要求人工协调。

恢复只撤销仍等于本事务写入值的对象。若对象随后被外部修改，不覆盖这些新变化。

## previous 的语义

`previous` 是最近一次已知可运行的代码 release 指针，不是数据备份，也不是无限历史：

- 不允许指向不存在或未验证的目录。
- 当前版本成功后保留旧 target。
- 回滚成功后可以让 `current` 指回旧版本，但 receipt 必须保留失败版本身份。
- 新一轮部署开始前确认 `previous` 与历史 receipt 一致。

## 清理与灾难恢复

- 至少保留一个完整业务周期的旧 release；长任务应覆盖其最长运行周期。
- 清理 release 是独立、显式操作，先确认没有 symlink、unit 或运行中进程引用。
- `previous` 和本机旧目录不能替代异机制品备份。
- credential 不复制进 release 备份；单独按组织的 secret 恢复流程管理。
- 定期演练从 release 资产、非敏感配置模板和外部 credential 存储重建环境。

## 完成证据

回滚或恢复只有在以下证据齐全时才完成：

- `current` canonical target 正确。
- unit hashes 与目标版本合同一致。
- 旧版本生产检查成功。
- timers 恢复到记录的原状态。
- transaction receipt 已终结且明确结果。
- 数据或外部副作用的未恢复范围已单独报告。
