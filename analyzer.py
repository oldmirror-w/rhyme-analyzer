from pypinyin import lazy_pinyin, Style
from collections import Counter

# 规则库：主元音分类
NUCLEUS_MAP = {
    "a": ["a", "ia", "ua", "ai", "uai", "an", "ian", "uan", "ang", "iang", "uang"],
    "o": ["o", "uo", "ao", "iao", "ou", "iou", "ong", "iong"],
    "e": ["e", "ie", "ve", "ei", "ui", "en", "in", "un", "eng", "ing"],
    "i": ["i", "er"],
    "u": ["u"],
    "ü": ["v", "ve", "un"]
}

COLOR_MAP = {
    "a": "#FF6B6B", "o": "#4ECDC4", "e": "#FFE66D", 
    "i": "#1A535C", "u": "#FF9F1C", "ü": "#9B5DE5", "unknown": "#E0E0E0"
}

def get_final_info(char):
    f_raw = lazy_pinyin([char], style=Style.FINALS, errors='ignore')[0]
    t = lazy_pinyin([char], style=Style.TONE3, errors='ignore')[0]
    tone = t[-1] if t and t[-1].isdigit() else "0"
    
    nucleus = "unknown"
    for key, val_list in NUCLEUS_MAP.items():
        if f_raw in val_list:
            nucleus = key
            break
    return f_raw, nucleus, tone

def analyze_lyrics(lines):
    results = []
    nuclei_list = []
    tones_list = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        
        last_char = line[-1]
        # 👇 新增：如果不是中文字符（比如数字或标点），直接跳过或给默认值
        f_raw, nucleus, tone = get_final_info(last_char)
        if not f_raw: 
            f_raw, nucleus, tone = "N/A", "unknown", "0"
        
        # 声调可视化映射（1/2声为平，3/4声为仄）
        tone_type = "平" if tone in ["1", "2"] else "仄" if tone in ["3", "4"] else "轻声"
        
        results.append({
            "line_idx": i + 1,
            "text": line,
            "last_char": last_char,
            "final": f_raw,
            "nucleus": nucleus,
            "tone": tone,
            "tone_type": tone_type,
            "color": COLOR_MAP.get(nucleus, COLOR_MAP["unknown"])
        })
        nuclei_list.append(nucleus)
        tones_list.append(tone_type)

    # === 算分逻辑：韵脚聚类法 ===
    nucleus_counts = Counter(nuclei_list)
    top_nuclei = [item[0] for item in nucleus_counts.most_common(2) if item[0] != "unknown"]
    
    match_count = 0
    if top_nuclei:
        for n in nuclei_list:
            if n in top_nuclei:
                match_count += 1
        score = int((match_count / len(nuclei_list)) * 100)
    else:
        score = 0

    if score >= 75:
        level = "非常工整"
    elif score >= 50:
        level = "尚可，有换韵"
    else:
        level = "偏松，押韵较散"

    # 强行凑韵检测
    CLICHE_WORDS = set("心情行明爱怀天眼泪碎飞醉美谁对寂寞落错破哭独")
    CLICHE_PHRASES = ["的心", "的爱", "的眼", "的泪", "是谁", "到底", "什么", "真的"]
    
    SUSPICIOUS = []
    for res in results:
        text = res["text"]
        last_char = res["last_char"]
        
        phrase_found = next((p for p in CLICHE_PHRASES if p in text), None)
        
        if last_char in CLICHE_WORDS:
            SUSPICIOUS.append((res, f"结尾的「{last_char}」是极度高频的凑韵词，容易显得俗套。"))
        elif phrase_found:
            SUSPICIOUS.append((res, f"句内包含「{phrase_found}」，可能为了凑字数或韵脚牺牲了语感。"))
            
    # 注意这行！必须返回 5 个变量！
    return score, level, results, SUSPICIOUS, tones_list