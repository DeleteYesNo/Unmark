# -*- coding: utf-8 -*-
"""
⚡ 快速启动 - 一键开始自动处理
Quick Start - One click to start auto processing
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from auto_processor import VideoProcessor, ProcessorConfig, print_categories

def main():
    print("="*60)
    print("⚡ 快速启动模式 / Quick Start Mode")
    print("="*60)

    config = ProcessorConfig()
    config.cleaner_type = "lama"  # 使用快速模式

    processor = VideoProcessor(config)

    print_categories()

    print("\n✅ 使用 LAMA 模型 (快速模式)")
    print(f"\n📁 将视频放入: {config.input_folder}")
    print("   └─ 选择对应的分类子文件夹")
    print(f"\n📁 处理完成后会出现在: {config.output_folder}")

    input("\n按回车键开始监控...")

    processor.watch_and_process()


if __name__ == "__main__":
    main()
