# -*- coding: utf-8 -*-
"""
批量视频重命名工具 - 多风格表情符号标题
Video Batch Renamer with Multiple Emoji Styles
"""

import os
import random
from pathlib import Path
from typing import List, Dict

# ============================================================
# 🎬 标题风格库 / Title Style Library
# ============================================================

TITLE_STYLES: Dict[str, Dict] = {
    "survival": {
        "name": "🦁 生存惊险型 / Survival & Thrilling",
        "description": "适合野生动物、惊险时刻、求生类视频",
        "titles": [
            "😱 One Wrong Move and It Was Over",
            "😰 This Could've Ended Very Badly",
            "🦁 A Predator Got Way Too Close…",
            "⚡ Seconds From Disaster",
            "🔥 This Moment Changed Everything",
            "💀 He Wasn't Supposed to Survive This",
            "😬 Too Close for Comfort",
            "⚡ A Split Second Decision",
            "😱 This Was Almost the End",
            "😲 No One Expected This Outcome",
            "🧘 Staying Calm Saved His Life",
            "💪 This Is How He Survived",
            "🚫 He Didn't Run… And It Worked",
            "🧠 The Smartest Move in This Situation",
            "✨ One Calm Decision Made the Difference",
            "🎯 Survival Is About Control",
            "😰 Panic Would've Ended It",
            "🤯 He Did Exactly What You're Not Supposed to Do",
            "✅ This Trick Actually Works",
            "🏆 A Perfect Survival Instinct",
            "🤔 What Would You Do Here?",
            "❓ Would You Run or Freeze?",
            "😨 Most People Would Panic",
            "🪞 Be Honest… Could You Stay Calm?",
            "💭 Would You Have Made It?",
            "🫣 Could You Handle This Moment?",
            "⚠️ Not Everyone Would Survive This",
            "🧪 This Situation Tests Your Instincts",
            "❔ Would You Know What to Do?",
            "☝️ Only One Choice Works Here",
            "📹 This Was Caught by Accident",
            "🌍 A Real Moment in the Wild",
            "🎬 This Wasn't Planned",
            "📅 Just Another Day… Until This Happened",
            "🌿 Nature Doesn't Warn You",
            "🎥 Real Life Has No Retakes",
            "🌪️ This Is Why Nature Is Unpredictable",
            "📸 A Rare Moment Caught on Camera",
            "🚨 This Is Not a Movie Scene",
            "🎞️ Real Survival Footage",
            "😳 Too Close",
            "😮‍💨 Almost Didn't Make It",
            "⚠️ This Was Risky",
            "⏰ Bad Timing",
            "📍 Wrong Place, Wrong Time",
            "🦎 Instinct Took Over",
            "🍀 He Got Lucky",
            "🏃 Barely Escaped",
            "😅 That Was Close",
            "🔴 Survival Mode",
        ]
    },
    "reversal": {
        "name": "🔥 反轉型 / Plot Twist (最吸流量)",
        "description": "适合结局反转、出人意料的内容",
        "titles": [
            "😳❤️ Everyone Thought This Would End Badly…",
            "😱➡️🥹 This Looked Scary Until the Last Second",
            "🐾❤️ Not the Ending Anyone Expected",
            "😮‍💨✨ From Tension to Pure Warmth",
            "😳💞 This Changed the Mood Completely",
            "🤯 Plot Twist You Didn't See Coming",
            "😲➡️😊 Watch Until the End",
            "💔➡️❤️ From Scary to Heartwarming",
            "🎭 Everything Changed in One Second",
            "😰➡️🥹 The Twist That Got Everyone",
        ]
    },
    "heartwarming": {
        "name": "🥹 溫馨感動型 / Heartwarming",
        "description": "适合温暖、治愈、感人的内容",
        "titles": [
            "🤍🐾 When Fear Turns Into Trust",
            "🥹❤️ A Moment That Melted Everyone's Heart",
            "🐺🤍 This Is Why Animals Are Amazing",
            "✨🌿 Unexpected Kindness in the Wild",
            "🫶🐾 Sometimes Instincts Are Gentle",
            "💕 Pure Love in One Moment",
            "🥹 This Restored My Faith",
            "🤍 The Sweetest Thing You'll See Today",
            "😭❤️ I Wasn't Ready for This",
            "🌸 Nature's Gentle Side",
        ]
    },
    "shorts": {
        "name": "📱 Shorts 專用短標題 / Short Titles",
        "description": "适合 YouTube Shorts、TikTok 等短视频",
        "titles": [
            "🥹 That Turned Out So Wholesome",
            "❤️ Wait for the Ending",
            "😳 This Was Not What I Expected",
            "🤍 Pure Heartwarming Moment",
            "😊 From Shock to Smile",
            "😱 OMG",
            "🔥 Insane",
            "💀 No Way",
            "😮 Wait What",
            "🤯 Mind Blown",
            "❤️ So Cute",
            "😳 Unexpected",
            "✨ Beautiful",
            "🥹 Emotional",
            "😅 That Was Close",
        ]
    },
    "candid": {
        "name": "🎥 偷拍真實感風 / Candid & Real",
        "description": "适合真实记录、偶然拍到的内容",
        "titles": [
            "🎥😮 This Was Caught on Camera",
            "🐾✨ A Rare Moment Like This",
            "🌍 Real Life Isn't Always What You Think",
            "🤍 Just Watch What Happens",
            "🥹 This Moment Felt Unreal",
            "📹 Accidentally Recorded This",
            "🎬 Unscripted Moment",
            "📸 Once in a Lifetime Shot",
            "🌿 Nature Caught Off Guard",
            "🎥 You Won't Believe This Is Real",
        ]
    },
    "fantasy_mysterious": {
        "name": "🐉 神秘生物型 / Mysterious Creatures",
        "description": "适合神秘、未知的奇幻生物",
        "titles": [
            "🐉 A creature no one has seen before.",
            "👁️ It watched from the shadows.",
            "🌫️ Something moved in the mist.",
            "🔮 They said it was just a legend.",
            "🌙 It only appears at midnight.",
            "👀 We were not alone.",
            "🕯️ The ancient texts were right.",
            "🌑 Born from darkness itself.",
            "✨ A being of pure magic.",
            "🦴 Older than time itself.",
            "🌿 The forest has a guardian.",
            "💫 It glowed like starlight.",
            "🪶 Wings that defy explanation.",
            "🔥 Eyes like burning embers.",
            "❄️ Cold radiated from its presence.",
            "⚡ Thunder followed its steps.",
            "🌊 It rose from the depths.",
            "🏔️ The mountain was alive.",
            "🌸 Beauty beyond this world.",
            "💀 Death walks among us.",
            "🐾 Tracks that vanish into nothing.",
            "🌪️ It commanded the storm.",
            "🎭 A face that shifts like water.",
            "🗝️ The keeper of ancient secrets.",
            "🌟 Celestial. Eternal. Unknowable.",
        ]
    },
    "fantasy_discovery": {
        "name": "🌟 奇幻發現型 / Fantasy Discovery",
        "description": "适合发现、初遇奇幻生物的时刻",
        "titles": [
            "🌟 The moment I first saw it.",
            "😲 This shouldn't exist.",
            "📖 The legends were true.",
            "🗺️ Found in an unexplored realm.",
            "🔍 What I discovered changes everything.",
            "🚪 Beyond that door was something impossible.",
            "🌄 At dawn, it revealed itself.",
            "🏛️ Hidden for a thousand years.",
            "💎 A treasure no gold could match.",
            "🌈 Colors I've never seen before.",
            "🧭 The map led me here.",
            "📜 Written in ancient scrolls.",
            "⛰️ Deep in the forgotten caves.",
            "🌲 The old forest keeps secrets.",
            "🏝️ On an island time forgot.",
            "🌌 Falling from the stars.",
            "🕳️ What emerged from the portal.",
            "🗿 Awakened after centuries of sleep.",
            "🌺 Blooming only once in a lifetime.",
            "🦋 Evolution took a different path here.",
        ]
    },
    "fantasy_bond": {
        "name": "🤝 羈絆連結型 / Creature Bond",
        "description": "适合人与奇幻生物之间的情感连结",
        "titles": [
            "🤝 It chose me.",
            "💞 A bond stronger than blood.",
            "🐾❤️ We found each other.",
            "🌙 Together under the same moon.",
            "✨ It understood my soul.",
            "🫂 Two outcasts becoming family.",
            "👁️ It saw through my fears.",
            "🔗 Connected by fate.",
            "🌟 My guardian from another world.",
            "💫 It healed what words couldn't.",
            "🦋 Gentle despite its power.",
            "🤲 It trusted me first.",
            "🌸 Friendship blooms in strange places.",
            "🛡️ It would protect me with its life.",
            "🌊 Calming the storm within me.",
            "🔥 Warming my coldest days.",
            "🌿 Growing together, changing together.",
            "💜 Love needs no common language.",
            "🌙 My midnight companion.",
            "⭐ Following me like a star.",
        ]
    },
    "fantasy_majestic": {
        "name": "👑 威嚴壯麗型 / Majestic & Grand",
        "description": "适合展现奇幻生物威严、壮观的时刻",
        "titles": [
            "👑 Bow before the ancient one.",
            "🐉 Wings that block the sun.",
            "⚔️ A force no army could stop.",
            "🏔️ Larger than mountains.",
            "🌊 The ocean trembled at its call.",
            "⚡ Power that shakes the heavens.",
            "🔥 Flames that could melt kingdoms.",
            "❄️ Winter bows to its will.",
            "🌪️ The sky itself obeys.",
            "💀 Even death respects it.",
            "👁️ One glance and you freeze.",
            "🦁 The true king of this realm.",
            "✨ Radiance that blinds mortals.",
            "🌑 Darkness incarnate.",
            "☀️ Brighter than the sun itself.",
            "🗡️ Undefeated. Unmatched. Unstoppable.",
            "🏛️ Worshipped as a god.",
            "🌌 Older than the stars.",
            "💎 Scales worth more than empires.",
            "🎆 Its arrival shook the world.",
        ]
    },
    "fantasy_cute": {
        "name": "🥺 可愛奇幻型 / Cute Fantasy",
        "description": "适合可爱、萌系的奇幻生物",
        "titles": [
            "🥺 Too cute to be real.",
            "✨ A tiny ball of magic.",
            "🌸 Soft. Fluffy. Magical.",
            "💕 My heart can't handle this.",
            "🦋 Small but full of wonder.",
            "🍄 Found this little one hiding.",
            "🌟 Pocket-sized magic.",
            "😭 I would die for this creature.",
            "🫧 Floating like a dream.",
            "🌈 Made of pure happiness.",
            "🐾 Those tiny paws though.",
            "👀 Big eyes, bigger heart.",
            "🍃 Nature's cutest creation.",
            "💫 Sparkles wherever it goes.",
            "🎀 Adorable beyond words.",
            "🌙 My sleepy little guardian.",
            "☁️ Softer than clouds.",
            "🍬 Sweet as sugar.",
            "🐣 Just hatched and already precious.",
            "💖 Cuteness overload.",
        ]
    },
    "fantasy_dark": {
        "name": "🖤 黑暗奇幻型 / Dark Fantasy",
        "description": "适合黑暗、神秘、略带恐怖的奇幻生物",
        "titles": [
            "🖤 Beauty in darkness.",
            "💀 Not evil. Just different.",
            "🌑 The night has a protector.",
            "👁️ Watching from the void.",
            "🕷️ Fear is just misunderstanding.",
            "🦇 Creatures of the eternal night.",
            "⛓️ Bound by ancient curses.",
            "🗡️ Dangerous doesn't mean cruel.",
            "🌫️ Lost in the realm between.",
            "💔 Broken but still beautiful.",
            "🔮 Dark magic runs through its veins.",
            "🕯️ A light in the abyss.",
            "☠️ Death is not the end.",
            "🌙 Children of the moon.",
            "🩸 Blood and beauty intertwined.",
            "⚰️ Risen from forgotten graves.",
            "👻 More spirit than flesh.",
            "🌪️ Chaos in its purest form.",
            "🖤 Embrace the shadows.",
            "🔥 Hellfire has a gentle side.",
        ]
    },
    "fantasy_elemental": {
        "name": "🌊 元素生物型 / Elemental Creatures",
        "description": "适合火、水、风、土等元素生物",
        "titles": [
            "🔥 Born from eternal flames.",
            "🌊 The ocean given form.",
            "🌪️ Wind that became alive.",
            "🏔️ Earth's living heart.",
            "⚡ Lightning in creature form.",
            "❄️ Winter's frozen soul.",
            "☀️ A piece of the sun.",
            "🌙 Moonlight made physical.",
            "🌸 Spring's gentle spirit.",
            "🍂 Autumn's wandering child.",
            "💎 Crystal given consciousness.",
            "🌋 Magma flows through its veins.",
            "🌈 Formed from pure light.",
            "🌑 Shadow given shape.",
            "⭐ Stardust come alive.",
            "🌿 The forest breathes through it.",
            "🌊❄️ Where ice meets the sea.",
            "🔥💨 Fire dances with wind.",
            "⛈️ The storm personified.",
            "🌍 The planet's last guardian.",
        ]
    },
    "fantasy_lore": {
        "name": "📜 世界觀傳說型 / Lore & Legend",
        "description": "适合展示奇幻世界观、背景故事",
        "titles": [
            "📜 The prophecy spoke of this day.",
            "🏛️ Temples built in its honor.",
            "📖 Chapter one of an ancient tale.",
            "🗺️ Marked on no map.",
            "⏳ Waiting since the first age.",
            "👑 The last of its royal bloodline.",
            "🔮 Seers predicted its return.",
            "⚔️ Wars were fought over it.",
            "💀 Civilizations fell seeking it.",
            "🌟 Born when the stars aligned.",
            "🏔️ The mountain's eternal secret.",
            "🌊 Sailors whispered of this creature.",
            "🌲 The forest elders remember.",
            "🔥 Forged in the world's creation.",
            "❄️ Frozen since the ice age.",
            "📿 Sacred to forgotten tribes.",
            "🗝️ The key to everything.",
            "🌙 Blessed by the moon goddess.",
            "☀️ Child of the sun deity.",
            "🌌 Before time had a name.",
        ]
    },
    "fantasy_pov": {
        "name": "👁️ 生物視角型 / Creature's POV",
        "description": "从奇幻生物的视角讲述",
        "titles": [
            "👁️ I have watched for centuries.",
            "🐾 They don't understand me.",
            "🌙 The night is my home.",
            "💭 I remember when gods walked here.",
            "🦋 Freedom is all I seek.",
            "😔 Loneliness is my oldest friend.",
            "🔥 My fire is not for destruction.",
            "❄️ I am cold, but I feel warmth.",
            "🌊 The deep is peaceful.",
            "🏔️ From up here, everything is small.",
            "🌿 I protect what cannot protect itself.",
            "⚡ Power is a burden.",
            "👑 I never asked to be worshipped.",
            "💔 They hunted my kind to extinction.",
            "🌟 I was here before your ancestors.",
            "🕯️ Even monsters need light.",
            "🤍 I only wanted to be loved.",
            "🗡️ I fight because I must.",
            "🌸 Beauty fades. I remain.",
            "🖤 Call me monster. I call myself survivor.",
        ]
    },
    "deep": {
        "name": "🖤 深層反思型 / Deep Reflection",
        "description": "适合被误解的生物、哲理性内容",
        "titles": [
            "🖤 It was never a monster.",
            "🌑 Different does not mean dangerous.",
            "🌌 Some beings don't belong anywhere.",
            "🪐 This world wasn't made for it.",
            "🔮 Not created to be understood.",
            "🌙 Misunderstood from the start.",
            "🖤 They only see what they fear.",
            "🌑 Born different. Judged forever.",
            "🌌 It never asked to be feared.",
            "🪐 Alone in a world that doesn't understand.",
        ]
    },
    "quiet_warmth": {
        "name": "🤍 靜謐溫暖型 / Quiet Warmth",
        "description": "适合安静、治愈、温柔的时刻",
        "titles": [
            "🤍 You are not alone.",
            "🫂 Sometimes, being held is enough.",
            "💫 No words. Just warmth.",
            "🌸 A quiet moment between two souls.",
            "🕊️ Even wild hearts need rest.",
            "🤍 Silence speaks louder here.",
            "🌙 Peace in an unexpected place.",
            "💫 Some connections need no words.",
            "🕊️ A gentle moment in chaos.",
            "🌸 Rest, little one.",
        ]
    },
    "sad_reality": {
        "name": "🥀 悲傷現實型 / Sad Reality",
        "description": "适合现实、沉重、引人深思的内容",
        "titles": [
            "🥀 No one noticed.",
            "💔 It didn't get saved.",
            "🖤 Cute doesn't mean happy.",
            "🌧️ This is how it survived.",
            "🤫 It learned to stay quiet.",
            "🥀 Not every story has a happy ending.",
            "💔 They never came back for it.",
            "🖤 Surviving isn't the same as living.",
            "🌧️ It smiled, but no one saw the pain.",
            "🤫 Some cries are silent.",
        ]
    },
    "mixed": {
        "name": "🎲 随机混合 / Random Mix",
        "description": "从所有风格中随机选择",
        "titles": []  # Will be populated dynamically
    }
}


