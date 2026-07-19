"""Book reader component: Step 3 - immersive reading experience."""
import streamlit as st
from utils.epub_generator import generate_epub, is_epub_available
from components.styles import READER_CSS



def _on_chapter_select():
    """Callback: fires only when user interacts with selectbox."""
    labels = st.session_state.get("_ch_labels", [])
    sel = st.session_state.get("chapter_selector", "")
    if sel in labels:
        st.session_state.reader_current_chapter = labels.index(sel)

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

    # Top toolbar
    col_back, col_save = st.columns([3, 1])
    with col_back:
        if st.button("\u2b05 返回工作台", key="back_to_workshop"):
            st.session_state.page = "workshop"
            st.session_state.workshop_step = "config"
            st.rerun()
    with col_save:
        if st.button("\U0001f516 加入书架", key="save_to_bookshelf", type="primary"):
            from utils.supabase_client import NovelStore
            user_id = st.session_state.get("user_id", "")
            if not user_id:
                st.warning("请先在侧边栏登录后再保存到书架")
            else:
                supabase_url = st.secrets.get("SUPABASE_URL", "")
                supabase_key = st.secrets.get("SUPABASE_ANON_KEY", "")
                store = NovelStore(supabase_url, supabase_key)
                if store.is_connected():
                    title = st.session_state.get("final_title", config.get("novel_title", "未命名"))
                    novel_data = {
                        "title": title,
                        "categories": config.get("categories", []),
                        "protagonist": config.get("protagonist", ""),
                        "length": config.get("length", ""),
                        "styles": config.get("styles", []),
                        "synopsis": st.session_state.get("novel_synopsis", ""),
                        "outline": outline,
                        "chapters": chapters,
                    }
                    # Check if already saved
                    existing_id = st.session_state.get("current_novel_id", "")
                    if existing_id:
                        store.update_novel(existing_id, novel_data)
                        st.success(f"《{title}》已更新到书架！")
                    else:
                        novel_id = store.save_novel(user_id, novel_data)
                        if novel_id:
                            st.session_state.current_novel_id = novel_id
                            st.success(f"《{title}》已加入书架！")
                        else:
                            st.error("保存失败，请重试")
                else:
                    st.error("无法连接 Supabase")

    # Chapter selector (with on_change to avoid overriding nav buttons)
    ch_labels = [f"第{ch['number']}章 {ch['title']}" for ch in outline]
    if ch_labels:
        # Store labels for callback access
        st.session_state._ch_labels = ch_labels
        # Use on_change to only fire when user interacts with selectbox
        selected_label = st.selectbox(
            "跳转到章节", ch_labels,
            key="chapter_selector",
            on_change=_on_chapter_select
        )

    # Controls
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("\U0001f319 夜间" if not night_mode else "\u2600\ufe0f 日间"):
            st.session_state.reader_night_mode = not night_mode
            st.rerun()
    with c2:
        new_size = st.select_slider("字号", options=[14, 16, 18, 20, 22, 24], value=font_size, key="fs")
        if new_size != font_size:
            st.session_state.reader_font_size = new_size
            st.rerun()
    with c3:
        new_lh = st.select_slider("行距", options=[1.5, 1.8, 2.0, 2.2, 2.5], value=line_height, key="lh")
        if new_lh != line_height:
            st.session_state.reader_line_height = new_lh
            st.rerun()
    with c4:
        if st.button("\U0001f4be 下载"):
            st.session_state.show_download = True

    # Download
    if st.session_state.get("show_download"):
        with st.expander("\U0001f4e5 下载选项", expanded=True):
            fmts = ["TXT"] + (["EPUB"] if epub_ok else [])
            if not epub_ok:
                st.info("EPUB 需要: pip install ebooklib")
            fmt = st.radio("格式", fmts, horizontal=True)
            title = st.session_state.get("final_title", "未命名")
            ch_list = [{"number": ch["number"], "title": ch["title"],
                        "content": chapters.get(str(i), "")}
                       for i, ch in enumerate(outline)]
            if fmt == "TXT":
                txt = title + "\n\n"
                for ch in ch_list:
                    txt += f"\n{'='*40}\n第{ch['number']}章 {ch['title']}\n{'='*40}\n\n{ch['content']}\n"
                st.download_button("下载 TXT", txt.encode("utf-8"), f"{title}.txt", "text/plain")
            elif epub_ok:
                try:
                    epub_bytes = generate_epub(title, "网文生成工坊", ch_list,
                                               st.session_state.get("novel_synopsis", ""))
                    st.download_button("下载 EPUB", epub_bytes, f"{title}.epub", "application/epub+zip")
                except Exception as e:
                    st.error(str(e))

    # Reading area
    if not outline or current_ch >= len(outline):
        st.info("没有可显示的内容")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    ch = outline[current_ch]
    content = chapters.get(str(current_ch), "（本章尚未生成）")
    paragraphs = "".join(f"<p>{p}</p>" for p in content.strip().split("\n") if p.strip())

    st.markdown(f"""
    <div class="reader-book" style="font-size:{font_size}px;line-height:{line_height};">
        <div id="reader-top"></div>
        <div class="chapter-title">第{ch['number']}章 {ch['title']}</div>
        <div class="chapter-content">{paragraphs}</div>
        <div class="reader-progress">第 {current_ch + 1} / {len(outline)} 章</div>
    </div>
    """, unsafe_allow_html=True)

    # Scroll to top of reader when chapter changes
    if current_ch != st.session_state.get("_prev_reader_ch", -1):
        st.session_state._prev_reader_ch = current_ch
        st.markdown(
            '<script>requestAnimationFrame(function(){requestAnimationFrame(function(){var e=document.getElementById("reader-top");if(e){var r=e.getBoundingClientRect();window.scrollTo({top:window.scrollY+r.top-64,behavior:"smooth"})}})})</script>',
            unsafe_allow_html=True)

    # Chapter navigation
    cn1, cn2, cn3 = st.columns([1, 2, 1])
    with cn1:
        if current_ch > 0 and st.button("\u2b05 上一章", use_container_width=True, key="nav_prev"):
            st.session_state.reader_current_chapter = current_ch - 1
            st.rerun()
    with cn3:
        if current_ch < len(outline) - 1 and st.button("下一章 \u27a1", use_container_width=True, key="nav_next"):
            st.session_state.reader_current_chapter = current_ch + 1
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
