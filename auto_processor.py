# -*- coding: utf-8 -*-
"""
🎬 视频自动处理器 / Video Auto Processor
==========================================
功能:
1. 监控指定文件夹的新视频
2. 自动去除水印 (使用 SoraWatermarkCleaner)
3. 根据分类自动重命名为吸引人的标题

使用方法:
- 将视频放入 input 文件夹对应的分类子文件夹
- 程序自动处理并输出到 output 文件夹
"""

import os
import sys
import io

# 修复 Windows 终端 Unicode 编码问题
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import shutil
import json
import random
import base64
import subprocess
import tempfile
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
import threading
from queue import Queue

# 添加 SoraWatermarkCleaner 路径
def _get_sora_wm_path():
    config_path = Path(__file__).parent / "config.json"
    default = Path(__file__).parent.parent / "SoraWatermarkCleaner"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        custom = cfg.get("sora_wm_path", "")
        if custom:
            return Path(custom)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return default

SORA_WM_PATH = _get_sora_wm_path()
sys.path.insert(0, str(SORA_WM_PATH))

# ============================================================
# 配置 / Configuration
# ============================================================

@dataclass
class ProcessorConfig:
    """处理器配置"""
    # 文件夹路径
    input_folder: Path = Path(__file__).parent / "input"
    output_folder: Path = Path(__file__).parent / "output"
    processing_folder: Path = Path(__file__).parent / "processing"
    failed_folder: Path = Path(__file__).parent / "failed"

    # 处理设置
    watch_interval: float = 3.0  # 监控间隔（秒）
    cleaner_type: str = "lama"  # 水印清除模型: "lama" (快) 或 "e2fgvi_hq" (质量好但慢)

    # Ollama 设置（自动分类用）
    ollama_model: str = "qwen3-vl:8b"
    ollama_url: str = "http://localhost:11434"

    # 视频格式
    video_extensions: tuple = ('.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v')

    # AI 标题生成设置
    ai_title_enabled: bool = True
    title_language: str = "en"
    title_rules: str = ""

    # SoraWatermarkCleaner 路径（留空则自动使用上层目录）
    sora_wm_path: str = ""


# ============================================================
# 标题库 (从 rename_videos.py 导入)
# ============================================================

from rename_videos import TITLE_STYLES, sanitize_filename


# 分类文件夹映射
CATEGORY_FOLDER_MAP = {
    "auto": "00_自动分类",
    "survival": "01_生存惊险",
    "reversal": "02_反转剧情",
    "heartwarming": "03_温馨感动",
    "shorts": "04_短视频",
    "candid": "05_真实记录",
    "fantasy_mysterious": "06_神秘生物",
    "fantasy_discovery": "07_奇幻发现",
    "fantasy_bond": "08_羁绊连结",
    "fantasy_majestic": "09_威严壮丽",
    "fantasy_cute": "10_可爱奇幻",
    "fantasy_dark": "11_黑暗奇幻",
    "fantasy_elemental": "12_元素生物",
    "fantasy_lore": "13_世界传说",
    "fantasy_pov": "14_生物视角",
    "deep": "15_深层反思",
    "quiet_warmth": "16_静谧温暖",
    "sad_reality": "17_悲伤现实",
    "mixed": "18_随机混合",
}


# ============================================================
# AI 视频分类器
# ============================================================

# 分类描述（用于 AI 分类 prompt）
CATEGORY_DESCRIPTIONS = {
    "survival": "野生动物、惊险时刻、求生、危险场景",
    "reversal": "结局反转、出人意料、剧情翻转",
    "heartwarming": "温暖、治愈、感人、温馨的内容",
    "shorts": "适合短视频平台的简短内容",
    "candid": "真实记录、偶然拍到、纪实风格",
    "fantasy_mysterious": "神秘、未知的奇幻生物",
    "fantasy_discovery": "发现、初遇奇幻生物的时刻",
    "fantasy_bond": "人与奇幻生物之间的情感连结、羁绊",
    "fantasy_majestic": "展现奇幻生物威严、壮观的时刻",
    "fantasy_cute": "可爱、萌系的奇幻生物",
    "fantasy_dark": "黑暗、神秘、略带恐怖的奇幻生物",
    "fantasy_elemental": "火、水、风、土等元素生物",
    "fantasy_lore": "奇幻世界观、背景故事、传说",
    "fantasy_pov": "从奇幻生物的视角讲述",
    "deep": "被误解的生物、哲理性、深层反思",
    "quiet_warmth": "安静、治愈、温柔的时刻",
    "sad_reality": "现实、沉重、引人深思的内容",
    "mixed": "不属于以上任何分类的内容",
}