def get_all_titles() -> List[str]:
    """获取所有风格的标题"""
    all_titles = []
    for style_key, style_data in TITLE_STYLES.items():
        if style_key != "mixed":
            all_titles.extend(style_data["titles"])
    return all_titles


def sanitize_filename(name: str) -> str:
    """移除文件名中的非法字符"""
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        name = name.replace(char, '')
    return name.strip()


def get_video_files(folder: Path) -> list:
    """获取文件夹中的所有视频文件"""
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    videos = []
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in video_extensions:
            videos.append(f)
    return sorted(videos)


def display_styles():
    """显示所有可用的标题风格"""
    print("\n" + "="*60)
    print("🎨 可用标题风格 / Available Title Styles")
    print("="*60)

    for i, (key, style) in enumerate(TITLE_STYLES.items(), 1):
        title_count = len(style["titles"]) if key != "mixed" else len(get_all_titles())
        print(f"\n  [{i}] {style['name']}")
        print(f"      {style['description']}")
        print(f"      📝 {title_count} 个标题")


def get_titles_for_style(style_key: str, shuffle: bool = False) -> List[str]:
    """获取指定风格的标题列表"""
    if style_key == "mixed":
        titles = get_all_titles()
    else:
        titles = TITLE_STYLES[style_key]["titles"].copy()

    if shuffle:
        random.shuffle(titles)

    return titles


