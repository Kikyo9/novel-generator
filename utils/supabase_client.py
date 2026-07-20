"""Supabase client wrapper for novel storage and authentication."""
import json
from datetime import datetime
from supabase import create_client, Client


class NovelStore:
    """Store and retrieve novels using Supabase."""

    def __init__(self, url: str = "", key: str = ""):
        self.client: Client | None = None
        if url and key:
            try:
                self.client = create_client(url, key)
            except Exception:
                self.client = None

    def is_connected(self) -> bool:
        return self.client is not None

    # ---- Auth ----
    def sign_up(self, email: str, password: str) -> dict:
        """Register a new user."""
        if not self.client:
            return {"error": "Supabase not connected"}
        try:
            res = self.client.auth.sign_up({"email": email, "password": password})
            if res.user:
                return {"user": {"id": res.user.id, "email": res.user.email}}
            return {"error": "注册失败"}
        except Exception as e:
            return {"error": str(e)}

    def sign_in(self, email: str, password: str) -> dict:
        """Login existing user."""
        if not self.client:
            return {"error": "Supabase not connected"}
        try:
            res = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                return {"user": {"id": res.user.id, "email": res.user.email}}
            return {"error": "登录失败"}
        except Exception as e:
            return {"error": str(e)}

    def sign_out(self):
        """Logout current user."""
        if self.client:
            try:
                self.client.auth.sign_out()
            except Exception:
                pass

    # ---- Novels CRUD ----
    def save_novel(self, user_id: str, novel_data: dict) -> str:
        """Save a novel to Supabase. Returns novel_id or empty string."""
        if not self.client:
            return ""
        # Ensure postgrest auth is set from session state if available
        import streamlit as st
        try:
            access_token = st.session_state.get("_supabase_access_token", "")
            if access_token:
                self.client.postgrest.auth(access_token)
        except Exception:
            pass
        payload = {
            "user_id": user_id,
            "title": novel_data.get("title", "未命名"),
            "categories": novel_data.get("categories", []),
            "protagonist": novel_data.get("protagonist", ""),
            "length": novel_data.get("length", ""),
            "styles": novel_data.get("styles", []),
            "synopsis": novel_data.get("synopsis", ""),
            "outline": json.dumps(novel_data.get("outline", []), ensure_ascii=False),
            "chapters": json.dumps(novel_data.get("chapters", {}), ensure_ascii=False),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        payload["config"] = json.dumps(novel_data.get("config", {}), ensure_ascii=False)
        return self._insert_novel(payload)

    def _insert_novel(self, payload: dict) -> str:
        """Insert novel with graceful fallback for older schemas without config column."""
        try:
            result = self.client.table("novels").insert(payload).execute()
            if result.data:
                return result.data[0].get("id", "")
            else:
                import sys
                print(f"Supabase insert: no data returned, result={result}", file=sys.stderr)
        except Exception as e:
            err_msg = str(e).lower()
            if "config" in err_msg or "column" in err_msg or "unknown field" in err_msg:
                fallback = {k: v for k, v in payload.items() if k != "config"}
                try:
                    result = self.client.table("novels").insert(fallback).execute()
                    if result.data:
                        return result.data[0].get("id", "")
                except Exception as e2:
                    import sys
                    print(f"Supabase insert fallback error: {e2}", file=sys.stderr)
            else:
                import sys
                print(f"Supabase insert error: {e}", file=sys.stderr)
        return ""

    def update_novel(self, novel_id: str, novel_data: dict) -> bool:
        """Update an existing novel."""
        if not self.client:
            return False
        # Ensure postgrest auth is set from session state if available
        import streamlit as st
        try:
            access_token = st.session_state.get("_supabase_access_token", "")
            if access_token:
                self.client.postgrest.auth(access_token)
        except Exception:
            pass
        payload = {
            "title": novel_data.get("title"),
            "outline": json.dumps(novel_data.get("outline", []), ensure_ascii=False),
            "chapters": json.dumps(novel_data.get("chapters", {}), ensure_ascii=False),
            "synopsis": novel_data.get("synopsis", ""),
            "config": json.dumps(novel_data.get("config", {}), ensure_ascii=False),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return self._update_novel(novel_id, payload)

    def _update_novel(self, novel_id: str, payload: dict) -> bool:
        """Update novel with graceful fallback for older schemas without config column."""
        try:
            result = self.client.table("novels").update(payload).eq("id", novel_id).execute()
            return bool(result.data)
        except Exception as e:
            err_msg = str(e).lower()
            if "config" in err_msg or "column" in err_msg or "unknown field" in err_msg:
                fallback = {k: v for k, v in payload.items() if k != "config"}
                try:
                    result = self.client.table("novels").update(fallback).eq("id", novel_id).execute()
                    return bool(result.data)
                except Exception:
                    return False
            return False

    def get_user_novels(self, user_id: str) -> list:
        """Fetch all novels for a user."""
        if not self.client:
            return []
        try:
            result = (self.client.table("novels")
                      .select("*")
                      .eq("user_id", user_id)
                      .order("updated_at", desc=True)
                      .execute())
            novels = []
            for row in (result.data or []):
                config_raw = row.get("config", "{}")
                try:
                    config = json.loads(config_raw) if isinstance(config_raw, str) else config_raw
                except Exception:
                    config = {}
                novels.append({
                    "id": row["id"],
                    "title": row.get("title", "未命名"),
                    "categories": row.get("categories", []),
                    "length": row.get("length", ""),
                    "styles": row.get("styles", []),
                    "synopsis": row.get("synopsis", ""),
                    "outline": json.loads(row.get("outline", "[]")),
                    "chapters": json.loads(row.get("chapters", "{}")),
                    "config": config,
                    "created_at": row.get("created_at", ""),
                    "updated_at": row.get("updated_at", ""),
                })
            return novels
        except Exception:
            return []

    def delete_novel(self, novel_id: str) -> bool:
        """Delete a novel."""
        if not self.client:
            return False
        try:
            self.client.table("novels").delete().eq("id", novel_id).execute()
            return True
        except Exception:
            return False