class VideoClassifier:
    """使用 Ollama 视觉模型自动分类视频"""

    def __init__(self, ollama_url: str = "http://localhost:11434", ollama_model: str = "qwen3-vl:8b"):
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model
        self._temp_frames: List[Path] = []

    def extract_frames(self, video_path: Path, num_frames: int = 3) -> List[Path]:
        """用 ffmpeg 从视频均匀抽取关键帧"""
        self.cleanup_frames()

        # 用 ffprobe 获取总帧数
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-count_packets", "-show_entries", "stream=nb_read_packets",
                 "-of", "csv=p=0", str(video_path)],
                capture_output=True, text=True, timeout=30
            )
            total_frames = int(result.stdout.strip())
        except Exception:
            # 备用方案：用时长估算
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(video_path)],
                    capture_output=True, text=True, timeout=30
                )
                duration = float(result.stdout.strip())
                total_frames = int(duration * 24)  # 假设 24fps
            except Exception as e:
                print(f"⚠️ 无法获取视频帧数: {e}")
                return []

        if total_frames < num_frames:
            num_frames = max(total_frames, 1)

        # 均匀分布抽取关键帧
        if num_frames == 1:
            frame_positions = [0]
        else:
            step = total_frames / (num_frames - 1)
            frame_positions = [min(int(i * step), max(total_frames - 1, 0)) for i in range(num_frames)]
        temp_dir = Path(tempfile.mkdtemp(prefix="video_classify_"))
        frames = []

        for i, pos in enumerate(frame_positions):
            frame_path = temp_dir / f"frame_{i}.jpg"
            try:
                subprocess.run(
                    ["ffmpeg", "-i", str(video_path), "-vf", f"select=eq(n\\,{pos})",
                     "-frames:v", "1", "-y", "-q:v", "2", str(frame_path)],
                    capture_output=True, timeout=30
                )
                if frame_path.exists() and frame_path.stat().st_size > 0:
                    frames.append(frame_path)
            except Exception as e:
                print(f"⚠️ 抽取第 {i+1} 帧失败: {e}")

        self._temp_frames = frames
        self._temp_dir = temp_dir
        return frames

    def classify_video(self, video_path: Path) -> Optional[str]:
        """分析视频截图并返回分类 key"""
        print(f"🤖 正在用 AI 分析视频内容...")

        frames = self.extract_frames(video_path)
        if not frames:
            print("⚠️ 无法抽取视频帧，跳过自动分类")
            return None

        print(f"🖼️ 已抽取 {len(frames)} 个关键帧")

        images_b64 = self._frames_to_base64(frames)
        if not images_b64:
            return None

        category_list = "\n".join(
            f"- {key}: {desc}" for key, desc in CATEGORY_DESCRIPTIONS.items()
        )
        prompt = (
            f"请根据以下视频截图判断这个视频最适合哪个分类。\n"
            f"可选分类：\n{category_list}\n\n"
            f"请只回复分类的 key 名称（如 survival、heartwarming 等），不要回复任何其他内容。"
        )

        ai_reply = self._call_ollama(prompt, images_b64)
        if not ai_reply:
            return None

        ai_reply = ai_reply.lower()
        for key in CATEGORY_DESCRIPTIONS:
            if key in ai_reply:
                print(f"✅ AI 分类结果: {key} ({CATEGORY_DESCRIPTIONS[key]})")
                return key

        print(f"⚠️ AI 回复无法解析为有效分类: {ai_reply}")
        return None

    def generate_title(self, video_path: Path, category: str, rules: str = "", language: str = "en") -> Optional[str]:
        """用 AI 根据视频截图和分类信息生成标题"""
        print(f"🤖 正在用 AI 生成标题...")

        # 复用已有截图（如果分类刚跑过），否则重新抽取
        frames = self._temp_frames if self._temp_frames else self.extract_frames(video_path)
        if not frames:
            print("⚠️ 无法抽取视频帧，跳过 AI 标题生成")
            return None

        images_b64 = self._frames_to_base64(frames)
        if not images_b64:
            return None

        category_desc = CATEGORY_DESCRIPTIONS.get(category, category)

        prompt = (
            f"你是一个视频标题生成器。根据以下视频截图和分类信息，生成一个吸引人的标题。\n\n"
            f"分类: {category} - {category_desc}\n"
            f"语言: {language}\n"
        )
        if rules:
            prompt += f"\n用户规则:\n{rules}\n"
        prompt += "\n请只回复标题本身，不要加引号或其他内容。"

        title = self._call_ollama(prompt, images_b64)
        if title:
            # 去除可能的引号包裹
            if len(title) >= 2 and title[0] in ('"', "'", '\u201c') and title[-1] in ('"', "'", '\u201d'):
                title = title[1:-1].strip()
            if title:
                print(f"✅ AI 生成标题: {title}")
                return title

        print("⚠️ AI 标题生成失败")
        return None

    def classify_and_title(self, video_path: Path, rules: str = "", language: str = "en") -> tuple:
        """一次 AI 调用同时完成分类 + 标题生成（节省时间）

        Returns:
            (category, title) — 任一可能为 None
        """
        print(f"🤖 正在用 AI 分析视频内容并生成标题...")

        frames = self.extract_frames(video_path)
        if not frames:
            print("⚠️ 无法抽取视频帧")
            return None, None

        print(f"🖼️ 已抽取 {len(frames)} 个关键帧")

        images_b64 = self._frames_to_base64(frames)
        if not images_b64:
            return None, None

        category_list = "\n".join(
            f"- {key}: {desc}" for key, desc in CATEGORY_DESCRIPTIONS.items()
        )

        prompt = (
            f"请根据以下视频截图完成两个任务:\n\n"
            f"任务1 - 分类: 从以下分类中选择最合适的一个:\n{category_list}\n\n"
            f"任务2 - 标题: 为这个视频生成一个吸引人的标题\n"
            f"语言: {language}\n"
        )
        if rules:
            prompt += f"\n用户标题规则:\n{rules}\n"
        prompt += (
            f"\n请严格按照以下格式回复（两行）:\n"
            f"CATEGORY: <分类key>\n"
            f"TITLE: <标题>"
        )

        ai_reply = self._call_ollama(prompt, images_b64)
        if not ai_reply:
            return None, None

        # 解析结果
        category = None
        title = None

        for line in ai_reply.split("\n"):
            line = line.strip()
            if line.upper().startswith("CATEGORY:"):
                cat_value = line.split(":", 1)[1].strip().lower()
                for key in CATEGORY_DESCRIPTIONS:
                    if key in cat_value:
                        category = key
                        break
            elif line.upper().startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
                # 去除引号
                if len(title) >= 2 and title[0] in ('"', "'", '\u201c') and title[-1] in ('"', "'", '\u201d'):
                    title = title[1:-1].strip()

        if category:
            print(f"✅ AI 分类结果: {category} ({CATEGORY_DESCRIPTIONS[category]})")
        else:
            print(f"⚠️ AI 分类失败")

        if title:
            print(f"✅ AI 生成标题: {title}")
        else:
            print(f"⚠️ AI 标题生成失败")

        return category, title

    def _frames_to_base64(self, frames: List[Path]) -> List[str]:
        """将帧图片转为 base64 列表"""
        images_b64 = []
        for frame_path in frames:
            try:
                with open(frame_path, "rb") as f:
                    images_b64.append(base64.b64encode(f.read()).decode("utf-8"))
            except Exception:
                pass
        return images_b64

    def _call_ollama(self, prompt: str, images_b64: List[str] = None, max_retries: int = 2) -> Optional[str]:
        """调用 Ollama API 并返回回复文本（streaming 模式，失败自动重试）"""
        message = {"role": "user", "content": f"/no_think\n{prompt}"}
        if images_b64:
            message["images"] = images_b64

        payload = {
            "model": self.ollama_model,
            "messages": [message],
            "stream": True,
        }

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload,
                    stream=True,
                    timeout=(10, None),  # 无读取超时，streaming 持续接收
                )
                response.raise_for_status()

                ai_reply = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        ai_reply += token
                        if chunk.get("done"):
                            break

                ai_reply = ai_reply.strip()

                # 兼容旧版：处理 <think> 标签
                if "</think>" in ai_reply:
                    ai_reply = ai_reply.split("</think>")[-1].strip()

                if ai_reply:
                    return ai_reply

                # 回复为空，重试
                if attempt < max_retries:
                    print(f"⚠️ AI 回复为空，重试中... ({attempt}/{max_retries})")
                else:
                    print(f"⚠️ AI 回复为空（已重试 {max_retries} 次）")
                    return None

            except requests.ConnectionError:
                print(f"❌ 无法连接 Ollama 服务 ({self.ollama_url})")
                return None
            except Exception as e:
                if attempt < max_retries:
                    print(f"⚠️ AI 调用失败: {e}，重试中... ({attempt}/{max_retries})")
                else:
                    print(f"❌ AI 调用失败: {e}（已重试 {max_retries} 次）")
                    return None

        return None

    def cleanup_frames(self):
        """清理暂存截图"""
        for frame in self._temp_frames:
            try:
                frame.unlink(missing_ok=True)
            except Exception:
                pass
        self._temp_frames = []
        if hasattr(self, '_temp_dir') and self._temp_dir.exists():
            try:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            except Exception:
                pass


