import streamlit as st
import pandas as pd
import random
import os
import time
import streamlit.components.v1 as components

# 1. 页面基础配置
st.set_page_config(page_title="西部计划特训", page_icon="📖", layout="centered")

# ================= UI 魔改区 =================
custom_css = """
<style>
/* 放大单选框的点击区域，防误触 */
div[role="radiogroup"] > label {
    padding: 15px !important;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    margin-bottom: 12px;
    background-color: #ffffff;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
}
div[role="radiogroup"] > label:hover {
    border-color: #FF7F50;
    background-color: #fff8f5;
}
/* 按钮美化 */
div.stButton > button:first-child {
    border-radius: 8px;
    font-weight: bold;
}
/* 隐藏无用的锚点链接 */
a.st-emotion-cache-1f35sxg {display: none;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ============================================

# 2. 题库配置大纲 (完全匹配你要求的下划线数字文件名)
SYLLABUS = {
    "一、理论学习与政治素养": {
        "📖 习近平新时代中国特色社会主义思想": "1_1.csv",
        "🚩 党的二十大及二十届历次全会精神": "1_2.csv",
        "📜 四史、中华民族发展史": "1_3.csv",
        "🌟 总书记关于青年工作重要思想": "1_4.csv",
        "🔥 红色精神、吉林省情": "1_5.csv"
    },
    "二、青年志愿服务": {
        "❤️ 青年志愿服务-精神内涵": "2_1.csv",
        "✉️ 青年志愿服务-总书记重要贺信精神": "2_2.csv",
        "💌 青年志愿服务-总书记重要回信精神": "2_3.csv",
        "⚖️ 青年志愿服务-志愿服务基本原则": "2_4.csv",
        "⏳ 志愿服务-发展历程": "2_5.csv"
    },
    "三、卫国戍边与西部计划": {
        "🏢 西部计划组织管理": "3_1.csv",
        "⏳ 西部计划发展历程": "3_2.csv",
        "🗺️ 西部计划服务领域": "3_3.csv",
        "📋 志愿者管理办法": "3_4.csv",
        "🛡️ 卫国戍边政策": "3_5.csv",
        "🤝 民族工作重要思想": "3_6.csv",
        "🪖 国防教育": "3_7.csv",
        "🔒 保密教育": "3_8.csv",
        "⚠️ 安全自护教育": "3_9.csv"
    },
    "四、吉林省省情": {
        "📍 边境地区基本情况": "4_1.csv",
        "🎤 总书记视察吉林重要讲话精神": "4_2.csv",
        "📝 吉林省委十二届八次全会精神": "4_3.csv",
        "📈 省“十五五”规划纲要": "4_4.csv",
        "🏞️ 省情概况": "4_5.csv",
        "🌲 长白山保护开发区": "4_6.csv"
    },
    "五、核心简答题必背专区": {
        "🧠 简答1：理论学习与政治素养": "简答1_理论学习与政治素养.csv",
        "🤝 简答2：青年志愿服务": "简答2_青年志愿服务.csv",
        "🛡️ 简答3：卫国戍边与西部计划": "简答3_卫国戍边与西部计划.csv",
        "🏞️ 简答4：吉林省省情": "简答4_吉林省省情.csv"
    }
}


@st.cache_data
def load_data(file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, file_path)
    if os.path.exists(full_path):
        return pd.read_csv(full_path)
    else:
        return pd.DataFrame()


# 3. 初始化会话状态
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_set_name' not in st.session_state: st.session_state.current_set_name = ""
if 'current_set_path' not in st.session_state: st.session_state.current_set_path = ""
if 'current_idx' not in st.session_state: st.session_state.current_idx = 0
if 'wrong_q_indices' not in st.session_state: st.session_state.wrong_q_indices = set()
if 'show_exp' not in st.session_state: st.session_state.show_exp = False
if 'mode' not in st.session_state: st.session_state.mode = '全题库 (随机乱序)'
if 'shuffled_indices' not in st.session_state: st.session_state.shuffled_indices = []

if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'answered_count' not in st.session_state: st.session_state.answered_count = 0
if 'correct_count' not in st.session_state: st.session_state.correct_count = 0


def init_new_quiz(num_questions):
    st.session_state.current_idx = 0
    st.session_state.show_exp = False
    st.session_state.wrong_q_indices = set()
    st.session_state.mode = '全题库 (随机乱序)'
    st.session_state.start_time = time.time()
    st.session_state.answered_count = 0
    st.session_state.correct_count = 0
    indices = list(range(num_questions))
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices


def next_question(total_len):
    st.session_state.show_exp = False
    if st.session_state.current_idx < total_len - 1:
        st.session_state.current_idx += 1
    else:
        st.session_state.current_idx = 0
        st.toast("✅ 已经刷到底啦！")
    st.rerun()


# ================== 第一层网页：选套题 ==================
if st.session_state.page == 'home':
    st.title("📚 西部计划·冲刺特训")
    st.write("欢迎来到 **Joanne的专属备考平台**，请选择今天要突破的专项：")
    st.write("---")

    for main_cat, sub_cats in SYLLABUS.items():
        with st.expander(f"📂 {main_cat}", expanded=False):
            for sub_name, file_path in sub_cats.items():
                if st.button(sub_name, key=file_path, use_container_width=True):
                    df_temp = load_data(file_path)
                    if df_temp.empty:
                        st.warning(f"🚧 专属题库 **{file_path}** 正在录入中...")
                    else:
                        st.session_state.current_set_name = f"{main_cat} - {sub_name}"
                        st.session_state.current_set_path = file_path
                        init_new_quiz(len(df_temp))
                        st.session_state.page = 'quiz'
                        st.rerun()

# ================== 第二层网页：做题 ==================
elif st.session_state.page == 'quiz':
    df = load_data(st.session_state.current_set_path)

    with st.sidebar:
        if st.button("⬅️ 返回重选专项", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

        st.header("📊 学习数据看板")
        if st.session_state.answered_count > 0:
            acc = int((st.session_state.correct_count / st.session_state.answered_count) * 100)
            elapsed_time = time.time() - st.session_state.start_time
            speed = int(elapsed_time / st.session_state.answered_count)
        else:
            acc, speed = 0, 0

        col_a, col_b = st.columns(2)
        col_a.metric("🎯 正确率", f"{acc}%")
        col_b.metric("⏱️ 答题速度", f"{speed}秒/题")

        st.write("---")
        mode = st.radio("选择模式：", ['全题库 (随机乱序)', '错题本'])
        if mode != st.session_state.mode:
            st.session_state.mode = mode
            st.session_state.current_idx = 0
            st.session_state.show_exp = False
            st.rerun()

        st.write("---")
        st.write(f"❌ 当前模块错题数：**{len(st.session_state.wrong_q_indices)}**")

        if len(st.session_state.wrong_q_indices) > 0:
            wrong_df = df.iloc[list(st.session_state.wrong_q_indices)]
            csv_data = wrong_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 导出错题本", data=csv_data, file_name=f"慧子错题本.csv", mime="text/csv",
                               use_container_width=True)

    st.subheader(st.session_state.current_set_name)

    # 10分钟倒计时 JS 注入
    TOTAL_SECONDS = 600
    elapsed_seconds = int(time.time() - st.session_state.start_time)
    timer_html = f"""
    <div id="timer-container" style="text-align:center; font-size:18px; font-weight:bold; color:#FF4B4B; background-color:#FFEBEB; padding:10px; border-radius:8px; margin-bottom:15px; border:1px dashed #FF4B4B;">
        ⏳ <span id="timer-title">专项突破倒计时：</span><span id="countdown"></span>
    </div>
    <script>
    var totalSeconds = {TOTAL_SECONDS}; var elapsed = {elapsed_seconds};
    var timerId = setInterval(function() {{
        elapsed++; var diff = totalSeconds - elapsed;
        if (diff >= 0) {{
            var m = Math.floor(diff / 60); var s = Math.floor(diff % 60);
            document.getElementById("countdown").innerHTML = m + " 分 " + s + " 秒";
        }} else {{
            var over = Math.abs(diff); var m = Math.floor(over / 60); var s = Math.floor(over % 60);
            document.getElementById("timer-container").style.backgroundColor = "#ffcccc";
            document.getElementById("timer-container").style.border = "2px solid red";
            document.getElementById("countdown").innerHTML = "<span style='color:red; font-size:20px; font-weight:900;'>⚠️ 已超时：" + m + " 分 " + s + " 秒</span>";
        }}
    }}, 1000);
    </script>
    """
    components.html(timer_html, height=75)

    if st.session_state.mode == '全题库 (随机乱序)':
        questions_list = st.session_state.shuffled_indices
    else:
        questions_list = list(st.session_state.wrong_q_indices)

    if not questions_list:
        st.success("目前没有题目哦！继续保持！🎉")
    else:
        total_q = len(questions_list)
        st.progress((st.session_state.current_idx + 1) / total_q)
        st.caption(f"当前进度: {st.session_state.current_idx + 1} / {total_q}")

        real_idx = questions_list[st.session_state.current_idx]
        q_data = df.iloc[real_idx]
        st.markdown(f"#### {q_data['题目']}")

        options = [str(q_data['选项A']).strip(), str(q_data['选项B']).strip(), str(q_data['选项C']).strip()]
        correct_raw = str(q_data['正确答案']).strip().upper()

        # 智能识别正确文本（解决简答题比对问题）
        if correct_raw in options:
            correct_text = correct_raw
        elif 'A' in correct_raw:
            correct_text = options[0]
        elif 'B' in correct_raw:
            correct_text = options[1]
        elif 'C' in correct_raw:
            correct_text = options[2]
        else:
            correct_text = options[0]

        choice = st.radio("请点击选项卡片作答：", options, index=None, key=f"q_{real_idx}_{st.session_state.mode}")

        if choice:
            if choice == correct_text:
                st.success(f"✅ 回答正确！")
                if not st.session_state.show_exp:
                    st.session_state.answered_count += 1
                    st.session_state.correct_count += 1
                    st.session_state.show_exp = True
                time.sleep(1.2)
                next_question(total_q)
            else:
                # 判定为错（含简答题选了模糊/不会）
                if "掌握" in correct_text and ("模糊" in choice or "不会" in choice):
                    st.error(f"⚠️ 已记入错题本，请仔细背诵参考答案。")
                else:
                    st.error(f"❌ 回答错误。正确答案是：**{correct_text}**")

                if not st.session_state.show_exp:
                    st.session_state.answered_count += 1
                    st.session_state.wrong_q_indices.add(real_idx)
                    st.session_state.show_exp = True

                st.info(f"💡 解析/答案：\n\n{q_data['解析']}")
                if st.button("我已记住，下一题 ➡️", use_container_width=True, type="primary"):
                    next_question(total_q)