import streamlit as st
import pandas as pd
import random
import os
import time
import streamlit.components.v1 as components

# 1. 页面基础配置
st.set_page_config(page_title="西部计划特训", page_icon="📖", layout="centered")

# ================= UI 美改区 =================
custom_css = """
<style>
/* 选项卡片美化 */
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
/* 隐藏无用的锚点 */
a.st-emotion-cache-1f35sxg {display: none;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. 核心大纲配置 (完全对应 1_1 到 1_7)
SYLLABUS = {
    "一、理论学习与政治素养": {
        "📊 【本章全真模拟】": "1_all.csv",
        "1️⃣ 习近平新时代中国特色社会主义思想": "1_1.csv",
        "2️⃣ 党的二十大及二十届历次全会精神": "1_2.csv",
        "3️⃣ 四史、中华民族发展史": "1_3.csv",
        "4️⃣ 习近平总书记关于青年工作重要思想": "1_4.csv",
        "5️⃣ 青年工作核心要义与实践 (侧重基层)": "1_5.csv",
        "6️⃣ 二十届全会精神深度解读 (侧重新政)": "1_6.csv",
        "7️⃣ 红色精神": "1_7.csv"
    },
    "二、青年志愿服务": {
        "📊 【本章全真模拟】": "2_all.csv",
        "❤️ 青年志愿服务-精神内涵": "2_1.csv",
        "✉️ 青年志愿服务-重要贺信精神": "2_2.csv",
        "💌 青年志愿服务-重要回信精神": "2_3.csv",
        "⚖️ 青年志愿服务-基本原则": "2_4.csv",
        "⏳ 志愿服务-发展历程": "2_5.csv"
    },
    "三、卫国戍边与西部计划": {
        "📊 【本章全真模拟】": "3_all.csv",
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
        "📊 【本章全真模拟】": "4_all.csv",
        "📍 边境地区基本情况": "4_1.csv",
        "🎤 总书记视察吉林重要讲话": "4_2.csv",
        "📝 省委十二届八次全会精神": "4_3.csv",
        "📈 省“十五五”规划纲要": "4_4.csv",
        "🏞️ 省情概况": "4_5.csv",
        "🌲 长白山保护开发区": "4_6.csv"
    },
    "五、核心简答题必背 (分点版)": {
        "🧠 简答1：理论学习与政治素养": "简答1_理论学习与政治素养.csv",
        "🤝 简答2：青年志愿服务": "简答2_青年志愿服务.csv",
        "🛡️ 简答3：卫国戍边与西部计划": "简答3_卫国戍边与西部计划.csv",
        "🏞️ 简答4：吉林省省情": "简答4_吉林省省情.csv"
    }
}


# 3. 工具函数
@st.cache_data(ttl=600)
def load_data(file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, file_path)
    if os.path.exists(full_path):
        return pd.read_csv(full_path)
    return pd.DataFrame()


def clean_duplicates(file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, file_path)
    if os.path.exists(full_path):
        df = pd.read_csv(full_path)
        if '题目' in df.columns:
            df['check'] = df['题目'].astype(str).str.replace(r'[^\w\u4e00-\u9fa5]', '', regex=True)
            df_cleaned = df.drop_duplicates(subset=['check'], keep='first').drop(columns=['check'])
            if len(df) > len(df_cleaned):
                df_cleaned.to_csv(full_path, index=False, encoding='utf-8-sig')
                return len(df) - len(df_cleaned)
    return 0


# 4. 会话状态初始化
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'wrong_q_indices' not in st.session_state: st.session_state.wrong_q_indices = set()
if 'show_exp' not in st.session_state: st.session_state.show_exp = False
if 'answered_count' not in st.session_state: st.session_state.answered_count = 0
if 'correct_count' not in st.session_state: st.session_state.correct_count = 0


def init_new_quiz(num_questions):
    st.session_state.current_idx = 0
    st.session_state.show_exp = False
    st.session_state.wrong_q_indices = set()
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
        st.toast("✅ 轮回结束，开始新的一轮！")
    st.rerun()


# ================== 第一层：导航首页 ==================
if st.session_state.page == 'home':
    st.title("📚 西部计划·冲刺特训")
    st.info("💡 建议每次更新题库后，点击右上角 ⋮ 选 'Clear cache' 以获取最新内容。")

    for main_cat, sub_cats in SYLLABUS.items():
        with st.expander(f"📂 {main_cat}", expanded=False):
            for sub_name, file_path in sub_cats.items():
                if st.button(sub_name, key=file_path, use_container_width=True):
                    df_temp = load_data(file_path)
                    if df_temp.empty:
                        st.warning(f"🚧 题库文件 {file_path} 尚未就绪。")
                    else:
                        st.session_state.current_set_name = sub_name
                        st.session_state.current_set_path = file_path
                        init_new_quiz(len(df_temp))
                        st.session_state.page = 'quiz'
                        st.rerun()

# ================== 第二层：答题界面 ==================
elif st.session_state.page == 'quiz':
    df = load_data(st.session_state.current_set_path)

    with st.sidebar:
        if st.button("⬅️ 返回主菜单", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

        st.header("📊 本轮实时数据")
        if st.session_state.answered_count > 0:
            acc = int((st.session_state.correct_count / st.session_state.answered_count) * 100)
            speed = int((time.time() - st.session_state.start_time) / st.session_state.answered_count)
            st.metric("🎯 准确率", f"{acc}%")
            st.metric("⏱️ 速度", f"{speed}秒/题")

        st.write("---")
        st.write(f"❌ 当前错题数：{len(st.session_state.wrong_q_indices)}")

        # 【新增：错题导出功能】
        if len(st.session_state.wrong_q_indices) > 0:
            wrong_df = df.iloc[list(st.session_state.wrong_q_indices)]
            # 导出为 CSV
            csv_data = wrong_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 导出本轮错题本",
                data=csv_data,
                file_name=f"错题本_{st.session_state.current_set_name}.csv",
                mime="text/csv",
                use_container_width=True
            )
            if st.button("🗑️ 清空本次错题记录", use_container_width=True):
                st.session_state.wrong_q_indices.clear()
                st.rerun()

        st.write("---")
        if st.button("🧹 清理文件重复题", use_container_width=True):
            num = clean_duplicates(st.session_state.current_set_path)
            st.success(f"清理了 {num} 道题！请重进生效。")

    st.subheader(f"📍 {st.session_state.current_set_name}")

    # 10分钟倒计时
    TOTAL_S = 600
    rem_s = TOTAL_S - int(time.time() - st.session_state.start_time)
    timer_color = "#FF4B4B" if rem_s > 0 else "#666666"
    timer_html = f"<div style='text-align:center;color:{timer_color};background:#FFEBEB;padding:10px;border-radius:8px;'>⏳ 倒计时：{max(0, rem_s // 60)}分{max(0, rem_s % 60)}秒</div>"
    st.markdown(timer_html, unsafe_allow_html=True)

    questions_list = st.session_state.shuffled_indices
    total_q = len(questions_list)
    curr_idx_in_list = st.session_state.current_idx

    st.progress((curr_idx_in_list + 1) / total_q)
    st.caption(f"题目进度：{curr_idx_in_list + 1} / {total_q}")

    q_data = df.iloc[questions_list[curr_idx_in_list]]
    st.markdown(f"#### {q_data['题目']}")

    options = [str(q_data['选项A']).strip(), str(q_data['选项B']).strip(), str(q_data['选项C']).strip()]
    ans_raw = str(q_data['正确答案']).strip().upper()

    # 判题逻辑
    correct_text = options[0] if 'A' in ans_raw else (options[1] if 'B' in ans_raw else options[2])
    if ans_raw in options: correct_text = ans_raw

    choice = st.radio("选择你的答案：", options, index=None, key=f"q_{curr_idx_in_list}")

    if choice:
        if choice == correct_text:
            st.success("✅ 回答正确！")
            if not st.session_state.show_exp:
                st.session_state.answered_count += 1
                st.session_state.correct_count += 1
                st.session_state.show_exp = True
            time.sleep(0.8)  # 缩短一点等待时间，刷题更爽
            next_question(total_q)
        else:
            if "掌握" in correct_text and ("不会" in choice or "模糊" in choice):
                st.error("⚠️ 已加入错题集。")
            else:
                st.error(f"❌ 答错了。正确答案：{correct_text}")

            if not st.session_state.show_exp:
                st.session_state.answered_count += 1
                st.session_state.wrong_q_indices.add(questions_list[curr_idx_in_list])
                st.session_state.show_exp = True

            st.info(f"💡 解析：\n\n{q_data['解析']}")
            if st.button("下一题 ➡️", use_container_width=True):
                next_question(total_q)