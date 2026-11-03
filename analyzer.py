import re
from collections import Counter

from pypinyin import Style, lazy_pinyin


# 基于十三辙归类。v 代表 ü；er 单列；e 与 o/uo 同归坡梭辙。
RHYME_GROUP_MAP = {
    "发花": ["a", "ia", "ua"],
    "坡梭": ["o", "uo", "e"],
    "乜斜": ["ie", "ve"],
    "姑苏": ["u"],
    "一七": ["i", "v", "er"],
    "怀来": ["ai", "uai"],
    "灰堆": ["ei", "ui"],
    "遥条": ["ao", "iao"],
    "油求": ["ou", "iu"],
    "言前": ["an", "ian", "uan", "van"],
    "人辰": ["en", "in", "un", "vn"],
    "江阳": ["ang", "iang", "uang"],
    "中东": ["eng", "ing", "ong", "iong"],
}

FINAL_TO_GROUP = {
    final: group
    for group, finals in RHYME_GROUP_MAP.items()
    for final in finals
}

# 每个辙口使用不同颜色；浅色标签改用深色文字，保证可读性。
GROUP_STYLE_MAP = {
    "发花": {"background": "#D1495B", "text": "#FFFFFF"},
    "坡梭": {"background": "#2A9D8F", "text": "#FFFFFF"},
    "乜斜": {"background": "#F4D35E", "text": "#1F2937"},
    "姑苏": {"background": "#264653", "text": "#FFFFFF"},
    "一七": {"background": "#F77F00", "text": "#FFFFFF"},
    "怀来": {"background": "#7B2CBF", "text": "#FFFFFF"},
    "灰堆": {"background": "#D63384", "text": "#FFFFFF"},
    "遥条": {"background": "#0077B6", "text": "#FFFFFF"},
    "油求": {"background": "#0F766E", "text": "#FFFFFF"},
    "言前": {"background": "#E9C46A", "text": "#1F2937"},
    "人辰": {"background": "#5A189A", "text": "#FFFFFF"},
    "江阳": {"background": "#B23A48", "text": "#FFFFFF"},
    "中东": {"background": "#4361EE", "text": "#FFFFFF"},
    "unknown": {"background": "#6B7280", "text": "#FFFFFF"},
}

# 保留旧常量名称，避免其他代码导入时失效。
GROUP_COLOR_MAP = {
    group: style["background"] for group, style in GROUP_STYLE_MAP.items()
}

# 常见古入声字只用于提示，不强制改变现代普通话平仄判定。
COMMON_RUSHENG = set(
    "白黑一不月雪国积极吃出发达杂擦杀刹扎拔跋八捌答搭塌拉邋"
    "十石食实识蚀直值植殖职汁只织执质侄疾嫉集籍及级极急"
    "吉即革隔格阁各恶客刻克嘿北百柏伯迫拍魄麦脉摘宅窄"
    "竹烛逐嘱瞩筑祝足族卒促簇速肃宿缩叔熟淑术述束"
    "日入肉六陆绿录鹿碌目木沐牧幕慕墓募"
    "曲局菊橘屈掘崛倔绝爵嚼觉角脚却确雀鹊"
    "学削薛穴血七漆乞迄泣乙壹逸溢译驿翼屋沃握幄"
)

CJK_CHAR_PATTERN = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


def normalize_line(line):
    """返回适合展示和分析的单行文本。"""
    return str(line or "").strip()


def find_last_chinese_char(line):
    """忽略句尾标点、英文、数字和表情，返回最后一个中文字符。"""
    for char in reversed(normalize_line(line)):
        if CJK_CHAR_PATTERN.fullmatch(char):
            return char
    return None


def get_final_info(char):
    """返回 (韵母, 辙口, 声调, 是否入声)，无法识别时安全降级。"""
    if not char or not CJK_CHAR_PATTERN.fullmatch(char):
        return "N/A", "unknown", "0", False

    finals = lazy_pinyin(
        char,
        style=Style.FINALS,
        strict=False,
        errors="ignore",
    )
    tones = lazy_pinyin(
        char,
        style=Style.TONE3,
        strict=False,
        errors="ignore",
    )

    final = finals[0] if finals else "N/A"
    tone_pinyin = tones[0] if tones else ""
    tone = tone_pinyin[-1] if tone_pinyin and tone_pinyin[-1].isdigit() else "0"
    rhyme_group = FINAL_TO_GROUP.get(final, "unknown")

    return final, rhyme_group, tone, char in COMMON_RUSHENG


