"""Book reader component: Step 3 - immersive reading experience."""
import streamlit as st
from utils.epub_generator import generate_epub, is_epub_available
from components.styles import READER_CSS


def render_reader():
    """Render the book reader with paper-like styling."""
    st.markdown(READER_CSS, unsafe_allow_html=True)

    config = st.session_state.get("workshop_config", {})
    outline = st.session_state.get("workshop_outline", [])
    chapters = st.session_state.get("generated_chapters", {})
    night_mode = st.session_state.get("reader_night_mode", False)
    font_size = st.session_state.get("reader_font_size", 16)
    line_height = st.session_state.get("reader_line_height", 2.0)
    current_ch = st.session_state.get("reader_current_chapter", 0)
    epub_ok = is_epub_available()

    night_class = "night-mode" if night_mode else ""

    st.markdown(f'<div class="{night_class}">', unsafe_allow_html=True)

    # Back button
    if st.button("\u2b05 返回书架", key="back_to_shelf"):
        st.session_state.page = "bookshelf"
        st.rerun()

    # Chapter selector
    ch_labels = [f"第{ch['number']}章 {ch['title']}" for ch in outline]
    if ch_labels:
        selected_label = st.selectbox(
            "跳转到章节",
            ch_labels,
            index=min(current_ch, len(ch_labels) - 1),
            key="chapter_selector",
        )
        selected_idx = ch_labels.index(selected_label)
        if selected_idx != current_ch:
            st.session_state.reader_current_chapter = selected_idx
            st.rerun()

    # Controls
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("\U0001f319 夜间模式" if not night_mode else "\u2600\ufe0f 日间模式"):
            st.session_state.reader_night_mode = not night_mode
            st.rerun()
    with c2:
        new_size = st.select_slider(
            "字号", options=[14, 16, 18, 20, 22, 24],
            value=font_size, key="font_size_slider",
        )
        if new_size != font_size:
            st.session_state.reader_font_size = new_size
            st.rerun()
    with c3:
        new_lh = st.select_slider(
            "行距", options=[1.5, 1.8, 2.0, 2.2, 2.5],
            value=line_height, key="line_height_slider",
        )
        if new_lh != line_height:
            st.session_state.reader_line_height = new_lh
            st.rerun()
    with c4:
        if st.button("\U0001f4be 下载"):
            st.session_state.show_download = True

    # Download dialog
    if st.session_state.get("show_download"):
        with st.expander("\U0001f4e5 下载选项", expanded=True):
            format_options = ["TXT"]
            if epub_ok:
                format_options.append("EPUB")
            else:
                st.info("EPUB 格式需要安装 ebooklib 库。\n运行: `pip install ebooklib`")

            fmt = st.radio("选择格式", format_options, horizontal=True)
            if st.button(f"下载 {fmt}", type="primary"):
                title = st.session_state.get("final_title", "未命名小说")
                ch_list = []
                for i, ch in enumerate(outline):
                    ch_list.append({
                        "number": ch["number"],
                        "title": ch["title"],
                        "content": chapters.get(str(i), "（本章尚未生成）"),
                    })

                if fmt == "TXT":
                    txt_content = f"{title}\n\n"
                    for ch in ch_list:
                        txt_content += f"\n{'=' * 40}\n"
                        txt_content += f"第{ch['number']}章 {ch['title']}\n"
                        txt_content += f"{'=' * 40}\n\n"
                        txt_content += ch["content"] + "\n"
                    st.download_button(
                        "确认下载 TXT",
                        data=txt_content.encode("utf-8"),
                        file_name=f"{title}.txt",
                        mime="text/plain",
                    )
                else:
                    try:
                        epub_bytes = generate_epub(
                            title=title,
                            author="网文生成工坊",
                            chapters=ch_list,
                            synopsis=st.session_state.get("novel_synopsis", ""),
                        )
                        st.download_button(
                            "确认下载 EPUB",
                            data=epub_bytes,
                            file_name=f"{title}.epub",
                            mime="application/epub+zip",
                        )
                    except ImportError as e:
                        st.error(str(e))

    # Book reading area
    if not outline or current_ch >= len(outline):
        st.info("没有可显示的内容")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    ch = outline[current_ch]
    content = chapters.get(str(current_ch), "（点击「生成本章」开始阅读）")

    paragraphs = "".join(
        f"<p>{p}</p>" for p in content.strip().split("\n") if p.strip()
    )

    st.markdown(f"""
    <div class="reader-book" style="font-size:{font_size}px;line-height:{line_height};">
        <div class="chapter-title">第{ch['number']}章 {ch['title']}</div>
        <div class="chapter-content">
            {paragraphs}
        </div>
        <div class="reader-progress">
            第 {current_ch + 1} / {len(outline)} 章
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chapter navigation buttons
    cn1, cn2, cn3 = st.columns([1, 2, 1])
    with cn1:
        if current_ch > 0:
            if st.button("\u2b05 上一章", use_container_width=True):
                st.session_state.reader_current_chapter = current_ch - 1
                st.rerun()
    with cn3:
        if current_ch < len(outline) - 1:
            if st.button("下一章 \u27a1", use_container_width=True):
                st.session_state.reader_current_chapter = current_ch + 1
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