# ============================================================
# 标题管理器
# ============================================================

class TitleManager:
    """管理标题分配，确保不重复"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.used_titles: Dict[str, List[int]] = {}
        self.load_state()

    def load_state(self):
        """加载已使用的标题状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.used_titles = json.load(f)
            except:
                self.used_titles = {}

    def save_state(self):
        """保存状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.used_titles, f, ensure_ascii=False, indent=2)

    def get_next_title(self, category: str, shuffle: bool = True) -> Optional[str]:
        """获取下一个未使用的标题"""
        if category not in TITLE_STYLES:
            return None

        titles = TITLE_STYLES[category]["titles"]
        if not titles:
            # 混合模式
            all_titles = []
            for key, style in TITLE_STYLES.items():
                if key != "mixed" and style["titles"]:
                    all_titles.extend([(key, i) for i in range(len(style["titles"]))])
            if shuffle:
                random.shuffle(all_titles)
            # 简单返回一个随机标题
            if all_titles:
                cat, idx = random.choice(all_titles)
                return TITLE_STYLES[cat]["titles"][idx]
            return None

        # 获取已使用的索引
        if category not in self.used_titles:
            self.used_titles[category] = []

        used_indices = set(self.used_titles[category])
        available_indices = [i for i in range(len(titles)) if i not in used_indices]

        # 如果所有标题都用过了，重置
        if not available_indices:
            self.used_titles[category] = []
            available_indices = list(range(len(titles)))

        # 选择标题
        if shuffle:
            idx = random.choice(available_indices)
        else:
            idx = available_indices[0]

        self.used_titles[category].append(idx)
        self.save_state()

        return titles[idx]

    def reset_category(self, category: str):
        """重置某个分类的使用记录"""
        if category in self.used_titles:
            self.used_titles[category] = []
            self.save_state()


# ============================================================
# 水印清除器包装
# ============================================================

class WatermarkRemover:
    """水印清除器"""

    def __init__(self, cleaner_type: str = "lama"):
        self.cleaner_type = cleaner_type
        self.cleaner = None
        self._initialized = False

    def initialize(self):
        """延迟初始化清除器"""
        if self._initialized:
            return True

        try:
            from sorawm.core import SoraWM
            from sorawm.watermark_cleaner import CleanerType

            cleaner_type_enum = CleanerType.LAMA if self.cleaner_type == "lama" else CleanerType.E2FGVI_HQ

            print(f"🔄 正在加载 {self.cleaner_type.upper()} 模型...")
            self.cleaner = SoraWM(cleaner_type=cleaner_type_enum)
            self._initialized = True
            print(f"✅ {self.cleaner_type.upper()} 模型加载完成")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False

    def remove_watermark(self, input_path: Path, output_path: Path) -> bool:
        """去除视频水印"""
        if not self.initialize():
            return False

        try:
            print(f"🎬 处理中: {input_path.name}")
            self.cleaner.run(
                Path(input_path),
                Path(output_path)
            )
            print(f"✅ 水印去除完成: {output_path.name}")
            return True
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False


# ============================================================
# 视频处理器
# ============================================================

class VideoProcessor:
    """视频自动处理器"""

    def __init__(self, config: ProcessorConfig = None):
        self.config = config or ProcessorConfig()
        self.title_manager = TitleManager(self.config.input_folder.parent / "title_state.json")
        self.watermark_remover = WatermarkRemover(self.config.cleaner_type)
        self.classifier = VideoClassifier(self.config.ollama_url, self.config.ollama_model)
        self.processing_queue: Queue = Queue()
        self.is_running = False

        # 创建文件夹结构
        self._setup_folders()

    def _setup_folders(self):
        """创建必要的文件夹结构"""
        # 创建主文件夹
        for folder in [self.config.input_folder, self.config.output_folder,
                       self.config.processing_folder, self.config.failed_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # 在 input 文件夹中创建分类子文件夹
        for category, folder_name in CATEGORY_FOLDER_MAP.items():
            (self.config.input_folder / folder_name).mkdir(exist_ok=True)

        print(f"📁 文件夹结构已创建:")
        print(f"   输入: {self.config.input_folder}")
        print(f"   输出: {self.config.output_folder}")

    def _get_category_from_folder(self, file_path: Path) -> Optional[str]:
        """根据文件所在文件夹确定分类"""
        parent_name = file_path.parent.name

        for category, folder_name in CATEGORY_FOLDER_MAP.items():
            if folder_name == parent_name:
                return category

        return None

    def _find_new_videos(self) -> List[Path]:
        """查找新的待处理视频"""
        videos = []

        for category, folder_name in CATEGORY_FOLDER_MAP.items():
            folder = self.config.input_folder / folder_name
            if folder.exists():
                for file in folder.iterdir():
                    if file.is_file() and file.suffix.lower() in self.config.video_extensions:
                        videos.append(file)

        return videos

    def _generate_output_filename(self, category: str, extension: str, ai_title: str = None) -> str:
        """生成输出文件名"""
        if ai_title:
            safe_title = sanitize_filename(ai_title)
            return f"{safe_title}{extension}"

        title = self.title_manager.get_next_title(category, shuffle=True)
        if not title:
            # 备用文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"video_{timestamp}{extension}"

        safe_title = sanitize_filename(title)
        return f"{safe_title}{extension}"

    def process_video(self, video_path: Path) -> bool:
        """处理单个视频"""
        category = self._get_category_from_folder(video_path)
        if not category:
            print(f"⚠️ 无法确定视频分类: {video_path}")
            return False

        print(f"\n{'='*60}")
        print(f"📹 开始处理: {video_path.name}")

        # === 第一步：先抽取截图（很快，避免后续文件锁冲突）===
        need_ai = (category == "auto") or self.config.ai_title_enabled
        pre_extracted_b64 = []
        if need_ai:
            print(f"🖼️ 抽取视频关键帧...")
            frames = self.classifier.extract_frames(video_path)
            if frames:
                pre_extracted_b64 = self.classifier._frames_to_base64(frames)
                print(f"🖼️ 已抽取 {len(frames)} 个关键帧")
            self.classifier.cleanup_frames()

        # === 第二步：移动到处理中文件夹 ===
        processing_path = self.config.processing_folder / video_path.name
        try:
            shutil.move(str(video_path), str(processing_path))
        except Exception as e:
            print(f"❌ 移动文件失败: {e}")
            return False

        # === 第三步：并行处理 AI 分析 + 去水印 ===
        ai_title = None
        wm_result = {"success": False, "temp_output": None}

        def do_watermark():
            """在线程中去除水印"""
            temp_out = self.config.processing_folder / f"temp_{processing_path.name}"
            wm_result["temp_output"] = temp_out
            wm_result["success"] = self.watermark_remover.remove_watermark(processing_path, temp_out)

        def do_ai_analysis():
            """在线程中进行 AI 分析（使用预先抽取的截图）"""
            nonlocal category, ai_title

            if not pre_extracted_b64:
                if category == "auto":
                    category = "mixed"
                return

            if category == "auto" and self.config.ai_title_enabled:
                # 自动分类 + 标题：合并为一次 AI 调用
                print(f"📂 分类: 🤖 自动分类 + AI 标题生成中...")
                ai_cat, ai_t = self._ai_classify_and_title(pre_extracted_b64)
                if ai_cat:
                    category = ai_cat
                    print(f"📂 AI 选定分类: {TITLE_STYLES.get(category, {}).get('name', category)}")
                else:
                    print(f"⚠️ AI 分类失败，使用默认分类: mixed")
                    category = "mixed"
                ai_title = ai_t

            elif category == "auto":
                # 只分类
                print(f"📂 分类: 🤖 自动分类中...")
                ai_cat = self._ai_classify_only(pre_extracted_b64)
                if ai_cat:
                    category = ai_cat
                    print(f"📂 AI 选定分类: {TITLE_STYLES.get(category, {}).get('name', category)}")
                else:
                    print(f"⚠️ AI 分类失败，使用默认分类: mixed")
                    category = "mixed"

            elif self.config.ai_title_enabled:
                # 已有分类，只生成标题
                print(f"📂 分类: {TITLE_STYLES.get(category, {}).get('name', category)}")
                ai_title = self._ai_title_only(pre_extracted_b64, category)

            else:
                print(f"📂 分类: {TITLE_STYLES.get(category, {}).get('name', category)}")

        print(f"{'='*60}")
        print(f"⚡ 并行处理: AI 分析 + 去水印同时进行...")

        wm_thread = threading.Thread(target=do_watermark)
        ai_thread = threading.Thread(target=do_ai_analysis)

        wm_thread.start()
        ai_thread.start()

        ai_thread.join()
        wm_thread.join()

        if not ai_title and self.config.ai_title_enabled:
            print("⚠️ AI 标题生成失败，使用标题库 fallback")

        # 生成输出文件名
        output_filename = self._generate_output_filename(category, processing_path.suffix, ai_title=ai_title)
        output_path = self.config.output_folder / output_filename

        # 确保文件名不重复
        counter = 1
        while output_path.exists():
            name_without_ext = output_filename.rsplit('.', 1)[0]
            output_path = self.config.output_folder / f"{name_without_ext}_{counter}{processing_path.suffix}"
            counter += 1

        # 处理水印结果
        temp_output = wm_result["temp_output"]
        if wm_result["success"] and temp_output and temp_output.exists():
            shutil.move(str(temp_output), str(output_path))
            processing_path.unlink(missing_ok=True)
            print(f"\n✨ 处理完成!")
            print(f"   新文件名: {output_path.name}")
            print(f"   位置: {output_path}")
            return True
        else:
            failed_path = self.config.failed_folder / video_path.name
            shutil.move(str(processing_path), str(failed_path))
            print(f"\n❌ 处理失败，文件已移至: {failed_path}")
            return False

    def _ai_classify_and_title(self, images_b64: List[str]) -> tuple:
        """用预先抽取的截图进行分类+标题（一次 AI 调用）"""
        category_keys = ", ".join(CATEGORY_DESCRIPTIONS.keys())
        prompt = (
            f"Look at these video frames. Do 2 tasks:\n"
            f"1) Classify into one of: {category_keys}\n"
            f"2) Write a viral title ({self.config.title_language})\n"
        )
        if self.config.title_rules:
            prompt += f"\nTitle rules: {self.config.title_rules}\n"
        prompt += (
            f"\nReply ONLY in this exact format (2 lines, nothing else):\n"
            f"CATEGORY: <key>\n"
            f"TITLE: <title>"
        )

        ai_reply = self.classifier._call_ollama(prompt, images_b64)
        if not ai_reply:
            return None, None

        category = None
        title = None
        for line in ai_reply.split("\n"):
            line = line.strip()
            # 去除 markdown 格式如 **Task 1:**
            clean = line.replace("*", "").strip()

            if clean.upper().startswith("CATEGORY:") or clean.upper().startswith("CATEGORY："):
                cat_value = clean.split(":", 1)[-1].split("\uff1a", 1)[-1].strip().lower()
                for key in CATEGORY_DESCRIPTIONS:
                    if key in cat_value:
                        category = key
                        break
            elif clean.upper().startswith("TITLE:") or clean.upper().startswith("TITLE："):
                title = clean.split(":", 1)[-1].split("\uff1a", 1)[-1].strip()
                # 去除引号
                if len(title) >= 2 and title[0] in ('"', "'", '\u201c') and title[-1] in ('"', "'", '\u201d'):
                    title = title[1:-1].strip()
            else:
                # 尝试从非标准格式中提取分类 key
                if not category:
                    lower_line = clean.lower()
                    for key in CATEGORY_DESCRIPTIONS:
                        if key == lower_line.strip():
                            category = key
                            break

        if title:
            print(f"✅ AI 生成标题: {title}")
        return category, title

    def _ai_classify_only(self, images_b64: List[str]) -> Optional[str]:
        """用预先抽取的截图进行分类"""
        category_list = "\n".join(
            f"- {key}: {desc}" for key, desc in CATEGORY_DESCRIPTIONS.items()
        )
        prompt = (
            f"请根据以下视频截图判断这个视频最适合哪个分类。\n"
            f"可选分类：\n{category_list}\n\n"
            f"请只回复分类的 key 名称（如 survival、heartwarming 等），不要回复任何其他内容。"
        )
        ai_reply = self.classifier._call_ollama(prompt, images_b64)
        if not ai_reply:
            return None
        ai_reply = ai_reply.lower()
        for key in CATEGORY_DESCRIPTIONS:
            if key in ai_reply:
                return key
        return None

    def _ai_title_only(self, images_b64: List[str], category: str) -> Optional[str]:
        """用预先抽取的截图生成标题"""
        category_desc = CATEGORY_DESCRIPTIONS.get(category, category)
        prompt = (
            f"你是一个视频标题生成器。根据以下视频截图和分类信息，生成一个吸引人的标题。\n\n"
            f"分类: {category} - {category_desc}\n"
            f"语言: {self.config.title_language}\n"
        )
        if self.config.title_rules:
            prompt += f"\n用户规则:\n{self.config.title_rules}\n"
        prompt += "\n请只回复标题本身，不要加引号或其他内容。"

        ai_reply = self.classifier._call_ollama(prompt, images_b64)
        if not ai_reply:
            return None
        # 去除引号
        if len(ai_reply) >= 2 and ai_reply[0] in ('"', "'", '\u201c') and ai_reply[-1] in ('"', "'", '\u201d'):
            ai_reply = ai_reply[1:-1].strip()
        if ai_reply:
            print(f"✅ AI 生成标题: {ai_reply}")
        return ai_reply if ai_reply else None

    def watch_and_process(self):
        """监控文件夹并处理新视频"""
        print(f"\n{'='*60}")
        print(f"👁️ 开始监控文件夹...")
        print(f"   将视频放入 input 文件夹的分类子文件夹中")
        print(f"   按 Ctrl+C 停止")
        print(f"{'='*60}\n")

        self.is_running = True

        try:
            while self.is_running:
                videos = self._find_new_videos()

                for video in videos:
                    self.process_video(video)

                time.sleep(self.config.watch_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 已停止监控")
            self.is_running = False

    def rename_output_videos(self) -> int:
        """重新用 AI 分类并命名 output 文件夹中的所有视频"""
        videos = [
            f for f in self.config.output_folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.config.video_extensions
        ]

        if not videos:
            print("📂 output 文件夹中没有视频文件")
            return 0

        print(f"\n找到 {len(videos)} 个视频，开始重新分类并命名...")
        print("=" * 60)

        renamed_count = 0
        for i, video_path in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}] 📹 {video_path.name}")

            # 抽取截图
            frames = self.classifier.extract_frames(video_path)
            if not frames:
                print(f"  ⚠️ 无法抽取帧，跳过")
                continue

            images_b64 = self.classifier._frames_to_base64(frames)
            self.classifier.cleanup_frames()

            if not images_b64:
                print(f"  ⚠️ 截图转换失败，跳过")
                continue

            # AI 分类 + 生成标题（一次调用）
            category, ai_title = self._ai_classify_and_title(images_b64)

            if not category:
                category = "mixed"

            if not ai_title:
                print(f"  ⚠️ AI 标题生成失败，使用标题库 fallback")
                ai_title = self.title_manager.get_next_title(category, shuffle=True)

            if not ai_title:
                print(f"  ⚠️ 无法生成标题，跳过")
                continue

            # 生成新文件名
            safe_title = sanitize_filename(ai_title)
            new_filename = f"{safe_title}{video_path.suffix}"
            new_path = self.config.output_folder / new_filename

            # 避免重名
            counter = 1
            while new_path.exists() and new_path != video_path:
                new_path = self.config.output_folder / f"{safe_title}_{counter}{video_path.suffix}"
                counter += 1

            # 跳过同名
            if new_path == video_path:
                print(f"  ℹ️ 文件名相同，跳过")
                continue

            # 重命名
            video_path.rename(new_path)
            renamed_count += 1
            cat_desc = CATEGORY_DESCRIPTIONS.get(category, category)
            print(f"  ✅ 分类: {category} ({cat_desc})")
            print(f"  ✅ 新名称: {new_path.name}")

        print(f"\n{'='*60}")
        print(f"✨ 完成! 共重命名 {renamed_count}/{len(videos)} 个视频")
        return renamed_count

    def process_single(self, video_path: Path, category: str) -> bool:
        """处理单个视频（手动指定分类）"""
        if not video_path.exists():
            print(f"❌ 文件不存在: {video_path}")
            return False

        # 临时移动到对应分类文件夹
        folder_name = CATEGORY_FOLDER_MAP.get(category)
        if not folder_name:
            print(f"❌ 无效的分类: {category}")
            return False

        target_folder = self.config.input_folder / folder_name
        target_path = target_folder / video_path.name

        shutil.copy(str(video_path), str(target_path))
        return self.process_video(target_path)


# ============================================================
# 命令行界面
# ============================================================

def print_categories():
    """打印所有可用分类"""
    print("\n📂 可用的视频分类:")
    print("="*60)
    for i, (category, folder_name) in enumerate(CATEGORY_FOLDER_MAP.items(), 1):
        if category == "auto":
            print(f"  {folder_name}/")
            print(f"     🤖 AI 自动分类 (Ollama 视觉分析)")
        else:
            style = TITLE_STYLES.get(category, {})
            name = style.get("name", category)
            count = len(style.get("titles", []))
            print(f"  {folder_name}/")
            print(f"     {name} ({count} 个标题)")
    print("="*60)


def load_config_from_file() -> ProcessorConfig:
    """从 config.json 加载配置"""
    config = ProcessorConfig()
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "cleaner_type" in data:
                config.cleaner_type = data["cleaner_type"]
            if "watch_interval" in data:
                config.watch_interval = data["watch_interval"]
            if "ollama_model" in data:
                config.ollama_model = data["ollama_model"]
            if "ollama_url" in data:
                config.ollama_url = data["ollama_url"]
            if "ai_title_enabled" in data:
                config.ai_title_enabled = data["ai_title_enabled"]
            if "title_language" in data:
                config.title_language = data["title_language"]
            if "title_rules" in data:
                config.title_rules = data["title_rules"]
            if "sora_wm_path" in data:
                config.sora_wm_path = data["sora_wm_path"]
        except Exception as e:
            print(f"⚠️ 读取 config.json 失败，使用默认配置: {e}")
    return config


def save_config_to_file(config: ProcessorConfig):
    """将 ProcessorConfig 写回 config.json"""
    config_path = Path(__file__).parent / "config.json"
    data = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass

    data["cleaner_type"] = config.cleaner_type
    data["watch_interval"] = config.watch_interval
    data["ollama_model"] = config.ollama_model
    data["ollama_url"] = config.ollama_url
    data["ai_title_enabled"] = config.ai_title_enabled
    data["title_language"] = config.title_language
    data["title_rules"] = config.title_rules

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def ai_title_settings(config: ProcessorConfig):
    """AI 标题生成设置子选单"""
    while True:
        ai_status = "✅ 已启用" if config.ai_title_enabled else "❌ 已停用"
        print(f"\n{'='*60}")
        print("=== AI 标题设置 ===")
        print(f"当前状态: {ai_status}")
        print(f"当前语言: {config.title_language}")
        if config.title_rules:
            print(f"当前规则: {config.title_rules}")
        else:
            print("当前规则: (未设定)")
        print(f"{'='*60}")

        print("\n[1] 启用/停用 AI 标题生成")
        print("[2] 设置标题语言")
        print("[3] 设置标题规则")
        print("[4] 返回主选单")

        sub_choice = input("\n请选择 [1-4]: ").strip()

        if sub_choice == "1":
            config.ai_title_enabled = not config.ai_title_enabled
            save_config_to_file(config)
            state = "启用" if config.ai_title_enabled else "停用"
            print(f"\n✅ AI 标题生成已{state}")

        elif sub_choice == "2":
            print("\n选择标题语言:")
            print("  [1] English (en)")
            print("  [2] 中文 (zh)")
            print("  [3] 自定义")
            lang_choice = input("请选择 [1-3]: ").strip()
            if lang_choice == "1":
                config.title_language = "en"
            elif lang_choice == "2":
                config.title_language = "zh"
            elif lang_choice == "3":
                custom_lang = input("请输入语言标识 (如 ja, ko, fr): ").strip()
                if custom_lang:
                    config.title_language = custom_lang
            else:
                print("❌ 无效选择")
                continue
            save_config_to_file(config)
            print(f"\n✅ 标题语言已设置为: {config.title_language}")

        elif sub_choice == "3":
            print("\n请输入标题生成规则 (输入 END 单独一行结束):")
            print("例如: 标题要有 emoji 开头、要能吸引点击、不超过 60 字符")
            print("-" * 40)
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            config.title_rules = "\n".join(lines).strip()
            save_config_to_file(config)
            if config.title_rules:
                print(f"\n✅ 标题规则已保存:\n{config.title_rules}")
            else:
                print("\n✅ 标题规则已清除")

        elif sub_choice == "4":
            break
        else:
            print("❌ 无效选择")


def main():
    """主函数"""
    print("="*60)
    print("🎬 视频自动处理器 / Video Auto Processor")
    print("   自动去水印 + 智能重命名 + AI 自动分类")
    print("="*60)

    config = load_config_from_file()
    processor = VideoProcessor(config)

    print_categories()

    print("\n📋 使用说明:")
    print("  1. 将视频放入 input 文件夹中对应分类的子文件夹")
    print("     或放入 00_自动分类/ 让 AI 自动判断分类")
    print("  2. 程序会自动检测并处理")
    print("  3. 处理完成的视频会出现在 output 文件夹")
    print(f"\n🤖 AI 分类模型: {config.ollama_model} ({config.ollama_url})")
    print(f"\n📁 输入文件夹: {config.input_folder}")
    print(f"📁 输出文件夹: {config.output_folder}")

    while True:
        # 显示 AI 标题状态
        ai_status = "✅ 已启用" if config.ai_title_enabled else "❌ 已停用"
        print(f"\n🤖 AI 标题生成: {ai_status} | 语言: {config.title_language}")
        if config.title_rules:
            rules_preview = config.title_rules[:50] + ("..." if len(config.title_rules) > 50 else "")
            print(f"   规则: {rules_preview}")

        print("\n选择模式:")
        print("  [1] 自动监控模式 (推荐)")
        print("  [2] 处理单个视频")
        print("  [3] 仅创建文件夹结构")
        print("  [4] 设定 AI 标题规则")
        print("  [5] 重新命名 output 视频 (AI 分类+标题)")
        print("  [6] 退出程序")

        choice = input("\n请选择 [1-6]: ").strip()

        if choice == "1":
            # 选择清除模型
            print("\n选择水印清除模型:")
            print("  [1] LAMA (快速，推荐)")
            print("  [2] E2FGVI_HQ (高质量，较慢)")
            model_choice = input("请选择 [1-2]: ").strip()

            if model_choice == "2":
                config.cleaner_type = "e2fgvi_hq"
                processor = VideoProcessor(config)

            processor.watch_and_process()

        elif choice == "2":
            video_input = input("\n请输入视频路径: ").strip().strip('"')
            video_path = Path(video_input)

            print("\n选择视频分类:")
            categories = list(CATEGORY_FOLDER_MAP.keys())
            for i, cat in enumerate(categories, 1):
                if cat == "auto":
                    print(f"  [{i}] 🤖 AI 自动分类")
                else:
                    style = TITLE_STYLES.get(cat, {})
                    print(f"  [{i}] {style.get('name', cat)}")

            cat_choice = input(f"\n请选择 [1-{len(categories)}]: ").strip()
            try:
                category = categories[int(cat_choice) - 1]
                processor.process_single(video_path, category)
            except (ValueError, IndexError):
                print("❌ 无效选择")

        elif choice == "3":
            print("\n✅ 文件夹结构已创建完成!")
            print(f"   请将视频放入: {config.input_folder}")

        elif choice == "4":
            ai_title_settings(config)

        elif choice == "5":
            videos = [
                f for f in config.output_folder.iterdir()
                if f.is_file() and f.suffix.lower() in config.video_extensions
            ] if config.output_folder.exists() else []
            print(f"\n📂 output 文件夹中有 {len(videos)} 个视频")
            if videos:
                for v in videos:
                    print(f"   - {v.name}")
                confirm = input(f"\n确认要重新命名这 {len(videos)} 个视频吗? [y/N]: ").strip().lower()
                if confirm == "y":
                    processor.rename_output_videos()
                else:
                    print("已取消")

        elif choice == "6":
            print("\n👋 再见!")
            break

        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    main()
