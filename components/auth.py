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
    # Restore session if we have stored tokens
    if store and store.is_connected():
        access_token = st.session_state.get("_supabase_access_token", "")
        refresh_token = st.session_state.get("_supabase_refresh_token", "")
        if access_token:
            try:
                store.client.postgrest.auth(access_token)
            except Exception:
                pass
    return store


def render_auth():
    """Render login/register form. Returns True if logged in."""
    store = get_supabase_store()
    if store is None or not store.is_connected():
        st.sidebar.warning("Supabase 未配置")
        return False

    # Check existing session
    if st.session_state.get("supabase_user"):
        with st.sidebar:
            user = st.session_state.supabase_user
            st.markdown(f"👤 **{user.get('email', '')}**")
            if st.button("🚪 退出登录", key="logout_btn"):
                store.sign_out()
                st.session_state.supabase_user = None
                st.session_state.user_id = ""
                st.rerun()
        return True

    # Login/Register form in sidebar
    with st.sidebar:
        st.markdown("---")
        tab1, tab2 = st.tabs(["登录", "注册"])

        with tab1:
            st.markdown("#### 登录")
            email = st.text_input("邮箱", key="login_email")
            password = st.text_input("密码", type="password", key="login_password")
            if st.button("登录", type="primary", use_container_width=True, key="login_btn"):
                if not email or not password:
                    st.error("请输入邮箱和密码")
                else:
                    result = store.sign_in(email, password)
                    if "user" in result:
                        st.session_state.supabase_user = result["user"]
                        st.session_state.user_id = result["user"]["id"]
                        # Store session for later API calls
                        if hasattr(store.client, 'auth') and hasattr(store.client.auth, 'current_session'):
                            sess = store.client.auth.current_session
                            if sess:
                                st.session_state._supabase_access_token = sess.access_token
                                st.session_state._supabase_refresh_token = getattr(sess, 'refresh_token', '')
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error(result.get("error", "登录失败"))

        with tab2:
            st.markdown("#### 注册")
            email_reg = st.text_input("邮箱", key="reg_email")
            password_reg = st.text_input("密码", type="password", key="reg_password")
            if st.button("注册", type="primary", use_container_width=True, key="reg_btn"):
                if not email_reg or not password_reg:
                    st.error("请输入邮箱和密码")
                elif len(password_reg) < 6:
                    st.error("密码至少6位")
                else:
                    result = store.sign_up(email_reg, password_reg)
                    if "user" in result:
                        st.session_state.supabase_user = result["user"]
                        st.session_state.user_id = result["user"]["id"]
                        if hasattr(store.client, 'auth') and hasattr(store.client.auth, 'current_session'):
                            sess = store.client.auth.current_session
                            if sess:
                                st.session_state._supabase_access_token = sess.access_token
                                st.session_state._supabase_refresh_token = getattr(sess, 'refresh_token', '')
                        st.success("注册成功！")
                        st.rerun()
                    else:
                        st.error(result.get("error", "注册失败"))

    return False
