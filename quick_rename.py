# -*- coding: utf-8 -*-
"""
快速重命名 - 将此脚本拖到视频文件夹上运行
Quick Rename - Drag a video folder onto this script
"""

import sys
from pathlib import Path
from rename_videos import (
    rename_videos,
    get_titles_for_style,
    display_styles,
    TITLE_STYLES,
    get_video_files,
)


def main():
    print("="*60)
    print("🎬 快速视频重命名 / Quick Video Renamer")
    print("="*60)

    if len(sys.argv) < 2:
        print("\n用法: 将视频文件夹拖到此脚本上")
        print("Usage: Drag a video folder onto this script")
        input("\n按回车键退出...")
        return

    folder = Path(sys.argv[1])

    if not folder.is_dir():
        print(f"❌ 不是有效的文件夹: {folder}")
        input("\n按回车键退出...")
        return

    videos = get_video_files(folder)
    print(f"\n📁 文件夹: {folder}")
    print(f"🎥 找到 {len(videos)} 个视频文件")

    # 显示可用风格
    display_styles()

    # 选择风格
    style_keys = list(TITLE_STYLES.keys())
    while True:
        try:
            choice = input(f"\n请选择标题风格 [1-{len(style_keys)}]: ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(style_keys):
                selected_style = style_keys[choice_idx]
                break
            else:
                print("❌ 无效选择，请重试")
        except ValueError:
            print("❌ 请输入数字")

    print(f"\n✅ 已选择: {TITLE_STYLES[selected_style]['name']}")

    # 是否随机排序
    shuffle = input("是否随机排列标题顺序? (y/n) [n]: ").strip().lower() == 'y'

    # 获取标题
    titles = get_titles_for_style(selected_style, shuffle)

    # 预览
    rename_videos(folder, titles, dry_run=True)

    # 确认
    confirm = input("\n确认执行重命名? (y/n): ").strip().lower()
    if confirm == 'y':
        rename_videos(folder, titles, dry_run=False)
    else:
        print("❌ 已取消")

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