def _tone_type(tone):
    if tone in {"1", "2"}:
        return "平"
    if tone in {"3", "4"}:
        return "仄"
    if tone == "0":
        return "轻声"
    return "未知"


def analyze_lyrics(lines):
    """分析歌词，并保持原有七项返回值结构兼容。"""
    results = []
    rhyme_groups = []
    tones_list = []

    for original_index, raw_line in enumerate(lines, start=1):
        line = normalize_line(raw_line)
        if not line:
            continue

        last_char = find_last_chinese_char(line)
        final, rhyme_group, tone, is_rusheng = get_final_info(last_char)
        tone_type = _tone_type(tone)
        rusheng_note = "（入声，古仄）" if is_rusheng and tone_type == "平" else ""
        style = GROUP_STYLE_MAP.get(rhyme_group, GROUP_STYLE_MAP["unknown"])

        results.append(
            {
                "line_idx": original_index,
                "text": line,
                "last_char": last_char or "未识别",
                "final": final,
                "rhyme_group": rhyme_group,
                "tone": tone,
                "tone_type": tone_type,
                "rusheng_note": rusheng_note,
                "color": style["background"],
                "text_color": style["text"],
                "recognized": rhyme_group != "unknown",
            }
        )
        rhyme_groups.append(rhyme_group)
        tones_list.append(tone_type)

    valid_groups = [group for group in rhyme_groups if group != "unknown"]
    if valid_groups and results:
        group_counts = Counter(valid_groups)
        main_group, main_count = group_counts.most_common(1)[0]
        coverage = main_count / len(results)
        score = round(coverage * 100)
        ranked_groups = group_counts.most_common(2)
        secondary = ranked_groups[1] if len(ranked_groups) > 1 else None
    else:
        main_group, score, secondary = None, 0, None

    if score >= 85:
        level = "主韵高度集中"
    elif score >= 60:
        level = "主韵清晰，存在换辙"
    else:
        level = "换辙较多，建议分段查看"

    cliché_words = set("心情行明爱怀天眼泪碎飞醉美谁对寂寞落错破哭独")
    cliché_phrases_by_group = {
        "言前": ["永远", "从前", "改变", "想念", "看见", "听见", "时间", "瞬间"],
        "中东": ["梦中", "心动", "相拥", "天空", "风中", "其中", "最终"],
        "一七": ["自己", "记忆", "过去", "距离", "呼吸", "唯一", "意义"],
        "发花": ["刹那", "年华", "牵挂", "放下", "害怕", "回答"],
        "遥条": ["拥抱", "微笑", "知道", "寻找", "燃烧", "逃跑"],
    }
    cliché_phrases_general = ["的心", "的爱", "的眼", "的泪", "是谁", "到底", "什么", "真的"]

    suspicious = []
    for index, result in enumerate(results):
        if result["last_char"] in cliché_words:
            window = results[max(0, index - 1) : index + 2]
            same_group_high_frequency = [
                item
                for item in window
                if item["rhyme_group"] == result["rhyme_group"]
                and item["last_char"] in cliché_words
            ]
            if len(same_group_high_frequency) >= 3:
                reason = (
                    f"结尾的「{result['last_char']}」属于高频韵脚，附近连续多行使用同辙口，"
                    "可能产生堆砌感。"
                )
            else:
                reason = (
                    f"结尾的「{result['last_char']}」属于高频韵脚，建议检查是否为了押韵"
                    "牺牲了表达。"
                )
            suspicious.append((result, reason))

    for result in results:
        phrase = next(
            (
                candidate
                for candidate in cliché_phrases_by_group.get(result["rhyme_group"], [])
                if candidate in result["text"]
            ),
            None,
        )
        phrase_kind = "辙口常见"
        if not phrase:
            phrase = next(
                (candidate for candidate in cliché_phrases_general if candidate in result["text"]),
                None,
            )
            phrase_kind = "通用常见"

        if phrase:
            suspicious.append(
                (
                    result,
                    f"句中包含「{phrase}」（{phrase_kind}表达），建议结合上下文检查语义是否自然。",
                )
            )

    return score, level, results, suspicious, tones_list, main_group, secondary
