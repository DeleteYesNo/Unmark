# Unmark — Video Auto Processor

自动去水印 + AI 分类 + 智能重命名的视频批量处理工具。

监控 `input/` 文件夹，自动完成：
1. **去除 Sora 水印**（使用 [SoraWatermarkCleaner](https://github.com/Doubiiu/SoraWatermarkCleaner)）
2. **AI 自动分类**（使用 Ollama 本地视觉模型）
3. **生成吸引人的标题**（AI 生成或内建标题库）

处理完成的视频输出到 `output/` 文件夹。

---

## 前置要求

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| **Python 3.10+** | 运行主程序 | [python.org](https://www.python.org/downloads/) |
| **SoraWatermarkCleaner** | 去除 Sora 水印 | 见下方说明 |
| **Ollama** | 本地 AI 分类 & 标题生成 | 见下方说明 |
| **ffmpeg** | 抽取视频关键帧 | 见下方说明 |

---

## 安装步骤

### 1. 克隆本项目

```bash
git clone https://github.com/DeleteYesNo/Unmark.git
cd Unmark
```

### 2. 安装 SoraWatermarkCleaner

本工具依赖 [SoraWatermarkCleaner](https://github.com/Doubiiu/SoraWatermarkCleaner) 进行水印去除。

**默认目录结构**（推荐）：
```
parent-folder/
├── Unmark/                  ← 本项目
└── SoraWatermarkCleaner/    ← 水印清除工具
```

```bash
# 在本项目的上层目录克隆
cd ..
git clone https://github.com/Doubiiu/SoraWatermarkCleaner.git
cd SoraWatermarkCleaner

# 创建虚拟环境并安装依赖
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

> **自定义路径**：如果 SoraWatermarkCleaner 不在上层目录，在 `config.json` 中设置 `sora_wm_path` 为其绝对路径。

### 3. 安装 Ollama（本地 AI 模型）

Ollama 用于视频自动分类和 AI 标题生成，所有推理都在本地运行，不需要 API Key。

**安装 Ollama：**

- **Windows**：从 [ollama.com](https://ollama.com/download) 下载安装程序
- **macOS**：`brew install ollama` 或从官网下载
- **Linux**：`curl -fsSL https://ollama.com/install.sh | sh`

**下载视觉模型：**

```bash
# 启动 Ollama 服务（Windows 安装后会自动启动）
ollama serve

# 下载视觉模型（在另一个终端）
ollama pull qwen3-vl:2b    # 轻量版（推荐，约 1.8GB）
# 或
ollama pull qwen3-vl:8b    # 完整版（效果更好，约 5GB）
```

> 模型下载完成后，Ollama 服务需要保持运行（默认监听 `http://localhost:11434`）。

### 4. 安装 ffmpeg

ffmpeg 用于从视频中抽取关键帧供 AI 分析。

- **Windows**：从 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载，解压后将 `bin/` 目录添加到系统 PATH
- **macOS**：`brew install ffmpeg`
- **Linux**：`sudo apt install ffmpeg`（Ubuntu/Debian）

验证安装：
```bash
ffmpeg -version
ffprobe -version
```

### 5. 复制配置文件

```bash
cp config.example.json config.json
```

根据需要编辑 `config.json`：

```jsonc
{
    "cleaner_type": "lama",         // "lama"（快）或 "e2fgvi_hq"（高质量）
    "ollama_model": "qwen3-vl:2b",  // Ollama 模型名称
    "ollama_url": "http://localhost:11434",
    "ai_title_enabled": true,        // 是否用 AI 生成标题
    "title_language": "en",          // 标题语言
    "sora_wm_path": "",              // SoraWatermarkCleaner 路径（留空=自动检测上层目录）
    "title_rules": ""                // 自定义标题生成规则
}
```

### 6. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

> **注意**：如果使用 `start_auto_processor.bat` 启动，它会自动使用 SoraWatermarkCleaner 虚拟环境中的 Python（已包含所有依赖）。

---

## 使用方法

### 方式一：批处理启动（Windows，推荐）

双击 `start_auto_processor.bat`，程序会自动使用 SoraWatermarkCleaner 的 Python 环境。

> 如果 Python 路径不同，可设置环境变量 `SORA_WM_PYTHON` 指向正确的 Python 可执行文件。

### 方式二：命令行启动

```bash
# 使用 SoraWatermarkCleaner 的虚拟环境
../SoraWatermarkCleaner/.venv/Scripts/python auto_processor.py    # Windows
../SoraWatermarkCleaner/.venv/bin/python auto_processor.py        # macOS/Linux
```

### 工作流程

1. 启动程序后，选择 `[1] 自动监控模式`
2. 将视频文件放入 `input/` 下对应的分类子文件夹：
   - `00_自动分类/` — AI 自动判断分类
   - `01_生存惊险/` ~ `18_随机混合/` — 手动指定分类
3. 程序自动完成：去水印 → AI 分类（如果是自动分类）→ 生成标题 → 输出到 `output/`

---

## 目录结构

```
Unmark/
├── auto_processor.py         # 主程序（监控、去水印、分类、重命名）
├── rename_videos.py          # 标题库 & 重命名逻辑
├── quick_start.py            # 快速启动（LAMA 模式）
├── quick_rename.py           # 拖拽重命名工具
├── start_auto_processor.bat  # Windows 启动脚本
├── run.bat                   # 简易启动脚本
├── config.example.json       # 配置模板
├── requirements.txt          # Python 依赖
├── titles.txt                # 标题列表
└── input/                    # 输入文件夹（19 个分类子目录）
    ├── 00_自动分类/
    ├── 01_生存惊险/
    ├── ...
    └── 18_随机混合/
```

---

## 其他工具

| 脚本 | 用途 |
|------|------|
| `quick_rename.py` | 将视频文件夹拖到脚本上，快速批量重命名 |
| `run.bat` | 运行 `rename_videos.py` 的简易批量重命名 |

---

## 常见问题

**Q: 提示无法连接 Ollama**
确认 Ollama 服务正在运行：`ollama serve`，默认端口 11434。

**Q: AI 分类/标题效果不好**
尝试换用更大的模型：在 `config.json` 中将 `ollama_model` 改为 `qwen3-vl:8b`。

**Q: 去水印失败**
确认 SoraWatermarkCleaner 已正确安装且模型权重已下载。详见其 README。

**Q: ffmpeg 找不到**
确认 ffmpeg 和 ffprobe 已添加到系统 PATH，重新打开终端后执行 `ffmpeg -version` 验证。
