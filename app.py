import streamlit as st
from analyzer import analyze_lyrics

st.set_page_config(page_title="歌词多模态分析器", page_icon="🎵", layout="wide")
st.title("🎵 中文歌词多模态分析器 v0.3")
st.markdown("基于音系学与自然语言处理：量化你的歌词工整度、可视化韵脚与平仄。")

# 左右分栏布局，左边输入，右边展示结果
col_input, col_output = st.columns([1, 1.5])

with col_input:
    st.subheader("📝 输入歌词")
    text = st.text_area("每行一句，粘贴后点击诊断：", height=400, placeholder="我看到\n久违的晴朗啊\n又在黎明醒来\n...")
    diagnose_btn = st.button("开始分析", type="primary", use_container_width=True)

with col_output:
    if diagnose_btn and text.strip():
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        if len(lines) < 2:
            st.warning("⚠️ 请至少输入两行歌词。")
        else:
            score, level, results, suspicious, tones = analyze_lyrics(lines)
            
            # 顶部分数面板
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                <h2 style="margin: 0; color: white;">押韵综合评分</h2>
                <h1 style="font-size: 50px; margin: 10px 0; color: white;">{score} <span style="font-size: 20px;">分</span></h1>
                <p style="margin: 0; font-size: 18px;">{level}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 韵脚颜色可视化
            st.subheader("🎨 韵脚聚类与平仄可视化")
            
            # 重点修改了这里：把 HTML 压成一行，防止 Streamlit 渲染失败
            html_content = "<div style='display: flex; flex-direction: column; gap: 8px; font-family: sans-serif;'>"
            for res in results:
                tone_color = "#28a745" if res['tone_type'] == "平" else "#6f42c1" if res['tone_type'] == "仄" else "#6c757d"
                html_content += f"<div style='display: flex; align-items: center; background: #fff; border: 1px solid #eee; padding: 8px 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'><div style='width: 30px; color: #aaa; font-size: 12px;'>{res['line_idx']:02d}</div><div style='flex-grow: 1; font-size: 15px;'>{res['text']}</div><div style='display: flex; gap: 5px;'><span style='background: {res['color']}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;'>韵: {res['final']}</span><span style='background: {tone_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{res['tone_type']}</span></div></div>"
            html_content += "</div>"
            
            st.markdown(html_content, unsafe_allow_html=True)
            
            # 诊断结果
            st.subheader("🕵️ 凑韵诊断")
            if not suspicious:
                st.success("✅ 恭喜！没有发现明显的套话韵脚或凑韵短语，歌词很自然。")
            else:
                for item, reason in suspicious:
                    st.warning(f"**第 {item['line_idx']} 行：** {item['text']}\n\n> 💡 {reason}")
    elif diagnose_btn and not text.strip():
        st.info("请先在左侧输入歌词。")
    else:
        st.info("👈 在左侧粘贴歌词，开始你的专属诊断。")