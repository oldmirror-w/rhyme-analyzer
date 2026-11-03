import html
from collections import Counter

import streamlit as st

from analyzer import analyze_lyrics


APP_VERSION = "v0.5"
SAMPLE_LYRICS = """我把旧梦留在风中
你说永远却没有回声
黎明醒来我仍然心动
最后一句写给夜空"""

st.set_page_config(
    page_title="中文歌词韵律诊断器",
    page_icon="🎵",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f8f9fa;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1 {
            line-height: 1.2 !important;
            overflow-wrap: anywhere;
        }

        .lyric-card {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-left: 5px solid #6b7280;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        }

        .line-number {
            width: 30px;
            flex: 0 0 30px;
            color: #6b7280;
            font-size: 12px;
        }

        .lyric-body {
            min-width: 0;
            flex: 1 1 auto;
        }

        .lyric-text {
            color: #1f2937;
            font-size: 16px;
            font-weight: 600;
            overflow-wrap: anywhere;
        }

        .lyric-meta {
            margin-top: 4px;
            color: #6b7280;
            font-size: 12px;
        }

        .lyric-tags {
            display: flex;
            flex: 0 0 auto;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 6px;
        }

        .tag {
            display: inline-flex;
            align-items: center;
            min-height: 26px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            white-space: nowrap;
        }

        .tag-ping {
            background-color: #15803d;
            color: #ffffff;
        }

        .tag-ze {
            background-color: #6d28d9;
            color: #ffffff;
        }

        .tag-neutral {
            background-color: #4b5563;
            color: #ffffff;
        }

        .score-panel {
            margin-bottom: 24px;
            padding: 26px;
            color: #ffffff;
            text-align: center;
            background: linear-gradient(135deg, #4f46e5 0%, #6d28d9 100%);
            border-radius: 10px;
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.16);
        }

        .score-title {
            margin: 0;
            font-size: 18px;
            font-weight: 700;
        }

        .score-value {
            margin: 6px 0;
            font-size: 54px;
            font-weight: 800;
            line-height: 1;
        }

        .score-level {
            margin: 0;
            font-size: 17px;
            font-weight: 600;
        }

        .score-detail {
            margin: 10px 0 0;
            color: rgba(255, 255, 255, 0.88);
            font-size: 13px;
        }

        .distribution-row {
            display: grid;
            grid-template-columns: 52px minmax(0, 1fr) 46px;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
        }

        .distribution-label,
        .distribution-value {
            color: #374151;
            font-size: 13px;
            font-weight: 600;
        }

        .distribution-value {
            text-align: right;
        }

        .distribution-track {
            height: 12px;
            overflow: hidden;
            background: #e5e7eb;
            border-radius: 999px;
        }

        .distribution-fill {
            height: 100%;
            min-width: 4px;
            border-radius: 999px;
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 1rem 1rem 2rem;
            }

            h1 {
                font-size: 2rem !important;
            }

            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 0.75rem !important;
            }

            [data-testid="column"] {
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }

            textarea {
                min-height: 250px !important;
                height: 250px !important;
            }

            .lyric-card {
                align-items: flex-start;
                flex-wrap: wrap;
                gap: 8px;
                padding: 12px;
            }

            .lyric-body {
                width: calc(100% - 42px);
            }

            .lyric-tags {
                width: 100%;
                justify-content: flex-start;
                padding-left: 42px;
            }

            .score-panel {
                padding: 22px 14px;
            }

            .score-value {
                font-size: 46px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_sample():
    st.session_state.lyrics_input = SAMPLE_LYRICS
    st.session_state.analysis = None
    st.session_state.analyzed_text = ""


def clear_input():
    st.session_state.lyrics_input = ""
    st.session_state.analysis = None
    st.session_state.analyzed_text = ""


st.session_state.setdefault("lyrics_input", "")
st.session_state.setdefault("analysis", None)
st.session_state.setdefault("analyzed_text", "")

st.title(f"🎵 中文歌词韵律诊断器 {APP_VERSION}")
st.markdown("分析主韵集中度、十三辙分布与句尾平仄，帮助你定位需要重新推敲的歌词。")
st.caption("结果基于普通话读音和规则模型，适合作为修改参考，不代表文学质量的绝对判断。")

input_column, output_column = st.columns([1, 1.45], gap="large")

with input_column:
    st.subheader("输入歌词")
    st.text_area(
        "每行一句，支持带标点的歌词：",
        key="lyrics_input",
        height=360,
        placeholder="我看到\n久违的晴朗啊。\n又在黎明醒来！",
    )

    diagnose_button = st.button(
        "开始分析",
        type="primary",
        use_container_width=True,
    )

    sample_column, clear_column = st.columns(2)
    with sample_column:
        st.button("加载示例", on_click=load_sample, use_container_width=True)
    with clear_column:
        st.button("清空", on_click=clear_input, use_container_width=True)

    if diagnose_button:
        current_text = st.session_state.lyrics_input.strip()
        lines = [line.strip() for line in current_text.splitlines() if line.strip()]

        if len(lines) < 2:
            st.warning("请至少输入两行有效歌词。")
        else:
            with st.spinner("正在分析韵脚与平仄..."):
                st.session_state.analysis = analyze_lyrics(lines)
                st.session_state.analyzed_text = current_text

with output_column:
    analysis = st.session_state.analysis

    if not analysis:
        st.info("分析结果将在这里显示。你可以先加载示例，快速查看完整效果。")
        st.markdown(
            """
            结果包括：

            - 主韵集中度及计算依据
            - 每一行的十三辙与平仄标签
            - 辙口分布和声调比例
            - 高频韵脚与常见表达风险提示
            """
        )
    else:
        score, level, results, suspicious, tones, main_group, secondary = analysis
        current_text = st.session_state.lyrics_input.strip()
        if current_text != st.session_state.analyzed_text:
            st.info("歌词已经修改。当前结果仍对应上一次文本，请点击“开始分析”更新。")

        recognized_count = sum(result["recognized"] for result in results)
        main_count = sum(
            result["rhyme_group"] == main_group for result in results
        ) if main_group else 0
        secondary_text = ""
        if secondary:
            secondary_text = f" ｜ 次要辙口：{secondary[0]}（{secondary[1]} 行）"

        main_group_text = main_group or "未识别"
        score_detail = (
            f"主辙口：{html.escape(main_group_text)}，占 {main_count}/{len(results)} 行"
            f" ｜ 成功识别 {recognized_count}/{len(results)} 行"
            f"{html.escape(secondary_text)}"
        )

        st.markdown(
            f"""
            <div class="score-panel">
                <p class="score-title">主韵集中度</p>
                <div class="score-value">{score}<span style="font-size: 22px; font-weight: 500;"> 分</span></div>
                <p class="score-level">{html.escape(level)}</p>
                <p class="score-detail">{score_detail}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("韵脚与平仄")
        cards = ['<div class="lyric-list">']
        for result in results:
            if result["tone_type"] == "平":
                tone_class = "tag-ping"
            elif result["tone_type"] == "仄":
                tone_class = "tag-ze"
            else:
                tone_class = "tag-neutral"

            tone_label = result["tone_type"] + result.get("rusheng_note", "")
            cards.append(
                f'<div class="lyric-card" style="border-left-color: {result["color"]};">'
                f'<div class="line-number">{result["line_idx"]:02d}</div>'
                '<div class="lyric-body">'
                f'<div class="lyric-text">{html.escape(result["text"])}</div>'
                f'<div class="lyric-meta">韵脚：{html.escape(result["last_char"])} ｜ '
                f'韵母：{html.escape(result["final"])}</div>'
                '</div>'
                '<div class="lyric-tags">'
                f'<span class="tag" style="background-color: {result["color"]}; '
                f'color: {result["text_color"]};">'
                f'辙：{html.escape(result["rhyme_group"])}</span>'
                f'<span class="tag {tone_class}">{html.escape(tone_label)}</span>'
                '</div>'
                '</div>'
            )
        cards.append("</div>")
        st.markdown("".join(cards), unsafe_allow_html=True)

        st.subheader("声调概览")
        tone_counts = Counter(tones)
        tone_columns = st.columns(4)
        tone_columns[0].metric("平声", tone_counts.get("平", 0))
        tone_columns[1].metric("仄声", tone_counts.get("仄", 0))
        tone_columns[2].metric("轻声", tone_counts.get("轻声", 0))
        tone_columns[3].metric("未识别", tone_counts.get("未知", 0))

        st.subheader("辙口分布")
        group_counts = Counter(
            result["rhyme_group"]
            for result in results
            if result["rhyme_group"] != "unknown"
        )
        if group_counts:
            maximum_count = max(group_counts.values())
            distribution_rows = []
            for group, count in group_counts.most_common():
                group_result = next(
                    result for result in results if result["rhyme_group"] == group
                )
                width = round(count / maximum_count * 100)
                distribution_rows.append(
                    '<div class="distribution-row">'
                    f'<div class="distribution-label">{html.escape(group)}</div>'
                    '<div class="distribution-track">'
                    f'<div class="distribution-fill" style="width: {width}%; '
                    f'background: {group_result["color"]};"></div>'
                    '</div>'
                    f'<div class="distribution-value">{count} 行</div>'
                    '</div>'
                )
            st.markdown("".join(distribution_rows), unsafe_allow_html=True)
        else:
            st.warning("暂未识别出有效的中文韵脚，请检查歌词内容。")

        st.subheader("表达风险提示")
        if not suspicious:
            st.success("没有发现明显的高频韵脚或常见套话风险。")
        else:
            for item, reason in suspicious:
                st.warning(
                    f"第 {item['line_idx']} 行：{item['text']}\n\n{reason}"
                )
