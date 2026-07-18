"""Settings page."""
import streamlit as st


def render_settings():
    """Render the settings page."""
    st.markdown("### ⚙️ 设置")

    # About section
    st.markdown("#### 关于网文生成工坊")
    st.markdown("""
    **版本**: 1.0.0

    网文生成工坊是一个基于 AI 的网络小说创作工具。只需设定分类、
    主角、篇幅和风格，AI 就能为你生成一部完整的网络小说。

    **技术栈**:
    - 前端: Streamlit
    - AI 引擎: DeepSeek
    - 数据存储: Supabase

    **使用说明**:
    1. 在「创作工坊」中填写小说设定
    2. AI 生成大纲后，你可以编辑、调整、添加注释
    3. 确认大纲后，AI 逐章生成内容
    4. 在阅读器中沉浸式阅读，支持字号/行距调节和夜间模式
    5. 支持下载 TXT / EPUB 格式
    """)

    st.markdown("---")

    # API Configuration hint
    st.markdown("#### 🔑 API 配置")

    ds_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if ds_key and ds_key != "sk-your-deepseek-api-key":
        st.success("DeepSeek API Key 已配置 ✓")
    else:
        st.warning("DeepSeek API Key 未配置。请在 .streamlit/secrets.toml 中设置 DEEPSEEK_API_KEY")

    supa_url = st.secrets.get("SUPABASE_URL", "")
    supa_key = st.secrets.get("SUPABASE_ANON_KEY", "")
    if supa_url and supa_url != "https://your-project.supabase.co":
        st.success("Supabase 已配置 ✓")
    else:
        st.info("Supabase 未配置。当前使用本地存储（刷新页面会丢失数据）。")

    st.caption("配置说明：在项目根目录的 .streamlit/secrets.toml 文件中填入你的 API Key")
