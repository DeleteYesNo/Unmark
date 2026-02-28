# Unmark — Video Auto Processor

**[English](#english)** | **[繁體中文](#繁體中文)**

---

# English

Batch video processing tool with automatic watermark removal + AI classification + smart renaming.

Monitors the `input/` folder and automatically:
1. **Removes Sora watermarks** (via [SoraWatermarkCleaner](https://github.com/Doubiiu/SoraWatermarkCleaner))
2. **Classifies videos with AI** (via Ollama local vision model)
3. **Generates catchy titles** (AI-generated or built-in title library)

Processed videos are saved to the `output/` folder.

---

## Prerequisites

| Dependency | Purpose | Install |
|---|---|---|
| **Python 3.10+** | Run the main program | [python.org](https://www.python.org/downloads/) |
| **SoraWatermarkCleaner** | Remove Sora watermarks | See below |
| **Ollama** | Local AI classification & title generation | See below |
| **ffmpeg** | Extract video keyframes | See below |

---

## Installation

### 1. Clone this project

```bash
git clone https://github.com/DeleteYesNo/Unmark.git
cd Unmark
```

### 2. Install SoraWatermarkCleaner

This tool depends on [SoraWatermarkCleaner](https://github.com/Doubiiu/SoraWatermarkCleaner) for watermark removal.

**Default directory structure** (recommended):
```
parent-folder/
├── Unmark/                  ← this project
└── SoraWatermarkCleaner/    ← watermark removal tool
```

```bash
# Clone in the parent directory of this project
cd ..
git clone https://github.com/Doubiiu/SoraWatermarkCleaner.git
cd SoraWatermarkCleaner

# Create virtual environment and install dependencies
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

> **Custom path**: If SoraWatermarkCleaner is not in the parent directory, set `sora_wm_path` in `config.json` to its absolute path.

### 3. Install Ollama (Local AI Model)

Ollama is used for video auto-classification and AI title generation. All inference runs locally — no API key required.

**Install Ollama:**

- **Windows**: Download from [ollama.com](https://ollama.com/download)
- **macOS**: `brew install ollama` or download from the website
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

**Download a vision model:**

```bash
# Start the Ollama service (auto-starts on Windows after installation)
ollama serve

# Download a vision model (in another terminal)
ollama pull qwen3-vl:2b    # Lightweight (recommended, ~1.8GB)
# or
ollama pull qwen3-vl:8b    # Full version (better quality, ~5GB)
```

> The Ollama service must remain running (default: `http://localhost:11434`).

### 4. Install ffmpeg

ffmpeg is used to extract keyframes from videos for AI analysis.

- **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract and add `bin/` to your system PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian)

Verify installation:
```bash
ffmpeg -version
ffprobe -version
```

### 5. Copy the config file

```bash
cp config.example.json config.json
```

Edit `config.json` as needed:

```jsonc
{
    "cleaner_type": "lama",         // "lama" (fast) or "e2fgvi_hq" (high quality)
    "ollama_model": "qwen3-vl:2b",  // Ollama model name
    "ollama_url": "http://localhost:11434",
    "ai_title_enabled": true,        // Enable AI title generation
    "title_language": "en",          // Title language
    "sora_wm_path": "",              // SoraWatermarkCleaner path (empty = auto-detect in parent dir)
    "title_rules": ""                // Custom title generation rules
}
```

### 6. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note**: If you use `start_auto_processor.bat` to launch, it automatically uses the Python from SoraWatermarkCleaner's virtual environment (which already includes all dependencies).

---

## Usage

### Option A: Batch file (Windows, recommended)

Double-click `start_auto_processor.bat`. It automatically uses SoraWatermarkCleaner's Python environment.

> To use a different Python path, set the `SORA_WM_PYTHON` environment variable to point to the correct Python executable.

### Option B: Command line

```bash
# Using SoraWatermarkCleaner's virtual environment
../SoraWatermarkCleaner/.venv/Scripts/python auto_processor.py    # Windows
../SoraWatermarkCleaner/.venv/bin/python auto_processor.py        # macOS/Linux
```

### Workflow

1. Launch the program and select `[1] Auto watch mode`
2. Place video files into the appropriate subfolder under `input/`:
   - `00_自動分類/` — AI auto-classification
   - `01_生存惊险/` ~ `18_随机混合/` — Manual category
3. The program automatically: removes watermark → AI classification (if auto) → generates title → outputs to `output/`

---

## Project Structure

```
Unmark/
├── auto_processor.py         # Main program (watch, watermark, classify, rename)
├── rename_videos.py          # Title library & rename logic
├── quick_start.py            # Quick start (LAMA mode)
├── quick_rename.py           # Drag-and-drop rename tool
├── start_auto_processor.bat  # Windows launch script
├── run.bat                   # Simple launch script
├── config.example.json       # Config template
├── requirements.txt          # Python dependencies
├── titles.txt                # Title list
└── input/                    # Input folder (19 category subdirectories)
    ├── 00_自動分類/
    ├── 01_生存惊险/
    ├── ...
    └── 18_随机混合/
```

---

## Other Tools

| Script | Purpose |
|---|---|
| `quick_rename.py` | Drag a video folder onto the script for quick batch renaming |
| `run.bat` | Simple batch rename via `rename_videos.py` |

---

## FAQ

**Q: Cannot connect to Ollama**
Make sure the Ollama service is running: `ollama serve` (default port 11434).

**Q: AI classification / titles are poor quality**
Try a larger model: set `ollama_model` to `qwen3-vl:8b` in `config.json`.

**Q: Watermark removal fails**
Make sure SoraWatermarkCleaner is properly installed and model weights are downloaded. See its README.

**Q: ffmpeg not found**
Make sure ffmpeg and ffprobe are added to your system PATH. Restart your terminal and verify with `ffmpeg -version`.

---
---

# 繁體中文

自動去浮水印 + AI 分類 + 智慧重新命名的影片批次處理工具。

監控 `input/` 資料夾，自動完成：
1. **去除 Sora 浮水印**（使用 [SoraWatermarkCleaner](https://github.com/Doubiiu/SoraWatermarkCleaner)）
2. **AI 自動分類**（使用 Ollama 本地視覺模型）
3. **產生吸引人的標題**（AI 產生或內建標題庫）

處理完成的影片輸出到 `output/` 資料夾。

---

## 前置需求

| 依賴 | 用途 | 安裝方式 |
|------|------|----------|
| **Python 3.10+** | 執行主程式 | [python.org](https://www.python.org/downloads/) |
| **SoraWatermarkCleaner** | 去除 Sora 浮水印 | 見下方說明 |
| **Ollama** | 本地 AI 分類 & 標題產生 | 見下方說明 |
| **ffmpeg** | 擷取影片關鍵幀 | 見下方說明 |

---

## 安裝步驟

### 1. 複製本專案

```bash
git clone https://github.com/DeleteYesNo/Unmark.git
cd Unmark
```

### 2. 安裝 SoraWatermarkCleaner

本工具依賴 [SoraWatermarkCleaner](https://github.com/Doubiiu/SoraWatermarkCleaner) 進行浮水印去除。

**預設目錄結構**（建議）：
```
parent-folder/
├── Unmark/                  ← 本專案
└── SoraWatermarkCleaner/    ← 浮水印清除工具
```

```bash
# 在本專案的上層目錄複製
cd ..
git clone https://github.com/Doubiiu/SoraWatermarkCleaner.git
cd SoraWatermarkCleaner

# 建立虛擬環境並安裝依賴
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

> **自訂路徑**：如果 SoraWatermarkCleaner 不在上層目錄，請在 `config.json` 中設定 `sora_wm_path` 為其絕對路徑。

### 3. 安裝 Ollama（本地 AI 模型）

Ollama 用於影片自動分類和 AI 標題產生，所有推論都在本地執行，不需要 API Key。

**安裝 Ollama：**

- **Windows**：從 [ollama.com](https://ollama.com/download) 下載安裝程式
- **macOS**：`brew install ollama` 或從官網下載
- **Linux**：`curl -fsSL https://ollama.com/install.sh | sh`

**下載視覺模型：**

```bash
# 啟動 Ollama 服務（Windows 安裝後會自動啟動）
ollama serve

# 下載視覺模型（在另一個終端機）
ollama pull qwen3-vl:2b    # 輕量版（建議，約 1.8GB）
# 或
ollama pull qwen3-vl:8b    # 完整版（效果更好，約 5GB）
```

> 模型下載完成後，Ollama 服務需要保持執行（預設監聽 `http://localhost:11434`）。

### 4. 安裝 ffmpeg

ffmpeg 用於從影片中擷取關鍵幀供 AI 分析。

- **Windows**：從 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下載，解壓縮後將 `bin/` 目錄加入系統 PATH
- **macOS**：`brew install ffmpeg`
- **Linux**：`sudo apt install ffmpeg`（Ubuntu/Debian）

驗證安裝：
```bash
ffmpeg -version
ffprobe -version
```

### 5. 複製設定檔

```bash
cp config.example.json config.json
```

根據需要編輯 `config.json`：

```jsonc
{
    "cleaner_type": "lama",         // "lama"（快速）或 "e2fgvi_hq"（高品質）
    "ollama_model": "qwen3-vl:2b",  // Ollama 模型名稱
    "ollama_url": "http://localhost:11434",
    "ai_title_enabled": true,        // 是否使用 AI 產生標題
    "title_language": "en",          // 標題語言
    "sora_wm_path": "",              // SoraWatermarkCleaner 路徑（留空＝自動偵測上層目錄）
    "title_rules": ""                // 自訂標題產生規則
}
```

### 6. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

> **注意**：如果使用 `start_auto_processor.bat` 啟動，它會自動使用 SoraWatermarkCleaner 虛擬環境中的 Python（已包含所有依賴）。

---

## 使用方法

### 方式一：批次檔啟動（Windows，建議）

雙擊 `start_auto_processor.bat`，程式會自動使用 SoraWatermarkCleaner 的 Python 環境。

> 如果 Python 路徑不同，可設定環境變數 `SORA_WM_PYTHON` 指向正確的 Python 執行檔。

### 方式二：命令列啟動

```bash
# 使用 SoraWatermarkCleaner 的虛擬環境
../SoraWatermarkCleaner/.venv/Scripts/python auto_processor.py    # Windows
../SoraWatermarkCleaner/.venv/bin/python auto_processor.py        # macOS/Linux
```

### 工作流程

1. 啟動程式後，選擇 `[1] 自動監控模式`
2. 將影片檔案放入 `input/` 下對應的分類子資料夾：
   - `00_自動分類/` — AI 自動判斷分類
   - `01_生存惊险/` ~ `18_随机混合/` — 手動指定分類
3. 程式自動完成：去浮水印 → AI 分類（如果是自動分類）→ 產生標題 → 輸出到 `output/`

---

## 目錄結構

```
Unmark/
├── auto_processor.py         # 主程式（監控、去浮水印、分類、重新命名）
├── rename_videos.py          # 標題庫 & 重新命名邏輯
├── quick_start.py            # 快速啟動（LAMA 模式）
├── quick_rename.py           # 拖曳重新命名工具
├── start_auto_processor.bat  # Windows 啟動腳本
├── run.bat                   # 簡易啟動腳本
├── config.example.json       # 設定範本
├── requirements.txt          # Python 依賴
├── titles.txt                # 標題列表
└── input/                    # 輸入資料夾（19 個分類子目錄）
    ├── 00_自動分類/
    ├── 01_生存惊险/
    ├── ...
    └── 18_随机混合/
```

---

## 其他工具

| 腳本 | 用途 |
|------|------|
| `quick_rename.py` | 將影片資料夾拖到腳本上，快速批次重新命名 |
| `run.bat` | 執行 `rename_videos.py` 的簡易批次重新命名 |

---

## 常見問題

**Q: 提示無法連線 Ollama**
確認 Ollama 服務正在執行：`ollama serve`，預設連接埠 11434。

**Q: AI 分類／標題效果不好**
嘗試換用更大的模型：在 `config.json` 中將 `ollama_model` 改為 `qwen3-vl:8b`。

**Q: 去浮水印失敗**
確認 SoraWatermarkCleaner 已正確安裝且模型權重已下載。詳見其 README。

**Q: ffmpeg 找不到**
確認 ffmpeg 和 ffprobe 已加入系統 PATH，重新開啟終端機後執行 `ffmpeg -version` 驗證。
