"""Configuration panel: Step 1 of the novel creation workflow."""
import streamlit as st

CATEGORIES = [
    "玄幻", "仙侠", "武侠", "都市", "职场", "现实",
    "言情", "纯爱", "科幻", "末世", "机甲",
    "悬疑", "灵异", "恐怖", "历史", "架空", "穿越",
    "游戏", "电竞", "系统流", "轻小说", "二次元",
]

STYLES = [
    "爽文", "虐文", "搞笑", "暗黑", "热血",
    "治愈", "甜宠", "正剧", "轻松",
]

LENGTHS = [
    "短篇（1-3万字）",
    "中篇（5-10万字）",
    "长篇（20-50万字）",
    "超长篇（100万字以上）",
]

GENERATION_MODES = {
    "大纲 → 逐章生成（推荐）": "outline_chapters",
    "一次性生成全文": "full_text",
    "交互式续写": "interactive",
    "大纲生成后批量生成所有章节": "outline_batch",
}


def init_config_state():
    defaults = {
        "novel_title": "",
        "categories": [],
        "protagonist_name": "",
        "protagonist_gender": "未定",
        "protagonist_personality": "",
        "length": LENGTHS[0],
        "styles": [],
        "free_text": "",
        "generation_mode": "outline_chapters",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def build_config() -> dict:
    protagonist_parts = []
    if st.session_state.get("protagonist_name"):
        protagonist_parts.append(f"姓名：{st.session_state.protagonist_name}")
    protagonist_parts.append(f"性别：{st.session_state.get('protagonist_gender', '未定')}")
    if st.session_state.get("protagonist_personality"):
        protagonist_parts.append(f"性格：{st.session_state.protagonist_personality}")

    return {
        "novel_title": st.session_state.get("novel_title", ""),
        "categories": st.session_state.get("categories", []),
        "protagonist": "，".join(protagonist_parts),
        "length": st.session_state.get("length", LENGTHS[0]),
        "styles": st.session_state.get("styles", []),
        "free_text": st.session_state.get("free_text", ""),
        "generation_mode": st.session_state.get("generation_mode", "outline_chapters"),
    }


def validate_config(config: dict) -> tuple:
    if not config["categories"]:
        return False, "请至少选择一个小说分类"
    if not config["protagonist"].strip() or "姓名：" not in config["protagonist"]:
        return False, "请输入主角姓名"
    if not config["styles"]:
        return False, "请至少选择一种风格/基调"
    return True, ""


def render_config_panel():
    init_config_state()

    st.markdown("### 第一步：创作设定")
    st.caption("分类、主角、篇幅和风格为必选项，额外描述用于补充世界观和剧情细节")

    # Novel Title
    st.text_input("小说标题（可选，留空由 AI 自动起名）",
                  key="novel_title",
                  placeholder="例：星辰变、斗破苍穹...")

    # Category
    st.markdown('<p style="font-weight:600;color:#4a4458;margin-top:16px;">分类 <span style="color:#e00;">*</span></p>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, cat in enumerate(CATEGORIES):
        col = cols[i % 5]
        with col:
            checked = cat in st.session_state.categories
            label = f"{cat} ✓" if checked else cat
            if st.checkbox(label, value=checked, key=f"cat_{cat}"):
                if cat not in st.session_state.categories:
                    st.session_state.categories.append(cat)
            else:
                if cat in st.session_state.categories:
                    st.session_state.categories.remove(cat)

    # Protagonist
    st.markdown('<p style="font-weight:600;color:#4a4458;margin-top:16px;">主角设定 <span style="color:#e00;">*</span></p>', unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns([2, 1, 3])
    with p_col1:
        st.text_input("主角姓名", key="protagonist_name", placeholder="例：林风")
    with p_col2:
        st.selectbox("性别", ["未定", "男", "女"], key="protagonist_gender")
    with p_col3:
        st.text_input("性格关键词（多个用逗号分隔）",
                      key="protagonist_personality",
                      placeholder="例：坚毅、冷静、腹黑")

    # Length
    st.markdown('<p style="font-weight:600;color:#4a4458;margin-top:16px;">篇幅 <span style="color:#e00;">*</span></p>', unsafe_allow_html=True)
    st.selectbox("选择篇幅", LENGTHS, key="length", label_visibility="collapsed")

    # Style
    st.markdown('<p style="font-weight:600;color:#4a4458;margin-top:16px;">风格/基调 <span style="color:#e00;">*</span></p>', unsafe_allow_html=True)
    s_cols = st.columns(5)
    for i, style in enumerate(STYLES):
        col = s_cols[i % 5]
        with col:
            checked = style in st.session_state.styles
            label = f"{style} ✓" if checked else style
            if st.checkbox(label, value=checked, key=f"style_{style}"):
                if style not in st.session_state.styles:
                    st.session_state.styles.append(style)
            else:
                if style in st.session_state.styles:
                    st.session_state.styles.remove(style)

    # Free Text
    st.markdown('<p style="font-weight:600;color:#4a4458;margin-top:16px;">额外描述</p>', unsafe_allow_html=True)
    st.text_area("补充世界观、剧情走向、特殊设定等（可选）",
                 key="free_text",
                 height=120,
                 placeholder="例：这是一部末世废土背景的小说，主角携带着前世记忆重生到灾难爆发前三天……")

    # Generation Mode
    st.markdown('<p style="font-weight:600;color:#4a4458;margin-top:16px;">生成模式</p>', unsafe_allow_html=True)
    mode_label = st.selectbox(
        "选择生成模式",
        list(GENERATION_MODES.keys()),
        key="generation_mode_label",
        label_visibility="collapsed",
    )
    st.session_state.generation_mode = GENERATION_MODES[mode_label]

    st.markdown("---")

    # Action Button
    if st.button("✨ 开始生成大纲", type="primary", use_container_width=True):
        config = build_config()
        valid, msg = validate_config(config)
        if not valid:
            st.error(msg)
        else:
            st.session_state.workshop_config = config
            st.session_state.workshop_step = "outline"
            st.rerun()
