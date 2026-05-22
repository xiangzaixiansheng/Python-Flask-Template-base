# CI/CD 持续集成指南

## 概述

项目使用 GitHub Actions 实现自动化 CI（持续集成）。每次代码推送或 PR 时，自动执行代码检查和测试，确保代码质量。

## 配置文件位置

```
.github/workflows/ci.yml
```

## 触发条件

| 事件 | 分支 | 说明 |
|------|------|------|
| push | main | 推送到 main 分支时自动触发 |
| pull_request | main | 向 main 发起 PR 时自动触发 |

## 流水线步骤

```
┌─────────────────┐
│  Checkout Code  │  拉取仓库代码
└────────┬────────┘
         ▼
┌─────────────────┐
│  Setup Python   │  安装 Python 3.10 + pip 缓存
└────────┬────────┘
         ▼
┌─────────────────┐
│  Install Deps   │  安装 requirements-dev.txt
└────────┬────────┘
         ▼
┌─────────────────┐
│     Lint        │  flake8 代码风格检查
└────────┬────────┘
         ▼
┌─────────────────┐
│   Run Tests     │  pytest + 覆盖率 ≥ 30%
└────────┬────────┘
         ▼
┌─────────────────┐
│ Upload Coverage │  上传覆盖率报告
└─────────────────┘
```

## 配置详解

```yaml
name: CI                          # Action 名称，显示在 GitHub 页面

on:                               # 触发条件
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:                           # Job 名称
    runs-on: ubuntu-latest        # 运行环境 (GitHub 提供的免费虚拟机)

    env:                          # 环境变量 (测试无需真实数据库)
      FLASK_ENV: testing
      KEY: test-ci-secret-key

    steps:
      - uses: actions/checkout@v5           # 拉取代码

      - uses: actions/setup-python@v5       # 安装 Python
        with:
          python-version: '3.10'
          cache: 'pip'                      # 缓存依赖加速

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Lint                          # 代码规范检查
        run: |
          flake8 app/ tests/ --count --show-source --statistics

      - name: Run tests                     # 测试 + 覆盖率
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=30

      - name: Upload coverage               # 上传报告
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: coverage.xml
          if-no-files-found: ignore
```

## 关键概念

| 概念 | 说明 | 示例 |
|------|------|------|
| `on` | 触发时机 | push、pull_request、schedule (定时)、workflow_dispatch (手动) |
| `jobs` | 任务组 | 可定义多个 job，默认并行执行 |
| `runs-on` | 运行环境 | ubuntu-latest、macos-latest、windows-latest |
| `steps` | 执行步骤 | 一个 job 内按顺序执行 |
| `uses` | 引用 Action | 类似插件，别人写好的可复用步骤 |
| `run` | Shell 命令 | 直接执行命令行 |
| `env` | 环境变量 | 可在 job 级或 step 级设置 |
| `if` | 条件执行 | `if: always()` 无论前面成功失败都执行 |

## 相关配置文件

| 文件 | 作用 |
|------|------|
| `.flake8` | flake8 代码检查规则 (行宽 120、忽略的错误码) |
| `pyproject.toml` | pytest / black / isort / coverage 配置 |
| `requirements-dev.txt` | CI 需要安装的开发依赖 |

## 查看结果

1. 进入 GitHub 仓库 → **Actions** 标签页
2. 点击具体的 workflow run 查看详细日志
3. 绿色 = 通过，红色 = 失败
4. 覆盖率报告可在 Artifacts 区域下载

## 常见扩展

### 多版本矩阵测试

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

### 自动部署 (CD)

```yaml
deploy:
  needs: test                   # 依赖 test job 通过
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to server
      run: |
        ssh user@server 'cd /app && git pull && make install && systemctl restart app'
```

### 定时执行

```yaml
on:
  schedule:
    - cron: '0 2 * * *'         # 每天凌晨2点跑一次
```

### 手动触发

```yaml
on:
  workflow_dispatch:             # 在 GitHub 页面手动点击触发
    inputs:
      environment:
        description: '部署环境'
        required: true
        default: 'staging'
```

### 失败通知

```yaml
- name: Notify on failure
  if: failure()
  run: |
    curl -X POST "https://hooks.slack.com/..." \
      -d '{"text": "CI 失败: ${{ github.repository }}"}'
```

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| Lint 失败 | 代码不符合 flake8 规则 | 本地跑 `make lint` 修复后再提交 |
| Tests 失败 | 测试用例不通过 | 本地跑 `make test` 排查 |
| 覆盖率不足 | 新代码未写测试 | 补充测试或调整阈值 |
| 依赖安装失败 | requirements.txt 有问题 | 检查包名和版本号 |
| Actions 废弃警告 | 使用了旧版本 Action | 升级 @v4 到 @v5 |
