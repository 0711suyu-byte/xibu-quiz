import streamlit as st
import pandas as pd
import random
import os
import time
import streamlit.components.v1 as components

# 1. 页面配置
st.set_page_config(page_title="西部计划特训系统", page_icon="🎯", layout="centered")

# ================= 简约设计 + Emoji 修饰 =================
st.markdown("""
<style>
    .stApp { background-color: #fcfcfc; }
    h1, h2, h3 { color: #333333 !important; font-family: 'Segoe UI', sans-serif; }

    /* 选项卡片设计 */
    div[role="radiogroup"] > label {
        padding: 14px 20px !important;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #ffffff;
        transition: all 0.2s ease;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #4dabf7;
        background-color: #f8f9fa;
    }

    /* 按钮样式 */
    div.stButton > button:first-child {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        background-color: #ffffff;
        color: #495057;
        font-weight: 500;
    }
    div.stButton > button:hover {
        border-color: #4dabf7;
        color: #228be6;
    }
</style>
""", unsafe_allow_html=True)

# 2. 题库大纲 (带 Emoji 修饰)
SYLLABUS = {
    "🏛️ 第一部分：理论学习与政治素养": {
        "📊 【本章全真模拟】": "1_all.csv",
        "1.1 习近平新时代思想": "1_1.csv",
        "1.2 二十大及全会精神": "1_2.csv",
        "1.3 四史、中华民族发展史": "1_3.csv",
        "1.4 青年工作重要思想(上)": "1_4.csv",
        "1.5 青年工作重要思想(下)": "1_5.csv",
        "1.6 二十届全会深度解读": "1_6.csv",
        "1.7 红色精神专练": "1_7.csv"
    },
    "🤝 第二部分：青年志愿服务": {
        "📊 【本章全真模拟】": "2_all.csv",
        "2.1 精神内涵": "2_1.csv",
        "2.2 重要贺信精神": "2_2.csv",
        "2.3 重要回信精神": "2_3.csv",
        "2.4 志愿服务基本原则": "2_4.csv",
        "2.5 志愿服务发展历程": "2_5.csv"
    },
    "🛡️ 第三部分：卫国戍边与西部计划": {
        "📊 【本章全真模拟】": "3_all.csv",
        "3.1 组织管理": "3_1.csv",
        "3.2 发展历程": "3_2.csv",
        "3.3 服务领域": "3_3.csv",
        "3.4 志愿者管理办法": "3_4.csv",
        "3.5 卫国戍边政策": "3_5.csv",
        "3.6 民族工作重要思想": "3_6.csv",
        "3.7 国防教育": "3_7.csv",
        "3.8 保密教育": "3_8.csv",
        "3.9 安全自护教育": "3_9.csv"
    },
    "🌲 第四部分：吉林省省情": {
        "📊 【本章全真模拟】": "4_all.csv",
        "4.1 边境地区基本情况": "4_1.csv",
        "4.2 总书记视察吉林讲话": "4_2.csv",
        "4.3 省委全会精神": "4_3.csv",
        "4.4 十五五规划纲要": "4_4.csv",
        "4.5 省情概况": "4_5.csv",
        "4.6 长白山保护开发区": "4_6.csv"
    },
    "🧠 第五部分：核心简答题背诵": {
        "📝 理论素养简答": "简答1_理论学习与政治素养.csv",
        "📝 志愿服务简答": "简答2_青年志愿服务.csv",
        "📝 西部计划简答": "简答3_卫国戍边与西部计划.csv",
        "📝 吉林省情简答": "简答4_吉林省情.csv"
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


# 4. 会话状态
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'wrong_q_indices' not in st.session_state: st.session_state.wrong_q_indices = set()
if 'show_exp' not in st.session_state: st.session_state.show_exp = False
if 'answered_count' not in st.session_state: st.session_state.answered_count = 0
if 'correct_count' not in st.session_state: st.session_state.correct_count = 0
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'losing_streak' not in st.session_state: st.session_state.losing_streak = 0


def init_new_quiz(num_questions):
    st.session_state.current_idx = 0
    st.session_state.show_exp = False
    st.session_state.wrong_q_indices = set()
    st.session_state.start_time = time.time()
    st.session_state.answered_count = 0
    st.session_state.correct_count = 0
    st.session_state.streak = 0
    st.session_state.losing_streak = 0
    indices = list(range(num_questions))
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices


def next_question(total_len):
    st.session_state.show_exp = False
    if st.session_state.current_idx < total_len - 1:
        st.session_state.current_idx += 1
    else:
        st.session_state.current_idx = 0
        st.toast("🏁 模块练习已结束")
    st.rerun()


# ================== 第一层：导航首页 ==================
if st.session_state.page == 'home':
    st.title("🚀 西部计划特训系统")
    st.write("---")

    for main_cat, sub_cats in SYLLABUS.items():
        with st.expander(main_cat, expanded=False):
            for sub_name, file_path in sub_cats.items():
                if st.button(sub_name, key=file_path, use_container_width=True):
                    df_temp = load_data(file_path)
                    if not df_temp.empty:
                        st.session_state.current_set_name = sub_name
                        st.session_state.current_set_path = file_path
                        init_new_quiz(len(df_temp))
                        st.session_state.page = 'quiz'
                        st.rerun()

# ================== 第二层：答题界面 ==================
elif st.session_state.page == 'quiz':
    df = load_data(st.session_state.current_set_path)

    with st.sidebar:
        if st.button("🏠 返回章节列表"):
            st.session_state.page = 'home'
            st.rerun()

        st.write("---")
        st.write(f"🔥 当前连对: **{st.session_state.streak}**")
        if st.session_state.answered_count > 0:
            acc = int((st.session_state.correct_count / st.session_state.answered_count) * 100)
            st.write(f"✅ 累计正确率: **{acc}%**")

        st.write("---")
        st.write(f"❌ 待巩固错题: {len(st.session_state.wrong_q_indices)}")
        if len(st.session_state.wrong_q_indices) > 0:
            wrong_df = df.iloc[list(st.session_state.wrong_q_indices)]
            csv_data = wrong_df.to_csv(index=False).encode('utf-8-sig')
            # 优化：动态文件名
            st.download_button(
                "📥 导出本章错题",
                data=csv_data,
                file_name=f"惠子的错题本_{st.session_state.current_set_name}.csv",
                mime="text/csv",
                use_container_width=True
            )

        if st.button("🧹 一键查杀重复题"):
            num = clean_duplicates(st.session_state.current_set_path)
            st.toast(f"成功清理 {num} 道重复题。")

    st.subheader(f"📍 {st.session_state.current_set_name}")

    # 倒计时
    TOTAL_S = 600
    rem_s = TOTAL_S - int(time.time() - st.session_state.start_time)
    st.markdown(
        f"<p style='text-align:right; font-size:12px; color:#999;'>⏱️ 剩余时间: {max(0, rem_s // 60)}分{max(0, rem_s % 60)}秒</p>",
        unsafe_allow_html=True)

    questions_list = st.session_state.shuffled_indices
    total_q = len(questions_list)
    curr_idx = st.session_state.current_idx

    st.progress((curr_idx + 1) / total_q)

    q_data = df.iloc[questions_list[curr_idx]]
    st.markdown(f"#### {q_data['题目']}")

    options = [str(q_data['选项A']).strip(), str(q_data['选项B']).strip(), str(q_data['选项C']).strip()]
    ans_raw = str(q_data['正确答案']).strip().upper()
    correct_text = options[0] if 'A' in ans_raw else (options[1] if 'B' in ans_raw else options[2])

    choice = st.radio("💡 请点击选项作答：", options, index=None, key=f"q_{curr_idx}")

    if choice:
        if choice == correct_text:
            if not st.session_state.show_exp:
                st.session_state.streak += 1
                st.session_state.losing_streak = 0
                st.session_state.answered_count += 1
                st.session_state.correct_count += 1
                st.session_state.show_exp = True

                # 连对激励
                if st.session_state.streak == 5:
                    st.toast("不错哦，已经连对 5 题了！ ✨")
                elif st.session_state.streak == 10:
                    st.balloons()
                    st.toast("太强了！连续 10 题全对！ 🏆")

            st.success("回答正确")
            time.sleep(0.7)
            next_question(total_q)
        else:
            if not st.session_state.show_exp:
                st.session_state.losing_streak += 1
                st.session_state.streak = 0
                st.session_state.answered_count += 1
                st.session_state.wrong_q_indices.add(questions_list[curr_idx])
                st.session_state.show_exp = True

                # 连错安慰
                if st.session_state.losing_streak == 3:
                    st.toast("没关系，这几题有点难，慢慢来 🍃")
                elif st.session_state.losing_streak >= 5:
                    st.toast("要不要喝口水休息下？记得看解析哦 ☕")

            st.error(f"判定错误。正确选项：{correct_text}")
            st.info(f"📖 【解析】\n\n{q_data['解析']}")
            if st.button("下一题 ➡️"):
                next_question(total_q)