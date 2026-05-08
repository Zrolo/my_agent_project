import json
import os
import tempfile
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
import noi_agent
from auth import create_token
from database import init_db


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


class AIChatModelSwitchUnitTests(unittest.TestCase):
    def setUp(self):
        init_db()
        api_server.app.dependency_overrides.clear()
        api_server.session_histories.clear()
        self.client = TestClient(api_server.app)
        suffix = int(time.time() * 1000)
        self.student_id = f"model_student_{suffix}"

    def test_model_options_show_availability_without_exposing_api_keys(self):
        with patch.dict(
            os.environ,
            {
                "MIMO_API_KEY": "mimo-secret",
                "DEEPSEEK_API_KEY": "deepseek-secret",
                "MOONSHOT_API_KEY": "",
                "NOI_DEFAULT_CHAT_PROVIDER": "deepseek_flash",
            },
            clear=False,
        ):
            payload = noi_agent.list_chat_model_options()

        encoded = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("mimo-secret", encoded)
        self.assertNotIn("deepseek-secret", encoded)
        self.assertEqual("deepseek_flash", payload["default_provider"])
        providers = {item["provider_id"]: item for item in payload["models"]}
        self.assertEqual({"deepseek_flash", "deepseek_pro"}, set(providers))
        self.assertTrue(providers["deepseek_flash"]["available"])
        self.assertTrue(providers["deepseek_pro"]["available"])
        self.assertEqual("DeepSeek 快速", providers["deepseek_flash"]["label"])
        self.assertEqual("DeepSeek 专业", providers["deepseek_pro"]["label"])

    def test_local_env_loader_sets_missing_model_keys_without_overwriting_existing_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("MIMO_API_KEY=from-file-mimo\n")
                f.write("DEEPSEEK_API_KEY='from-file-deepseek'\n")

            with patch.dict(os.environ, {"MIMO_API_KEY": "already-set"}, clear=True):
                loaded = noi_agent.load_local_env_if_present(env_path)

                self.assertEqual("already-set", os.environ["MIMO_API_KEY"])
                self.assertEqual("from-file-deepseek", os.environ["DEEPSEEK_API_KEY"])
                self.assertEqual(["DEEPSEEK_API_KEY"], loaded)

    def test_chat_models_endpoint_returns_safe_student_options(self):
        with patch.dict(
            os.environ,
            {
                "MIMO_API_KEY": "mimo-secret",
                "DEEPSEEK_API_KEY": "deepseek-secret",
                "MOONSHOT_API_KEY": "",
                "NOI_DEFAULT_CHAT_PROVIDER": "deepseek_flash",
            },
            clear=False,
        ):
            response = self.client.get("/api/chat/models", headers=auth_headers(self.student_id))

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("deepseek_flash", payload["default_provider"])
        self.assertEqual(["deepseek_flash", "deepseek_pro"], [item["provider_id"] for item in payload["models"]])
        self.assertNotIn("mimo-secret", json.dumps(payload, ensure_ascii=False))
        self.assertNotIn("deepseek-secret", json.dumps(payload, ensure_ascii=False))

    def test_chat_endpoint_passes_selected_model_provider_to_agent(self):
        captured = {}

        def fake_chat(messages, student_id, problem_id, chat_model_provider=None):
            captured["chat_model_provider"] = chat_model_provider
            return "我们先看你当前这一步。", "我们先看你当前这一步。", "L2"

        with patch.object(api_server, "chat", side_effect=fake_chat):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.student_id),
                json={
                    "student_id": self.student_id,
                    "problem_id": "P405",
                    "session_id": "sess_model_switch",
                    "message": "为什么这里要二分？",
                    "problem_title": "测试题",
                    "chat_model_provider": "deepseek_pro",
                },
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual("deepseek_pro", captured["chat_model_provider"])
        self.assertEqual("deepseek_pro", response.json()["chat_model_provider"])
        self.assertIn("专业", response.json()["chat_model_label"])

    def test_legacy_deepseek_provider_aliases_to_pro_mode(self):
        profile = noi_agent.resolve_chat_model_profile("deepseek")

        self.assertEqual("deepseek_pro", profile.provider_id)
        self.assertEqual("deepseek-v4-pro", profile.model)

    def test_deepseek_fast_and_pro_use_distinct_models_with_thinking_enabled(self):
        flash = noi_agent._profile_by_provider("deepseek_flash")
        pro = noi_agent._profile_by_provider("deepseek_pro")

        self.assertEqual("deepseek-v4-flash", flash.model)
        self.assertEqual("deepseek-v4-pro", pro.model)
        self.assertEqual("enabled", flash.thinking_mode)
        self.assertEqual("enabled", pro.thinking_mode)
        self.assertEqual({"thinking": {"type": "enabled"}}, flash.extra_body)
        self.assertEqual({"thinking": {"type": "enabled"}}, pro.extra_body)

    def test_kimi_defaults_to_large_max_completion_tokens(self):
        with patch.dict(os.environ, {"NOI_CHAT_MAX_COMPLETION_TOKENS": ""}, clear=False):
            kimi = noi_agent._profile_by_provider("kimi")
            deepseek = noi_agent._profile_by_provider("deepseek_pro")

            self.assertGreaterEqual(noi_agent.chat_max_completion_tokens_for_profile(kimi), 30000)
            self.assertIsNone(noi_agent.chat_max_completion_tokens_for_profile(deepseek))

    def test_explicit_chat_max_tokens_overrides_kimi_default(self):
        with patch.dict(os.environ, {"NOI_CHAT_MAX_COMPLETION_TOKENS": "4096"}, clear=False):
            kimi = noi_agent._profile_by_provider("kimi")

            self.assertEqual(4096, noi_agent.chat_max_completion_tokens_for_profile(kimi))

    def test_deepseek_pedagogical_judge_uses_light_json_request(self):
        deepseek = noi_agent._profile_by_provider("deepseek_pro")

        with patch.dict(os.environ, {"NOI_PEDAGOGICAL_JUDGE_MAX_TOKENS": ""}, clear=False):
            kwargs = noi_agent.build_pedagogical_judge_request_kwargs(
                deepseek,
                [{"role": "user", "content": "只输出 JSON"}],
            )

        self.assertEqual("deepseek-v4-pro", kwargs["model"])
        self.assertEqual({"type": "json_object"}, kwargs["response_format"])
        self.assertEqual({"thinking": {"type": "disabled"}}, kwargs["extra_body"])
        self.assertEqual(4096, kwargs["max_tokens"])
        self.assertNotIn("temperature", kwargs)

    def test_deepseek_pedagogical_judge_max_tokens_can_be_overridden(self):
        deepseek = noi_agent._profile_by_provider("deepseek_pro")

        with patch.dict(os.environ, {"NOI_PEDAGOGICAL_JUDGE_MAX_TOKENS": "4096"}, clear=False):
            kwargs = noi_agent.build_pedagogical_judge_request_kwargs(
                deepseek,
                [{"role": "user", "content": "只输出 JSON"}],
            )

        self.assertEqual(4096, kwargs["max_tokens"])

    def test_offline_deepseek_judge_uses_official_max_tokens_field(self):
        deepseek = noi_agent._offline_judge_profile("deepseek")

        kwargs = noi_agent._offline_json_judge_request_kwargs(
            profile=deepseek,
            messages=[{"role": "user", "content": "只输出 JSON"}],
            max_tokens_env="NOI_BRIDGE_JUDGE_MAX_TOKENS",
            default_max_tokens="1024",
            timeout_env="NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS",
            default_timeout="5.0",
        )

        self.assertEqual(1024, kwargs["max_tokens"])
        self.assertNotIn("max_completion_tokens", kwargs)

    def test_offline_kimi_judge_uses_official_max_completion_tokens_field(self):
        kimi = noi_agent._offline_judge_profile("kimi")

        kwargs = noi_agent._offline_json_judge_request_kwargs(
            profile=kimi,
            messages=[{"role": "user", "content": "只输出 JSON"}],
            max_tokens_env="NOI_BRIDGE_JUDGE_MAX_TOKENS",
            default_max_tokens="1024",
            timeout_env="NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS",
            default_timeout="5.0",
        )

        self.assertEqual(1024, kwargs["max_completion_tokens"])
        self.assertNotIn("max_tokens", kwargs)


if __name__ == "__main__":
    unittest.main()
