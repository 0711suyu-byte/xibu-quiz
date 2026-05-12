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
div.stButton > button:first-child {
    border-radius: 10px;
    font-weight: bold;
}
/* 隐藏无用的锚点链接 */
a.st-emotion-cache-1f35sxg {display: none;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ============================================

# 2. 题库配置库（已更新为你定制的四套题名称）
QUIZ_SETS = {
    "第一套：理论学习与政治素养": "1.csv",
    "第二套：青年志愿服务与精神内涵": "2.csv",
    "第三套：吉林省省情": "3.csv",
    "第四套：卫国戍边与西部计划政策": "4.csv"
}


@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
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

# 记录速度和准确率的状态
if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'answered_count' not in st.session_state: st.session_state.answered_count = 0
if 'correct_count' not in st.session_state: st.session_state.correct_count = 0


def init_new_quiz(num_questions):
    st.session_state.current_idx = 0
    st.session_state.show_exp = False
    st.session_state.wrong_q_indices = set()
    st.session_state.mode = '全题库 (随机乱序)'

    # 重置学习数据
    st.session_state.start_time = time.time()
    st.session_state.answered_count = 0
    st.session_state.correct_count = 0

    indices = list(range(num_questions))
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices


# ================== 第一层网页：选套题 ==================
if st.session_state.page == 'home':
    st.title("📚 西部计划·冲刺特训")
    st.write("欢迎来到 **Joanne的专属备考平台**，请选择今天要刷的套题：")
    st.write("---")

    for set_name, file_path in QUIZ_SETS.items():
        if st.button(f"📝 {set_name}", use_container_width=True):
            df_temp = load_data(file_path)
            if df_temp.empty:
                st.error(f"⚠️ 找不到题库文件 **{file_path}**。请确保文件已上传！")
            else:
                st.session_state.current_set_name = set_name
                st.session_state.current_set_path = file_path
                init_new_quiz(len(df_temp))
                st.session_state.page = 'quiz'
                st.rerun()

# ================== 第二层网页：做题 ==================
elif st.session_state.page == 'quiz':
    df = load_data(st.session_state.current_set_path)

    # 侧边栏：学习看板与导出功能
    with st.sidebar:
        if st.button("⬅️ 返回重选套题", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

        st.header("📊 学习数据看板")

        # 计算准确率和平均速度
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
        st.write(f"❌ 当前套题错题数：**{len(st.session_state.wrong_q_indices)}**")

        # 错题导出功能
        if len(st.session_state.wrong_q_indices) > 0:
            wrong_df = df.iloc[list(st.session_state.wrong_q_indices)]
            csv_data = wrong_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 导出错题本(打印专用)",
                data=csv_data,
                file_name=f"慧子的错题本_{st.session_state.current_set_name[-4:]}.csv",
                mime="text/csv",
                use_container_width=True
            )

            if st.button("🗑️ 清空本套错题", use_container_width=True):
                st.session_state.wrong_q_indices.clear()
                st.rerun()

    st.title(st.session_state.current_set_name)

    # 动态悬浮倒计时（设为 30 分钟 = 1800 秒）
    TOTAL_SECONDS = 1800
    elapsed_seconds = int(time.time() - st.session_state.start_time)

    # 注入 Javascript 实现无刷新秒表跳动，超时变红正向计时
    timer_html = f"""
    <div id="timer-container" style="text-align: center; font-size: 18px; font-weight: bold; color: #FF4B4B; background-color: #FFEBEB; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px dashed #FF4B4B; transition: all 0.3s;">
        ⏳ <span id="timer-title">模拟考场倒计时：</span><span id="countdown"></span>
    </div>
    <script>
    var totalSeconds = {TOTAL_SECONDS};
    var elapsed = {elapsed_seconds};

    var timerId = setInterval(function() {{
        elapsed++;
        var diff = totalSeconds - elapsed;

        if (diff >= 0) {{
            var m = Math.floor(diff / 60);
            var s = Math.floor(diff % 60);
            document.getElementById("countdown").innerHTML = m + " 分 " + s + " 秒";
        }} else {{
            // 超时正向计时逻辑
            var over = Math.abs(diff);
            var m = Math.floor(over / 60);
            var s = Math.floor(over % 60);

            // 改变外观为红色加粗警告
            document.getElementById("timer-container").style.backgroundColor = "#ffcccc";
            document.getElementById("timer-container").style.border = "2px solid red";
            document.getElementById("timer-title").innerHTML = "";
            document.getElementById("countdown").innerHTML = "<span style='color: red; font-size: 20px; font-weight: 900;'>⚠️ 考试时间已到！已超时：" + m + " 分 " + s + " 秒</span>";
        }}
    }}, 1000);
    </script>
    """
    components.html(timer_html, height=75)

    # 确定当前展示哪组题
    if st.session_state.mode == '全题库 (随机乱序)':
        questions_list = st.session_state.shuffled_indices
    else:
        questions_list = list(st.session_state.wrong_q_indices)

    if not questions_list:
        if st.session_state.mode == '错题本':
            st.success("太棒啦！这套题目前没有错题，继续保持！🎉")
            st.balloons()  # 触发满分气球彩蛋！
        else:
            st.warning("当前题库暂无题目。")
    else:
        # 进度条
        progress = (st.session_state.current_idx + 1) / len(questions_list)
        st.progress(progress)
        st.caption(f"当前进度: {st.session_state.current_idx + 1} / {len(questions_list)}")

        real_idx = questions_list[st.session_state.current_idx]
        q_data = df.iloc[real_idx]

        st.markdown(f"#### {q_data['题目']}")

        options = [q_data['选项A'], q_data['选项B'], q_data['选项C']]
        correct_letter = str(q_data['正确答案']).strip()

        choice = st.radio("请点击选项卡片作答：", options, index=None, key=f"q_{real_idx}_{st.session_state.mode}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("提交并查看解析", use_container_width=True):
                if choice:
                    st.session_state.show_exp = True
                    # 记录答题数量
                    st.session_state.answered_count += 1

                    if choice.startswith(correct_letter):
                        st.session_state.correct_count += 1
                    else:
                        st.session_state.wrong_q_indices.add(real_idx)
                else:
                    st.warning("请先选择一个答案哦！")

        with col2:
            if st.button("下一题 ➡️", use_container_width=True):
                st.session_state.show_exp = False
                if st.session_state.current_idx < len(questions_list) - 1:
                    st.session_state.current_idx += 1
                else:
                    st.session_state.current_idx = 0
                    st.toast("✅ 已经刷到底啦！")
                st.rerun()

        # 解析区
        if st.session_state.show_exp:
            st.write("---")
            if choice.startswith(correct_letter):
                st.success("🎉 回答正确！")
            else:
                st.error(f"❌ 回答错误。正确答案是：**{correct_letter}**")
            st.info(f"💡 解析：{q_data['解析']}")