def preview_rename(folder: Path, titles: List[str]) -> list:
    """预览重命名结果"""
    videos = get_video_files(folder)
    if not videos:
        print("❌ 未找到视频文件")
        return []

    if len(videos) > len(titles):
        print(f"⚠️ 警告: 视频数量 ({len(videos)}) 超过标题数量 ({len(titles)})")

    rename_plan = []
    for i, video in enumerate(videos):
        if i < len(titles):
            new_name = sanitize_filename(titles[i]) + video.suffix
            rename_plan.append((video, video.parent / new_name))

    return rename_plan


def rename_videos(folder: Path, titles: List[str], dry_run: bool = True) -> None:
    """
    批量重命名视频

    Args:
        folder: 包含视频的文件夹路径
        titles: 标题列表
        dry_run: 如果为 True，只预览不实际重命名
    """
    rename_plan = preview_rename(folder, titles)

    if not rename_plan:
        return

    print("\n" + "="*60)
    print("📋 重命名计划 / Rename Plan")
    print("="*60)

    for i, (old_path, new_path) in enumerate(rename_plan, 1):
        print(f"\n{i:02d}. {old_path.name}")
        print(f"    → {new_path.name}")

    print("\n" + "="*60)

    if dry_run:
        print("\n🔍 预览模式 - 未实际重命名")
        return

    # 实际重命名
    print("\n🚀 开始重命名...")
    success_count = 0
    for old_path, new_path in rename_plan:
        try:
            if new_path.exists():
                print(f"⚠️ 跳过 (文件已存在): {new_path.name}")
                continue
            old_path.rename(new_path)
            print(f"✅ {old_path.name} → {new_path.name}")
            success_count += 1
        except Exception as e:
            print(f"❌ 重命名失败: {old_path.name} - {e}")

    print(f"\n✨ 完成! 成功重命名 {success_count}/{len(rename_plan)} 个文件")


def main():
    """主函数 - 交互式使用"""
    print("="*60)
    print("🎬 视频批量重命名工具 / Video Batch Renamer")
    print("   支持多种标题风格 / Multiple Title Styles")
    print("="*60)

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

    # 获取用户输入的文件夹路径
    folder_input = input("\n请输入视频文件夹路径 (或拖入文件夹): ").strip().strip('"')

    if not folder_input:
        print("❌ 未输入路径")
        return

    folder = Path(folder_input)

    if not folder.exists():
        print(f"❌ 文件夹不存在: {folder}")
        return

    if not folder.is_dir():
        print(f"❌ 不是有效的文件夹: {folder}")
        return

    # 预览
    rename_videos(folder, titles, dry_run=True)

    # 确认
    confirm = input("\n确认执行重命名? (y/n): ").strip().lower()
    if confirm == 'y':
        rename_videos(folder, titles, dry_run=False)
    else:
        print("❌ 已取消")


if __name__ == "__main__":
    main()
