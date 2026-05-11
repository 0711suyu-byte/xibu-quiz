import streamlit as st
import pandas as pd

# 1. 页面基础配置（适配手机端，界面更清爽）
st.set_page_config(page_title="西部计划特训", page_icon="📖", layout="centered")


# 2. 加载题库数据
@st.cache_data
def load_data():
    # 确保 CSV 文件名与实际一致
    return pd.read_csv("4.csv")


df = load_data()

# 3. 初始化会话状态（实现错题记忆和进度记录）
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'wrong_q_indices' not in st.session_state:
    st.session_state.wrong_q_indices = set()  # 用集合存储错题索引，避免重复
if 'show_exp' not in st.session_state:
    st.session_state.show_exp = False
if 'mode' not in st.session_state:
    st.session_state.mode = '全题库'

# 4. 侧边栏：模式切换与错题统计
with st.sidebar:
    st.header("⚙️ 刷题设置")
    mode = st.radio("选择模式：", ['全题库', '错题本'])

    # 当切换模式时，重置进度
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.session_state.current_idx = 0
        st.session_state.show_exp = False
        st.rerun()

    st.write("---")
    st.write(f"❌ 当前错题总数：{len(st.session_state.wrong_q_indices)}")
    if st.button("清空错题本"):
        st.session_state.wrong_q_indices.clear()
        st.rerun()

# 5. 根据模式获取要刷的题目列表
if st.session_state.mode == '全题库':
    questions_list = list(range(len(df)))
else:
    questions_list = list(st.session_state.wrong_q_indices)

# 6. 主界面交互逻辑
st.title("📚 西部计划·冲刺特训")

if not questions_list:
    st.success("太棒啦！目前没有错题，继续保持！🎉")
else:
    # 进度条
    progress = (st.session_state.current_idx + 1) / len(questions_list)
    st.progress(progress)
    st.caption(f"当前进度: {st.session_state.current_idx + 1} / {len(questions_list)}")

    # 获取当前题目数据
    real_idx = questions_list[st.session_state.current_idx]
    q_data = df.iloc[real_idx]

    # 展示题目
    st.markdown(f"#### {q_data['题目']}")

    # 提取选项
    options = [q_data['选项A'], q_data['选项B'], q_data['选项C']]
    correct_letter = q_data['正确答案']  # 例如 "A"

    # 单选框，key 绑定题目索引防止状态混乱
    choice = st.radio("请选择你的答案：", options, index=None, key=f"q_{real_idx}")

    # 并排显示按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("提交并查看解析", use_container_width=True):
            if choice:
                st.session_state.show_exp = True
                # 如果选错了，加入错题本
                if not choice.startswith(correct_letter):
                    st.session_state.wrong_q_indices.add(real_idx)
            else:
                st.warning("请先选择一个答案哦！")

    with col2:
        if st.button("下一题 ➡️", use_container_width=True):
            st.session_state.show_exp = False
            if st.session_state.current_idx < len(questions_list) - 1:
                st.session_state.current_idx += 1
            else:
                st.session_state.current_idx = 0  # 到底后循环回第一题
            st.rerun()

    # 显示解析区
    if st.session_state.show_exp:
        st.write("---")
        if choice.startswith(correct_letter):
            st.success("🎉 回答正确！")
        else:
            st.error(f"❌ 回答错误。正确答案是：**{correct_letter}**")
        st.info(f"💡 解析：{q_data['解析']}")