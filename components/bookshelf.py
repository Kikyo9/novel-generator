"""Bookshelf page: display and manage saved novels from Supabase."""
import streamlit as st
import json
from datetime import datetime


def render_bookshelf():
    """Render the bookshelf page with all user novels from Supabase."""
    st.markdown("### \U0001f4da 我的书架")

    user_id = st.session_state.get("user_id", "")
    if not user_id:
        st.info("\U0001f512 请先在侧边栏登录，登录后即可使用书架功能。")
        if st.button("\U0001f680 前往创作工坊"):
            st.session_state.page = "workshop"
            st.rerun()
        return

    from components.auth import get_supabase_store
    store = get_supabase_store()
    if store is None or not store.is_connected():
        st.error("无法连接 Supabase，请先登录。")
        return

    novels = store.get_user_novels(user_id)

    if not novels:
        st.info("\U0001f4ed 书架空空如也，去创作工坊生成你的第一本小说吧！")
        if st.button("\U0001f680 前往创作工坊", type="primary"):
            st.session_state.page = "workshop"
            st.rerun()
        return

    # Display novel cards
    for novel in novels:
        with st.container():
            col1, col2, col3 = st.columns([6, 2, 1])
            with col1:
                st.markdown(f"### \U0001f4d6 {novel.get('title', '未命名')}")
                meta = []
                cats = novel.get("categories", [])
                if isinstance(cats, str):
                    try:
                        cats = json.loads(cats) if cats.startswith("[") else [cats]
                    except Exception:
                        cats = [cats]
                if cats:
                    meta.append(" · ".join(cats))
                length = novel.get("length", "")
                if length:
                    meta.append(length)
                sts = novel.get("styles", [])
                if isinstance(sts, str):
                    try:
                        sts = json.loads(sts) if sts.startswith("[") else [sts]
                    except Exception:
                        sts = [sts]
                if sts:
                    meta.append(" · ".join(sts))
                st.caption(" · ".join(meta))
                synopsis = novel.get("synopsis", "")
                if synopsis:
                    st.markdown(synopsis[:150] + ("..." if len(synopsis) > 150 else ""))
                created = novel.get("created_at", "")
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        st.caption(f"创建于 {dt.strftime('%Y-%m-%d %H:%M')}")
                    except Exception:
                        pass

            with col2:
                if st.button("\U0001f4d6 阅读", key=f"read_{novel.get('id', '')}"):
                    st.session_state.current_novel_id = novel.get("id", "")
                    saved_config = novel.get("config", {}) or {}
                    st.session_state.workshop_config = {
                        "categories": saved_config.get("categories", cats),
                        "protagonist": saved_config.get("protagonist", novel.get("protagonist", "")),
                        "length": saved_config.get("length", length),
                        "styles": saved_config.get("styles", sts),
                        "free_text": saved_config.get("free_text", ""),
                        "generation_mode": saved_config.get("generation_mode", "outline_chapters"),
                        "novel_title": saved_config.get("novel_title", novel.get("title", "")),
                    }
                    st.session_state.workshop_outline = novel.get("outline", [])
                    gen_chapters = novel.get("chapters", {})
                    if isinstance(gen_chapters, str):
                        gen_chapters = json.loads(gen_chapters)
                    st.session_state.generated_chapters = gen_chapters
                    st.session_state.final_title = novel.get("title", "未命名")
                    st.session_state.novel_synopsis = novel.get("synopsis", "")
                    st.session_state.reader_current_chapter = 0
                    st.session_state.workshop_step = "reading"
                    st.session_state.page = "workshop"
                    st.rerun()

            with col3:
                if st.button("\U0001f5d1", key=f"del_{novel.get('id', '')}", help="删除"):
                    store.delete_novel(novel["id"])
                    st.rerun()

            st.divider()
