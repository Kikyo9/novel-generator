"""Authentication component: login and register UI."""
import streamlit as st
from utils.supabase_client import NovelStore


def render_auth():
    """Render login/register form. Returns True if logged in."""
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_ANON_KEY", "")

    if not supabase_url or "your-project" in supabase_url:
        st.sidebar.warning("Supabase 未配置")
        return False

    store = NovelStore(supabase_url, supabase_key)
    if not store.is_connected():
        st.sidebar.warning("无法连接 Supabase")
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
                        st.success("注册成功！请查看邮箱确认（或已自动登录）")
                        st.session_state.supabase_user = result["user"]
                        st.session_state.user_id = result["user"]["id"]
                        st.rerun()
                    else:
                        st.error(result.get("error", "注册失败"))

    return False
