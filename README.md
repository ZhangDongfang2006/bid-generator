# 海越湖北电气 - 投标文件自动生成系统

> 基于AI的智能投标文件生成工具

[![GitHub Stars](https://img.shields.io/badge/Stars-yellow?style=flat-square)](https://github.com/ZhangDongfang2006/bid-generator)
[![License](https://img.shields.io/badge/License-Internal%20Use-red?style=flat-square)](#)

---

## 📋 目录

- [快速开始](#快速开始)
- [系统功能](#系统功能)
- [程序架构](#程序架构)
- [技术栈](#技术栈)
- [Git 工作流程](#git-工作流程)
- [GitHub 优势功能](#github-优势功能)
- [其他同事如何使用](#其他同事如何使用)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 快速开始

### 数据保护说明

**重要**：本项目默认使用示例数据进行演示，真实公司数据不会被提交到代码仓库。

### 数据模式

| 模式 | 说明 | 数据来源 | 适用场景 |
|------|------|----------|----------|
| **DEMO（示例数据）** | 默认模式，使用演示数据 | `data/examples/` 目录 | 开源分享、演示测试 |
| **PRODUCTION（真实数据）** | 使用真实公司数据 | `/data/` 目录（本地） | 你个人或内部服务器使用 |

### 如何切换数据模式

#### 方式1：使用真实数据（不分享代码时）

不需要做任何操作！只要不设置环境变量，系统就会默认加载 `/data/` 目录的真实数据。

#### 方式2：使用示例数据（开源分享时）

```bash
export USE_DEMO_DATA=true
streamlit run app.py
```

或者在 `.env` 文件中添加：
```bash
USE_DEMO_DATA=true
```

### 安全机制

1. **`.gitignore` 配置**
   - `/data/` 目录已被忽略，真实数据不会提交到 Git
   - 只有 `/data/examples/` 目录的示例数据会被提交

2. **环境变量控制**
   - 不设置 `USE_DEMO_DATA` → 使用真实数据（本地）
   - 设置 `USE_DEMO_DATA=true` → 使用示例数据（演示）

3. **启动时提示**
   系统启动时会显示当前使用的数据模式：
   ```
   =============================================================
   📊 数据模式：示例数据（DEMO）
   ✓ 当前使用示例数据进行演示
   ✓ 不会加载真实公司数据

   💡 如需使用真实数据，请设置环境变量：
      export USE_DEMO_DATA=false
   =============================================================
   ```

---

### 第一次使用（安装）

```bash
# 进入项目目录
cd ~/workspace/bid-generator

# 运行安装脚本
./setup.sh
```

### 日常使用（启动）

#### 单人使用
```bash
./setup.sh
```

#### 多人共用（局域网）
```bash
./start_lan.sh
```

启动后访问：`http://localhost:8501`

---

## 系统功能

### 核心功能
- 📄 **自动解析**：支持PDF和Word格式的招标文件
  - PDF 文件解析（PyPDF2）
  - Word (.docx) 文件解析（python-docx）
  - Word (.doc) 文件解析（antiword 自动转换为 .docx）

- 🔗 **智能匹配**：自动匹配公司资质、案例、产品
  - 基于关键词的智能匹配
  - 支持模糊匹配和分类筛选

- 📊 **资料管理**：统一管理公司数据库
  - 资质证书管理（含图片转换）
  - 项目案例管理
  - 产品信息管理
  - 人员信息管理

- 🚀 **快速生成**：一键生成投标文件（Word格式）
  - 技术标和商务标分开生成
  - 证书图片自动插入
  - 格式规范化

- 💾 **本地部署**：数据安全，本地运行
  - 无需联网即可使用
  - 数据存储在本地
  - 支持局域网共享

### 已加载资料

| 类别 | 数量 | 说明 |
|------|------|------|
| 资质证书 | 64项 | 含质量、环境、安全、能源认证及型式试验报告等 |
| 产品信息 | 15项 | 高低压开关柜、预制舱等 |
| 业绩案例 | 20项 | 覆盖14个行业，2019-2025年 |
| 人员信息 | 待更新 | 需补充人员资料 |

---

## 程序架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Web 界面层 (app.py)                    │
│                  Streamlit 应用入口                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ 解析模块     │ │ 生成模块  │ │ 数据库模块   │
│ (parser.py)  │ │(generator│ │ (database.py)│
│              │ │   .py)   │ │              │
└──────────────┘ └──────────┘ └──────────────┘
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ PDF/Word     │ │ Word     │ │ JSON 数据库  │
│ 文件解析     │ │ 文档生成 │ │ (data/*.json) │
└──────────────┘ └──────────┘ └──────────────┘
        │            │
        ▼            ▼
┌──────────────┐ ┌──────────┐
│ Ghostscript  │ │ python-  │
│ (PDF转图片)  │ │ docx     │
└──────────────┘ └──────────┘
```

### 核心模块说明

#### 1. app.py - Web 应用入口
- **功能**：Streamlit 应用主程序，提供 Web 界面
- **主要功能**：
  - 文件上传和解析
  - 资料管理界面
  - 投标文件生成
  - 调试模式

#### 2. parser.py - 招标文件解析模块
- **功能**：解析 PDF 和 Word 格式的招标文件
- **主要方法**：
  - `parse_file(filepath)` - 主解析方法
  - `_parse_pdf(filepath)` - PDF 文件解析
  - `_parse_docx(filepath)` - Word (.docx) 文件解析
  - `_parse_doc(filepath)` - Word (.doc) 文件解析（转换为 .docx）
- **依赖**：PyPDF2, python-docx, antiword

#### 3. generator.py - 投标文件生成模块
- **功能**：生成 Word 格式的投标文件
- **主要方法**：
  - `generate_bid()` - 生成单一投标文件
  - `generate_separate_bids()` - 生成技术标和商务标分开的文件
  - `_add_qualifications_with_pdf_images()` - 添加证书图片
- **依赖**：python-docx, pdf2image, Pillow

#### 4. database.py - 数据库管理模块
- **功能**：管理公司资质、案例、产品、人员数据
- **主要方法**：
  - `get_qualifications()` - 获取资质证书列表
  - `get_cases()` - 获取项目案例列表
  - `get_products()` - 获取产品信息列表
  - `get_personnel()` - 获取人员信息列表
  - `match_qualifications(requirements)` - 智能匹配资质
- **数据存储**：JSON 文件（data/qualifications.json 等）

#### 5. pdf_to_image_service.py - PDF 转图片服务
- **功能**：将 PDF 文件转换为图片
- **主要方法**：
  - `convert_pdf_to_images()` - 批量转换 PDF
- **依赖**：pdf2image, Pillow, Ghostscript, poppler

### 数据流

```
用户上传招标文件
    ↓
parser.py 解析文件内容
    ↓
database.py 智能匹配资质、案例、产品
    ↓
generator.py 生成 Word 文档
    ↓
pdf_to_image_service.py 转换证书为图片（如需要）
    ↓
插入图片到文档
    ↓
用户下载生成的投标文件
```

---

## 技术栈

### 后端框架
- **Streamlit**：Web 应用框架
- **Python**：3.9+

### 核心库
- **PyPDF2**：PDF 文件解析
- **python-docx**：Word (.docx) 文件读写
- **antiword**：Word (.doc) 文件转换
- **pdf2image**：PDF 转图片
- **Pillow**：图片处理

### 工具
- **Ghostscript**：PDF 处理引擎
- **poppler**：PDF 渲染库

### 版本控制
- **Git**：版本控制
- **GitHub**：代码托管
- **GitHub CLI**：命令行工具

---

## Git 工作流程

### 推荐工作流程

#### 1. 开发新功能前
```bash
# 拉取最新代码
git pull origin main

# 创建新分支
git checkout -b feature/新功能名称
```

#### 2. 开发中
```bash
# 查看修改
git status

# 暂存修改的文件
git add 文件名

# 提交修改
git commit -m "类型: 简短描述

详细说明本次修改的目的和内容

- 修改1
- 修改2

相关 Issue: #123"

# 推送分支到远程
git push -u origin feature/新功能名称
```

#### 3. 完成后
```bash
# 切换回主分支
git checkout main

# 合并分支
git merge feature/新功能名称

# 推送到远程
git push origin main

# 删除本地分支
git branch -d feature/新功能名称

# 删除远程分支
git push origin --delete feature/新功能名称
```

### Commit 消息规范

使用以下前缀标识提交类型：

| 前缀 | 说明 | 示例 |
|------|------|------|
| `feat:` | 新功能 | `feat: 添加证书图片显示功能` |
| `fix:` | 修复问题 | `fix: 修复 pdf2image 参数错误` |
| `docs:` | 文档更新 | `docs: 更新 README.md` |
| `style:` | 代码格式 | `style: 统一代码缩进` |
| `refactor:` | 重构 | `refactor: 优化数据库查询逻辑` |
| `perf:` | 性能优化 | `perf: 减少 PDF 解析时间` |
| `test:` | 测试相关 | `test: 添加证书转换测试` |
| `chore:` | 构建/工具 | `chore: 更新依赖库` |

### 更新日志

每次重要更新后，更新 `CHANGELOG.md`：

```markdown
## [版本号] - YYYY-MM-DD

### 新增 ✨
- 新功能描述

### 优化 🚀
- 优化描述

### 修复 🐛
- 修复描述

### 依赖 🔧
- 依赖变更
```

### 版本号发布

```bash
# 更新版本号（在相关文件中）
git commit -am "release: 发布版本 x.y.z"
git tag -a v.x.y.z -m "版本说明"
git push --tags
```

---

## GitHub 优势功能

### 1. Issues（问题追踪）
**用途**：追踪 bug、功能请求、任务

**示例**：
```markdown
**标题**：修复证书图片不显示问题

**问题描述**：
生成的投标文件中没有显示证书图片

**复现步骤**：
1. 上传招标文件
2. 勾选"显示证书图片"选项
3. 生成投标文件
4. 打开文档查看

**期望行为**：
证书图片应该显示在第3章（企业资质）

**实际行为**：
没有显示任何图片

**环境信息**：
- 系统：macOS
- Python 版本：3.9
- 相关依赖：pdf2image 1.17.0, Pillow 9.0.0

**附加信息**：
截图、日志文件等
```

**使用命令**：
```bash
# 创建 Issue
gh issue create --title "标题" --body "描述"

# 列出 Issues
gh issue list

# 查看 Issue
gh issue view 123
```

### 2. Pull Requests（PR）
**用途**：代码审查、合并分支

**使用命令**：
```bash
# 创建 PR
gh pr create --title "标题" --body "描述"

# 列出 PRs
gh pr list

# 查看和合并 PR
gh pr view 123
gh pr merge 123 --merge
```

### 3. Actions（CI/CD）
**用途**：自动化测试、部署

**推荐工作流**：
- 自动运行测试
- 代码质量检查
- 自动部署

**配置文件**：`.github/workflows/ci.yml`

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/
```

### 4. Projects（项目管理）
**用途**：看板管理、任务跟踪

**推荐使用场景**：
- 待办事项
- 进行中的任务
- 已完成的任务
- 功能规划

### 5. Wiki（文档）
**用途**：详细文档、教程

**推荐文档**：
- 部署指南
- 开发指南
- API 文档
- 常见问题

### 6. Releases（版本发布）
**用途**：发布版本、下载安装包

**使用命令**：
```bash
# 创建 Release
gh release create v1.0.0 --notes "版本说明"

# 列出 Releases
gh release list
```

### 7. GitHub Pages（静态网站）
**用途**：托管项目网站、文档

**配置**：
1. 在 `Settings` → `Pages` 中启用
2. 选择分支（如 `gh-pages`）
3. 访问 `https://zhangdongfang2006.github.io/bid-generator/`

### 8. Security（安全）
**用途**：
- Dependabot（依赖安全提醒）
- Code scanning（代码扫描）
- Secret scanning（密钥扫描）

**推荐设置**：
- 启用 Dependabot 自动更新依赖
- 配置 Secret scanning 防止密钥泄露

---

## 其他同事如何使用

### 方案1：单机使用（每人独立）

每个同事在自己的电脑上安装一套系统：

1. 获取项目文件包（联系项目负责人）
2. 解压到本地目录
3. 运行 `./setup.sh` 安装
4. 日常使用运行 `./setup.sh` 启动
5. 定期同步 `data/` 目录数据

**优点**：互不干扰，可以同时工作
**缺点**：需要每台电脑都安装，数据需要手动同步

### 方案2：多人共用（一台服务器）

一台电脑启动局域网模式，其他同事通过浏览器访问：

1. 在服务器电脑上运行 `./start_lan.sh`
2. 记录显示的IP地址（如 192.168.1.100）
3. 其他同事在浏览器访问：`http://192.168.1.100:8501`

**优点**：数据统一，无需重复安装
**缺点**：服务器电脑需保持运行

---

## 配置说明

### 修改公司信息

编辑 `config.py` 文件：

```python
COMPANY_INFO = {
    "name": "海越（湖北）电气股份有限公司",
    "address": "湖北省孝感市孝昌县经济开发区华阳大道188-1号",
    "email": "info@nbhaiyue.com",
    "phone": "+86-0712-8303818",
    # ...
}
```

修改后重启系统生效。

### 修改报价配置

编辑 `config.py` 文件：

```python
QUOTE_CONFIG = {
    "tax_rate": 0.13,          # 13%增值税
    "delivery_days": 30,       # 默认交货期30天
    "warranty_period": "一年",  # 质保期
    "quote_validity_days": 30, # 报价有效期30天
}
```

---

## 常见问题

### Q: 我不是技术人员，如何使用？

A: 系统设计了友好的Web界面，无需编程知识。
1. 阅读 `用户使用手册.md`
2. 按照 `QUICKSTART.md` 操作
3. 遇到问题联系技术支持

### Q: 如何添加新的资质、案例、产品？

A:
1. 启动系统后，点击左侧"📊 资料管理"
2. 选择对应的标签页（资质/案例/产品）
3. 填写信息后点击"添加"按钮

### Q: 生成的投标文件格式不完美怎么办？

A: 系统生成的文件是标准Word格式，可以：
1. 直接用Word或WPS打开
2. 手动调整格式和内容
3. 保存后使用

### Q: 如何让其他同事也能使用？

A: 两种方案：
1. **单机模式**：每个同事安装一套（见上文"其他同事如何使用"）
2. **局域网模式**：启动 `./start_lan.sh`，其他同事通过浏览器访问

### Q: 系统会自动联网吗？数据安全吗？

A:
- 系统完全本地运行，不会自动上传数据
- 所有数据存储在本地的 `data/` 目录
- 数据安全可控，适合企业内部使用

---

## 📁 文档说明

| 文件 | 说明 |
|------|------|
| `README.md` | 本文件 - 项目概述和架构说明 |
| `CHANGELOG.md` | 更新日志 |
| `QUICKSTART.md` | 快速启动指南 |
| `用户使用手册.md` | 详细使用教程（推荐新用户阅读） |
| `PROJECT_SUMMARY.md` | 项目总结 |
| `排错指南.md` | 常见问题排错指南 |

---

## 📞 技术支持

- **邮箱**：gl@haiyueelec.com
- **电话**：0712-8303989
- **网址**：www.haiyueelec.com

---

## 📄 许可证

本项目仅供海越（湖北）电气股份有限公司内部使用。

---

**如有任何问题，请查看 `用户使用手册.md` 或联系技术支持**
