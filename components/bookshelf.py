"""Bookshelf page: display and manage saved novels."""
import streamlit as st
from datetime import datetime
import json

try:
    from utils.supabase_client import NovelStore
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def render_bookshelf():
    """Render the bookshelf page with all user novels."""
    st.markdown("### 📚 我的书架")

    # Try to load from Supabase first, then fallback to local storage
    novels = []

    # Supabase
    if SUPABASE_AVAILABLE:
        supabase_url = st.secrets.get("SUPABASE_URL", "")
        supabase_key = st.secrets.get("SUPABASE_ANON_KEY", "")
        if supabase_url and supabase_key:
            try:
                store = NovelStore(supabase_url, supabase_key)
                if st.session_state.get("user_id"):
                    novels = store.get_user_novels(st.session_state.user_id)
            except Exception:
                pass

    # Local fallback
    if not novels:
        local = st.session_state.get("local_novels", [])
        novels = local

    if not novels:
        st.info("📭 书架空空如也，去创作工坊生成你的第一本小说吧！")
        if st.button("🚀 前往创作工坊", type="primary"):
            st.session_state.page = "workshop"
            st.session_state.workshop_step = "config"
            st.rerun()
        return

    # Display novel cards
    for novel in novels:
        with st.container():
            col1, col2, col3 = st.columns([6, 2, 1])
            with col1:
                st.markdown(f"### 📖 {novel.get('title', '未命名')}")

                meta_parts = []
                cats = novel.get("categories", [])
                if isinstance(cats, str):
                    cats = json.loads(cats) if cats.startswith("[") else [cats]
                if cats:
                    meta_parts.append(" · ".join(cats))

                length = novel.get("length", "")
                if length:
                    meta_parts.append(length)

                sts = novel.get("styles", [])
                if isinstance(sts, str):
                    sts = json.loads(sts) if sts.startswith("[") else [sts]
                if sts:
                    meta_parts.append(" · ".join(sts))

                st.caption(" · ".join(meta_parts))

                synopsis = novel.get("synopsis", "")
                if synopsis:
                    st.markdown(synopsis[:150] + ("..." if len(synopsis) > 150 else ""))

                created = novel.get("created_at", "")
                if created:
                    try:
                        dt = datetime.fromisoformat(created)
                        st.caption(f"创建于 {dt.strftime('%Y-%m-%d %H:%M')}")
                    except Exception:
                        pass

            with col2:
                if st.button("📖 阅读", key=f"read_{novel.get('id', '')}"):
                    # Load novel into session state
                    st.session_state.workshop_config = novel.get("config", {})
                    st.session_state.workshop_outline = novel.get("outline", [])
                    st.session_state.generated_chapters = novel.get("chapters", {})
                    st.session_state.final_title = novel.get("title", "未命名")
                    st.session_state.novel_synopsis = novel.get("synopsis", "")
                    st.session_state.reader_current_chapter = 0
                    st.session_state.workshop_step = "reading"
                    st.session_state.page = "workshop"
                    st.rerun()

            with col3:
                if st.button("🗑", key=f"del_{novel.get('id', '')}", help="删除"):
                    if SUPABASE_AVAILABLE:
                        supabase_url = st.secrets.get("SUPABASE_URL", "")
                        supabase_key = st.secrets.get("SUPABASE_ANON_KEY", "")
                        store = NovelStore(supabase_url, supabase_key)
                        store.delete_novel(novel["id"])
                    else:
                        local = st.session_state.get("local_novels", [])
                        local = [n for n in local if n.get("id") != novel.get("id")]
                        st.session_state.local_novels = local
                    st.rerun()

            st.divider()
