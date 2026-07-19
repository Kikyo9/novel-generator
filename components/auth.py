"""Authentication component: login and register UI."""
import streamlit as st
from utils.supabase_client import NovelStore


def get_supabase_store() -> NovelStore | None:
    """Get or create a shared Supabase store with auth session."""
    if "_supabase_store" not in st.session_state:
        su_url = st.secrets.get("SUPABASE_URL", "")
        su_key = st.secrets.get("SUPABASE_ANON_KEY", "")
        if su_url and "your-project" not in su_url:
            store = NovelStore(su_url, su_key)
            st.session_state._supabase_store = store
    store = st.session_state.get("_supabase_store")
    if store and store.is_connected():
        access_token = st.session_state.get("_supabase_access_token", "")
        refresh_token = st.session_state.get("_supabase_refresh_token", "")
        if access_token:
            try:
                store.client.auth.set_session(access_token, refresh_token)
            except Exception:
                pass
    return store


def render_auth():
    """Render login/register form. Returns True if logged in."""
    store = get_supabase_store()
    if store is None or not store.is_connected():
        st.sidebar.warning("Supabase not configured")
        return False

    # Already logged in
    if st.session_state.get("supabase_user"):
        with st.sidebar:
            st.markdown(f"👤 **{st.session_state.supabase_user.get('email', '')}**")
            if st.button("🚪 \u9000\u51fa登录", key="logout_btn"):
                store.sign_out()
                st.session_state.supabase_user = None
                st.session_state.user_id = ""
                st.session_state._supabase_access_token = ""
                st.session_state._supabase_refresh_token = ""
                st.rerun()
        return True

    # Login/Register
    with st.sidebar:
        st.markdown("---")
        tab1, tab2 = st.tabs(["登录", "注册"])

        with tab1:
            email = st.text_input("邮箱", key="login_email")
            password = st.text_input("密码", type="password", key="login_password")
            if st.button("登录", type="primary", use_container_width=True, key="login_btn"):
                if not email or not password:
                    st.error("\u8bf7\u8f93\u5165邮箱\u548c密码")
                else:
                    result = store.sign_in(email, password)
                    if "user" in result:
                        st.session_state.supabase_user = result["user"]
                        st.session_state.user_id = result["user"]["id"]
                        try:
                            sess = store.client.auth.get_session()
                            if sess:
                                st.session_state._supabase_access_token = sess.access_token
                                st.session_state._supabase_refresh_token = getattr(sess, 'refresh_token', '')
                        except Exception:
                            pass
                        st.rerun()
                    else:
                        st.error(result.get("error", "登录\u5931\u8d25"))

        with tab2:
            email_r = st.text_input("邮箱", key="reg_email")
            password_r = st.text_input("密码", type="password", key="reg_password")
            if st.button("注册", type="primary", use_container_width=True, key="reg_btn"):
                if not email_r or not password_r:
                    st.error("\u8bf7\u8f93\u5165邮箱\u548c密码")
                elif len(password_r) < 6:
                    st.error("密码\u81f3\u5c116\u4f4d")
                else:
                    result = store.sign_up(email_r, password_r)
                    if "user" in result:
                        st.session_state.supabase_user = result["user"]
                        st.session_state.user_id = result["user"]["id"]
                        try:
                            sess = store.client.auth.get_session()
                            if sess:
                                st.session_state._supabase_access_token = sess.access_token
                                st.session_state._supabase_refresh_token = getattr(sess, 'refresh_token', '')
                        except Exception:
                            pass
                        st.rerun()
                    else:
                        st.error(result.get("error", "注册\u5931\u8d25"))

    return False
