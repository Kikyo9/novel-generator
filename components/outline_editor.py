"""Outline editor: Step 2 of the novel creation workflow."""
import streamlit as st
from utils.ai_client import NovelAI


def render_outline_editor():
    """Render the outline generation and editing interface."""
    st.markdown("### 第二步：大纲确认与编辑")

    config = st.session_state.get("workshop_config", {})

    # Show config summary
    with st.expander("📋 查看当前设定", expanded=False):
        cats = "、".join(config.get("categories", []))
        sts = "、".join(config.get("styles", []))
        st.markdown(f"**分类**: {cats}")
        st.markdown(f"**主角**: {config.get('protagonist', '')}")
        st.markdown(f"**篇幅**: {config.get('length', '')}")
        st.markdown(f"**风格**: {sts}")
        ft = config.get("free_text", "")
        if ft:
            st.markdown(f"**额外描述**: {ft}")

    # Initialize outline in session state
    if "generated_outline" not in st.session_state:
        st.session_state.generated_outline = []
        st.session_state.novel_title_ai = ""
        st.session_state.novel_synopsis = ""

    # Generate outline button
    if not st.session_state.generated_outline:
        st.markdown("---")
        st.info("点击下方按钮，AI 将根据你的设定生成章节大纲")

        if st.button("🔮 生成大纲", type="primary", use_container_width=True):
            with st.spinner("AI 正在构思大纲，请稍候..."):
                try:
                    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
                    if not api_key:
                        st.error("未配置 DeepSeek API Key，请在 .streamlit/secrets.toml 中设置")
                        return

                    ai = NovelAI(api_key)
                    result = ai.generate_outline(config)

                    st.session_state.novel_title_ai = result.get("title", "未命名")
                    st.session_state.novel_synopsis = result.get("synopsis", "")
                    st.session_state.generated_outline = result.get("chapters", [])

                    # Initialize editing states
                    st.session_state.edited_outline = [
                        {
                            "number": ch["number"],
                            "title": ch["title"],
                            "summary": ch["summary"],
                            "note": "",
                        }
                        for ch in st.session_state.generated_outline
                    ]
                    st.rerun()
                except Exception as e:
                    st.error(f"大纲生成失败：{str(e)}")

    # Display and edit outline
    if st.session_state.generated_outline:
        # AI suggested title
        st.markdown("---")
        ai_title = st.session_state.get("novel_title_ai", "")
        if ai_title:
            st.markdown(f"**AI 建议书名**: 《{ai_title}》")
            user_title = st.text_input(
                "你可以修改书名（或留空使用 AI 建议）",
                value=st.session_state.get("final_title", ai_title),
                key="final_title_input",
            )
            st.session_state.final_title = user_title or ai_title

        synopsis = st.session_state.get("novel_synopsis", "")
        if synopsis:
            with st.expander("📖 小说简介", expanded=False):
                st.markdown(synopsis)

        st.markdown("---")
        st.markdown(f"**章节大纲** ({len(st.session_state.generated_outline)} 章)")

        edited = st.session_state.get("edited_outline", [])
        if not edited:
            edited = [
                {"number": ch["number"], "title": ch["title"],
                 "summary": ch["summary"], "note": ""}
                for ch in st.session_state.generated_outline
            ]
            st.session_state.edited_outline = edited

        # Display each chapter with edit capabilities
        for idx, ch in enumerate(edited):
            with st.container():
                col1, col2, col3 = st.columns([0.5, 4, 0.8])
                with col1:
                    st.markdown(f"**第{ch['number']}章**")
                with col2:
                    new_title = st.text_input(
                        "标题",
                        value=ch["title"],
                        key=f"ch_title_{idx}",
                        label_visibility="collapsed",
                    )
                    edited[idx]["title"] = new_title

                    new_summary = st.text_input(
                        "概要",
                        value=ch["summary"],
                        key=f"ch_summary_{idx}",
                        label_visibility="collapsed",
                    )
                    edited[idx]["summary"] = new_summary

                    new_note = st.text_input(
                        "给这章的特别要求（可选）",
                        value=ch.get("note", ""),
                        key=f"ch_note_{idx}",
                        label_visibility="collapsed",
                        placeholder="例：这章要多写打斗场面",
                    )
                    edited[idx]["note"] = new_note

                with col3:
                    if idx > 0:
                        if st.button("⬆", key=f"up_{idx}", help="上移"):
                            edited[idx], edited[idx - 1] = edited[idx - 1], edited[idx]
                            edited[idx]["number"] = idx + 1
                            edited[idx - 1]["number"] = idx
                            st.rerun()
                    if idx < len(edited) - 1:
                        if st.button("⬇", key=f"down_{idx}", help="下移"):
                            edited[idx], edited[idx + 1] = edited[idx + 1], edited[idx]
                            edited[idx]["number"] = idx + 1
                            edited[idx + 1]["number"] = idx + 2
                            st.rerun()

                st.divider()

        st.session_state.edited_outline = edited

        # Action buttons
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🔄 重新生成大纲", use_container_width=True):
                st.session_state.generated_outline = []
                st.session_state.edited_outline = []
                st.rerun()
        with col_b:
            if st.button("⬅ 返回设定", use_container_width=True):
                st.session_state.workshop_step = "config"
                st.rerun()
        with col_c:
            if st.button("✅ 确认大纲，开始生成", type="primary", use_container_width=True):
                st.session_state.workshop_outline = st.session_state.edited_outline
                st.session_state.workshop_step = "generating"
                st.rerun()
