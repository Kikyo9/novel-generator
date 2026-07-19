"""
网文生成工坊 v1.0.0
AI-powered web novel generation tool.
"""
import streamlit as st
from components.auth import render_auth
from components.config_panel import render_config_panel, build_config
from components.outline_editor import render_outline_editor
from components.reader import render_reader
from components.bookshelf import render_bookshelf
from components.settings import render_settings
from components.styles import READER_CSS
from utils.ai_client import NovelAI
import json
import uuid
from datetime import datetime

# ---- Page Config ----
st.set_page_config(
    page_title="网文生成工坊",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Initialize Session State ----
def init_session():
    """Initialize all session state variables."""
    defaults = {
        "page": "workshop",
        "workshop_step": "config",
        "workshop_config": {},
        "workshop_outline": [],
        "generated_outline": [],
        "edited_outline": [],
        "generated_chapters": {},
        "novel_title_ai": "",
        "novel_synopsis": "",
        "final_title": "",
        "reader_current_chapter": 0,
        "reader_night_mode": False,
        "reader_font_size": 16,
        "reader_line_height": 2.0,
        "show_download": False,
        "local_novels": [],
        "user_id": "",
        "generating_chapter": -1,
        "generation_mode": "outline_chapters",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ---- Sidebar ----
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0;">
        <h2 style="margin:0;color:#4a4458;">📖 网文生成工坊</h2>
        <p style="color:#999;font-size:0.85em;margin:4px 0 0 0;">AI 驱动的网络小说创作工具</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Auth
    logged_in = render_auth()

    st.markdown("---")

    # Navigation
    pages = {
        "✏️ 创作工坊": "workshop",
        "📚 我的书架": "bookshelf",
        "⚙️ 设置": "settings",
    }

    for label, page_key in pages.items():
        is_active = st.session_state.page == page_key
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{page_key}", type=btn_type, use_container_width=True):
            st.session_state.page = page_key
            if page_key == "workshop" and st.session_state.workshop_step == "config":
                pass  # stay on config
            st.rerun()

    st.markdown("---")

    # Workshop step indicator (only show on workshop page)
    if st.session_state.page == "workshop":
        steps = [
            ("1. 设定", "config"),
            ("2. 大纲", "outline"),
            ("⚙ 生成中", "generating"),
            ("3. 阅读", "reading"),
        ]
        current = st.session_state.workshop_step

        st.caption("创作进度")
        for label, step_key in steps:
            step_keys = [s[1] for s in steps]
            current_idx = step_keys.index(current) if current in step_keys else -1
            this_idx = step_keys.index(step_key)
            if step_key == current:
                icon = "⏳" if step_key == "generating" else "✅"
            elif current_idx >= 0 and this_idx < current_idx:
                icon = "✅"
            else:
                icon = "○"
            st.markdown(f"{icon} {label}")


def _render_generation():
    """Handle chapter generation based on the selected mode."""
    config = st.session_state.get("workshop_config", {})
    outline = st.session_state.get("workshop_outline", [])
    chapters = st.session_state.get("generated_chapters", {})
    mode = config.get("generation_mode", "outline_chapters")

    if not outline:
        st.warning("没有找到章节大纲，请返回第二步生成大纲。")
        if st.button("⬅ 返回大纲编辑"):
            st.session_state.workshop_step = "outline"
            st.rerun()
        return

    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        st.error("未配置 DeepSeek API Key")
        if st.button("⬅ 返回"):
            st.session_state.workshop_step = "outline"
            st.rerun()
        return

    # Show mode info
    mode_labels = {
        "outline_chapters": "逐章生成 —— 每次点击生成一章",
        "full_text": "一次性生成全文 —— AI 直接输出完整小说",
        "interactive": "交互式续写 —— 你给方向，AI 接着写",
        "outline_batch": "批量生成 —— 一次性生成所有章节",
    }
    st.markdown(f"### 第三步：生成小说")
    st.caption(mode_labels.get(mode, ""))

    # ---- Mode: outline_chapters ----
    if mode == "outline_chapters":
        all_done = len(outline) > 0 and all(str(i) in chapters for i in range(len(outline)))
        if all_done:
            st.success("🎉 所有章节已生成完毕！")
            if st.button("📖 开始阅读", type="primary"):
                st.session_state.workshop_step = "reading"
                st.rerun()

        # One-click generate all button
        ungenerated = sum(1 for i in range(len(outline)) if str(i) not in chapters)
        if ungenerated > 0:
            st.button(f"⚡ 一键生成 {ungenerated} 章", key="batch_gen_all", type="primary", on_click=lambda: st.session_state.__setitem__("_batch_active", True))
        if st.session_state.get("_batch_active"):
            from utils.ai_client import NovelAI as NAI2
            ai2 = NAI2(api_key)
            pbar = st.progress(0)
            stxt = st.empty()
            for bi in range(len(outline)):
                if str(bi) in chapters:
                    pbar.progress((bi + 1) / len(outline))
                    continue
                bc = outline[bi]
                stxt.text(f"正在生成：第{bc['number']}章 {bc['title']} ({bi+1}/{len(outline)})")
                try:
                    ps = "".join(f"第{outline[p]['number']}章 {outline[p].get('title','')}：{outline[p].get('summary','')}\n" for p in range(bi) if str(p) not in chapters)
                    pc = "\n".join(chapters.get(str(p), "") for p in range(bi) if str(p) in chapters)
                    c2 = ai2.generate_chapter(config, outline, bi, ps, pc)
                    chapters[str(bi)] = c2
                    st.session_state.generated_chapters = chapters
                except Exception as e2:
                    st.error(f"第{bc['number']}章\u5931\u8d25：{e2}")
                pbar.progress((bi + 1) / len(outline))
            stxt.text("\u5168\u90e8章\u8282\u751f\u6210\u5b8c\u6bd5\uff01")
            st.session_state._batch_active = False
            st.rerun()

        for idx, ch in enumerate(outline):
            is_generated = str(idx) in chapters
            col1, col2 = st.columns([4, 1])
            with col1:
                status_icon = "✅" if is_generated else "⏳"
                note_suffix = f" — *{ch.get('note', '')}*" if ch.get("note") else ""
                st.markdown(f"{status_icon} **第{ch['number']}章** {ch['title']}{note_suffix}")
            with col2:
                if not is_generated:
                    if st.button("生成本章", key=f"gen_ch_{idx}"):
                        st.session_state.generating_chapter = idx
                        st.rerun()
                else:
                    if st.button("重新生成", key=f"regen_ch_{idx}"):
                        del chapters[str(idx)]
                        st.session_state.generating_chapter = idx
                        st.rerun()

        # Actually generate a chapter
        gen_idx = st.session_state.get("generating_chapter", -1)
        if gen_idx >= 0 and gen_idx < len(outline):
            ch = outline[gen_idx]
            with st.spinner(f"正在生成第{ch['number']}章：{ch['title']}..."):
                try:
                    ai = NovelAI(api_key)

                    # Build previous summary
                    prev_summary = ""
                    for pi in range(gen_idx):
                        prev_ch = outline[pi]
                        prev_summary += f"第{prev_ch['number']}章 {prev_ch['title']}：{prev_ch.get('summary', '')}\n"

                    prev_chapters = "\n".join(chapters.get(str(p), "") for p in range(gen_idx) if str(p) in chapters)
                    content = ai.generate_chapter(config, outline, gen_idx, prev_summary, prev_chapters)
                    chapters[str(gen_idx)] = content
                    st.session_state.generated_chapters = chapters
                    st.session_state.generating_chapter = -1

                    # Auto-save to local
                    _save_locally()

                    st.rerun()
                except Exception as e:
                    st.error(f"生成失败：{str(e)}")
                    st.session_state.generating_chapter = -1

    # ---- Mode: full_text ----
    elif mode == "full_text":
        if "full_text_generated" not in st.session_state:
            st.session_state.full_text_generated = False

        if not st.session_state.full_text_generated:
            if st.button("🚀 生成全文", type="primary"):
                with st.spinner("AI 正在创作，这可能需要几分钟..."):
                    try:
                        ai = NovelAI(api_key)
                        full_text = ai.generate_full_novel(config, outline)

                        # Parse into chapters
                        import re
                        ch_pattern = re.compile(r'第([一二三四五六七八九十百千\d]+)章\s*(.*?)\n')
                        parts = ch_pattern.split(full_text)

                        parsed = {}
                        ch_num = 0
                        for i in range(1, len(parts), 3):
                            title = parts[i + 1].strip() if i + 1 < len(parts) else ""
                            content = parts[i + 2].strip() if i + 2 < len(parts) else ""
                            parsed[str(ch_num)] = f"第{ch_num+1}章 {title}\n\n{content}"
                            ch_num += 1

                        if not parsed:
                            parsed = {"0": full_text}

                        st.session_state.generated_chapters = parsed
                        st.session_state.full_text_generated = True

                        if outline:
                            new_outline = []
                            for i in range(len(parsed)):
                                new_outline.append({
                                    "number": i + 1,
                                    "title": f"第{i+1}章",
                                    "summary": "",
                                    "note": "",
                                })
                            st.session_state.workshop_outline = new_outline

                        _save_locally()
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败：{str(e)}")
        else:
            st.success("全文已生成！")
            if st.button("📖 开始阅读", type="primary"):
                st.session_state.workshop_step = "reading"
                st.rerun()

    # ---- Mode: interactive ----
    elif mode == "interactive":
        if "interactive_text" not in st.session_state:
            st.session_state.interactive_text = ""
            st.session_state.interactive_history = []

        st.text_area("当前内容",
                     value=st.session_state.interactive_text or "（尚未开始创作）",
                     height=400,
                     disabled=True)

        direction = st.text_area("续写方向",
                                  placeholder="描述你希望后续情节如何发展...",
                                  height=80)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 续写", type="primary", use_container_width=True):
                if direction.strip():
                    with st.spinner("AI 正在续写..."):
                        try:
                            ai = NovelAI(api_key)
                            continuation = ai.continue_chapter(
                                config,
                                st.session_state.interactive_text,
                                direction,
                            )
                            st.session_state.interactive_text += "\n\n" + continuation
                            st.session_state.interactive_history.append({
                                "direction": direction,
                                "continuation": continuation,
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"续写失败：{str(e)}")
                else:
                    st.warning("请输入续写方向")
        with col2:
            if st.button("📖 完成创作，保存", use_container_width=True):
                st.session_state.generated_chapters = {
                    "0": st.session_state.interactive_text
                }
                st.session_state.workshop_outline = [{
                    "number": 1, "title": "全文", "summary": "", "note": ""
                }]
                _save_locally()
                st.session_state.workshop_step = "reading"
                st.rerun()

    # ---- Mode: outline_batch ----
    elif mode == "outline_batch":
        all_done = len(outline) > 0 and all(str(i) in chapters for i in range(len(outline)))
        if all_done:
            st.success("🎉 所有章节已生成完毕！")
            if st.button("📖 开始阅读", type="primary"):
                st.session_state.workshop_step = "reading"
                st.rerun()
        else:
            if st.button("🚀 批量生成所有章节", type="primary"):
                ai = NovelAI(api_key)
                progress = st.progress(0)
                status = st.empty()

                for idx, ch in enumerate(outline):
                    if str(idx) in chapters:
                        continue
                    status.text(f"正在生成：第{ch['number']}章 {ch['title']}")
                    try:
                        prev_summary = ""
                        for pi in range(idx):
                            prev_ch = outline[pi]
                            prev_summary += f"第{prev_ch['number']}章 {prev_ch['title']}：{prev_ch.get('summary', '')}\n"

                        content = ai.generate_chapter(config, outline, idx, prev_summary)
                        chapters[str(idx)] = content
                        st.session_state.generated_chapters = chapters
                        _save_locally()
                    except Exception as e:
                        st.error(f"第{ch['number']}章生成失败：{e}")
                    progress.progress((idx + 1) / len(outline))

                status.text("全部章节生成完毕！")
                st.rerun()

    # Navigation
    st.markdown("---")
    if st.button("⬅ 返回大纲编辑"):
        st.session_state.workshop_step = "outline"
        st.rerun()


def _save_locally():
    """Save current novel to local storage and Supabase."""
    novel_id = st.session_state.get("current_novel_id", str(uuid.uuid4())[:8])
    st.session_state.current_novel_id = novel_id

    config = st.session_state.get("workshop_config", {})
    local = st.session_state.get("local_novels", [])

    novel_entry = {
        "id": novel_id,
        "title": st.session_state.get("final_title", config.get("novel_title", "未命名")),
        "categories": config.get("categories", []),
        "length": config.get("length", ""),
        "styles": config.get("styles", []),
        "synopsis": st.session_state.get("novel_synopsis", ""),
        "outline": st.session_state.get("workshop_outline", []),
        "chapters": st.session_state.get("generated_chapters", {}),
        "config": config,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    # Update or append locally
    found = False
    for i, n in enumerate(local):
        if n.get("id") == novel_id:
            local[i] = novel_entry
            found = True
            break
    if not found:
        local.append(novel_entry)
    st.session_state.local_novels = local

    # Also save to Supabase if logged in
    user_id = st.session_state.get("user_id", "")
    if user_id:
        try:
            from components.auth import get_supabase_store
            store2 = get_supabase_store()
            if store2 and store2.is_connected():
                if novel_id and any(n.get("id") == novel_id for n in local):
                    store2.update_novel(novel_id, novel_entry)
                else:
                    new_id = store2.save_novel(user_id, novel_entry)
                    if new_id:
                        st.session_state.current_novel_id = new_id
        except Exception as e:
            import sys
            print(f"Supabase save error: {e}", file=sys.stderr)

# ---- Main Content ----
if st.session_state.page == "workshop":
    step = st.session_state.workshop_step

    if step == "config":
        render_config_panel()

    elif step == "outline":
        render_outline_editor()

    elif step == "generating":
        _render_generation()

    elif step == "reading":
        render_reader()

elif st.session_state.page == "bookshelf":
    render_bookshelf()

elif st.session_state.page == "settings":
    render_settings()


