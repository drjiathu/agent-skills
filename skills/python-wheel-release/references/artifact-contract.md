# Release 制品合同

## 制品层次

根据项目需要选择，不要假定所有项目都需要离线 bundle：

1. 通用 wheel：纯 Python 项目通常为 `py3-none-any.whl`，具体兼容性仍由 metadata 与依赖决定。
2. 标准 lock 导出：例如 `pylock.toml`，用于其他平台在线解析和可复现安装。
3. 平台离线 bundle：只承诺 manifest 中声明的 OS、架构和 Python，包含应用 wheel、带 hash 的依赖清单、binary wheelhouse 和非敏感部署材料。

## 必需文件

一次 release 至少包含：

```text
application wheel
RELEASE.json
SHA256SUMS
```

项目声明通用安装或离线安装时，再分别增加 lock 导出或平台 bundle。checksum 文件自身的信任来自 GitHub immutable release/attestation、签名渠道或独立可信传输，不能循环地只校验自身。

## RELEASE.json

manifest 至少记录：

```json
{
  "project": "project-name",
  "version": "1.2.3",
  "tag": "v1.2.3",
  "commit": "full-git-sha",
  "source_branch": "main",
  "python": "3.13.9",
  "build_tool": "uv 0.x.y",
  "build_backend": "backend and version range",
  "platform": "any or explicit target",
  "build_time_utc": "RFC3339 timestamp",
  "lock_sha256": "sha256 or null",
  "artifacts": {
    "artifact-name": "sha256"
  }
}
```

不要通过手工重复输入生成互相矛盾的字段。优先从 Git、project metadata、实际构建工具和最终文件计算。部署时以 manifest 为发布身份来源，但仍独立核对 wheel metadata 和 checksum。

## Wheel 验证

- 文件名、`METADATA` 版本和 console entry points 与项目声明一致。
- wheel 可在不引用源码树的新环境安装、导入并运行 `--help`/`--version`。
- `pip check` 或等价依赖检查通过。
- wheel 不包含测试数据、notebook、开发配置、credential、systemd unit、部署脚本或本地状态，除非项目明确把某类非敏感资源定义为包数据。
- 不使用 editable install 作为发布验证。
- 对 uv 项目用 `uv build --no-sources` 发现本地 source 注解依赖。

## 离线 bundle 验证

- 目标平台、架构和 Python 必须写入文件名与 manifest。
- wheelhouse 只包含目标环境需要的文件；要求 binary-only 时不得混入 sdist。
- 依赖清单固定版本并包含每个安装文件的 hash。
- 在禁用网络的干净目标 Python 环境完成一次安装演练。
- 归档内所有相对路径规范化，禁止绝对路径、`..` 穿越和指向归档外的链接。
- 部署材料可以包含 unit/templates，但不能包含生产 credential 或真实 `settings.toml`。

## Release handoff

向部署流程输出结构化信息：

```text
project:
version:
tag:
commit:
release_mode: github | local
artifact_path_or_url:
artifact_sha256:
manifest_path:
platform:
source_verification:
required_checks:
final_asset_verification:
```

handoff 缺少 commit、SHA-256、manifest 或最终资产验证时，部署 skill 应拒绝自动激活。
