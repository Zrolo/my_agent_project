import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
import noi_agent
import review_engine
from auth import create_token
from database import (
    LEARNING_STATUS_NEEDS_TEACHER,
    LEARNING_STATUS_RESOLVED,
    REVIEW_STATUS_COMPLETED,
    REVIEW_STATUS_PENDING,
    create_checkin,
    create_pending_review,
    create_review_quiz,
    create_review,
    get_review_by_checkin,
    get_review_manual_review,
    get_review_events_for_checkin,
    get_bridge_rule_draft_decision,
    mark_review_failed,
    mark_review_pending,
    record_quiz_attempt,
    update_review_bridge_path,
    update_review_learning_status,
    update_review_mastery_status,
)


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


def teacher_headers(teacher_id: str = "teacher") -> dict:
    token = create_token(teacher_id, "teacher")
    return {"Authorization": f"Bearer {token}"}


class ReviewAsyncApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)
        self.owner_id = f"student_owner_{int(time.time() * 1000)}"
        self.other_id = f"student_other_{int(time.time() * 1000)}"

    def _create_checkin(self, student_id: str, title: str = "测试题") -> int:
        return create_checkin(
            student_id=student_id,
            problem_url="https://example.com/problem",
            problem_title=title,
            oj_source="other",
            completion_status="unfinished",
            bottleneck_text="我总把时间条件和地点条件看成主次关系，不知道是不是要同时满足。",
            error_types=["模型转化"],
            reflection="这里像是并列约束，不是主次条件。",
            problem_context="每个活动都必须同时满足时间窗口和指定地点两个条件。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="wa",
            student_code="",
            session_id=f"checkin_test_{int(time.time() * 1000)}",
        )

    def test_student_checkin_detail_requires_owner(self):
        checkin_id = self._create_checkin(self.owner_id, "owner-checkin")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.other_id),
        )

        self.assertEqual(404, response.status_code)

    def test_frontend_history_routes_serve_spa_entry(self):
        for path in (
            "/app",
            "/app/chat",
            "/app/checkin",
            "/app/history",
            "/app/history/12345",
            "/app/teacher",
            "/app/teacher/quota",
            "/app/teacher/checkins",
            "/app/teacher/stats",
            "/app/teacher/manual-review",
            "/app/teacher/flags",
        ):
            response = self.client.get(path)
            self.assertEqual(200, response.status_code)
            self.assertIn("text/html", response.headers.get("content-type", ""))

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            "/auth/login",
            json={"user_id": "student_a", "password": "wrong-password"},
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual("Invalid user_id or password", response.json()["detail"])

    def test_chat_endpoint_passes_current_problem_context_to_agent(self):
        captured = {}

        def fake_chat(messages, student_id, problem_id):
            captured["messages"] = [dict(message) for message in messages]
            captured["student_id"] = student_id
            captured["problem_id"] = problem_id
            return "先看路径上的点怎么被计数。", "先看路径上的点怎么被计数。", "L1"

        with patch.object(api_server, "chat", side_effect=fake_chat):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.owner_id),
                json={
                    "student_id": self.owner_id,
                    "problem_id": "P3128",
                    "message": "我不知道这里为什么要用树上差分。",
                    "session_id": f"sess_context_{self.owner_id}",
                    "problem_title": "P3128 [USACO15DEC] Max Flow P",
                    "problem_url": "https://www.luogu.com.cn/problem/P3128",
                    "problem_context": "给一棵树和多条运输路径，要求统计经过次数最多的点。",
                    "student_code": "diff[u]++; diff[v]++; diff[lca]-=2;",
                },
            )

        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual(self.owner_id, captured["student_id"])
        self.assertEqual("P3128", captured["problem_id"])
        last_user_message = [message for message in captured["messages"] if message["role"] == "user"][-1]["content"]
        self.assertIn("当前题目上下文", last_user_message)
        self.assertIn("P3128 [USACO15DEC] Max Flow P", last_user_message)
        self.assertIn("多条运输路径", last_user_message)
        self.assertIn("diff[u]++", last_user_message)
        self.assertIn("我不知道这里为什么要用树上差分。", last_user_message)

    def test_chat_endpoint_should_not_read_hint_quota(self):
        def fake_chat(messages, student_id, problem_id):
            return "先把题目对象说清楚。", "先把题目对象说清楚。", "L1"

        with (
            patch.object(api_server, "chat", side_effect=fake_chat),
            patch.object(api_server, "get_remaining_quota", side_effect=AssertionError("学生端聊天接口不应读取旧配额")),
        ):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.owner_id),
                json={
                    "student_id": self.owner_id,
                    "problem_id": "P3128",
                    "message": "这题怎么开始？",
                    "session_id": f"sess_no_quota_{self.owner_id}",
                    "problem_context": "给一棵树和多条运输路径。",
                },
            )

        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual("先把题目对象说清楚。", response.json()["reply"])
        self.assertEqual(0, response.json()["remaining_quota"])

    def test_chat_endpoint_auto_imports_luogu_context_when_only_problem_ref_is_provided(self):
        captured = {}

        def fake_fetch(raw_url):
            captured["fetch_ref"] = raw_url
            return {
                "problem_url": "https://www.luogu.com.cn/problem/P3128",
                "problem_title": "P3128 [USACO15DEC] Max Flow P",
                "problem_context": "给一棵树和多条运输路径，要求统计经过次数最多的点。",
                "problem_tags": ["树上差分", "LCA"],
                "oj_source": "luogu",
            }

        def fake_chat(messages, student_id, problem_id):
            captured["messages"] = [dict(message) for message in messages]
            captured["student_id"] = student_id
            captured["problem_id"] = problem_id
            return "先把一条路径对端点和 LCA 的贡献写出来。", "先把一条路径对端点和 LCA 的贡献写出来。", "L1"

        with patch.object(api_server, "fetch_luogu_problem", side_effect=fake_fetch), patch.object(api_server, "chat", side_effect=fake_chat):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.owner_id),
                json={
                    "student_id": self.owner_id,
                    "problem_id": "P3128",
                    "message": "这题我只知道是 LCA，但不知道怎么统计。",
                    "session_id": f"sess_auto_import_{self.owner_id}",
                },
            )

        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual("https://www.luogu.com.cn/problem/P3128", captured["fetch_ref"])
        last_user_message = [message for message in captured["messages"] if message["role"] == "user"][-1]["content"]
        self.assertIn("P3128 [USACO15DEC] Max Flow P", last_user_message)
        self.assertIn("多条运输路径", last_user_message)
        self.assertIn("这题我只知道是 LCA", last_user_message)

    def test_chat_endpoint_returns_handoff_payload_for_ac_unclear(self):
        with patch.object(api_server, "chat", return_value=("请去打卡复盘。", "请去打卡复盘。", "L2")):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.owner_id),
                json={
                    "student_id": self.owner_id,
                    "problem_id": "P3128",
                    "message": "我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。",
                    "session_id": f"sess_handoff_{self.owner_id}",
                    "problem_title": "P3128 [USACO15DEC] Max Flow P",
                    "problem_url": "https://www.luogu.com.cn/problem/P3128",
                    "problem_context": "给一棵树和多条运输路径，要求统计经过次数最多的点。",
                },
            )

        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()["handoff_payload"]
        self.assertEqual("checkin_reflection", payload["handoff_type"])
        self.assertEqual("aichat", payload["source"])
        self.assertEqual("ac_unclear_in_aichat", payload["risk_type"])
        self.assertEqual("P3128", payload["problem_ref"])
        self.assertIn("复盘已 AC", payload["suggested_focus"])

    def test_chat_tutor_policy_keeps_type_confirm_redline_without_legacy_policy_block(self):
        control = noi_agent.analyze_student_turn("这题是不是用树剖 LCA 加差分？", [])

        tutor_control = control.get("tutor_control") or {}
        self.assertEqual("Z2", tutor_control.get("zpd_level"))
        self.assertEqual(1, tutor_control.get("scaffold_stage"))
        self.assertEqual("ask_evidence_question", tutor_control.get("tutor_action"))
        self.assertIn("禁止确认/否认题型", tutor_control.get("forbidden", []))

        prompt = noi_agent.build_system_prompt(
            control,
            remaining=3,
            student_id=self.owner_id,
            problem_id="P3128",
        )

        self.assertNotIn("SOCRATIC_POLICY", prompt)
        self.assertNotIn("Adaptive Scaffolding", prompt)
        self.assertNotIn("Evidence-Driven Feedback", prompt)
        self.assertIn("ask_evidence_question", prompt)
        self.assertIn("type_confirm 特殊约束", prompt)
        self.assertIn("不能确认题型", prompt)
        self.assertIn("必须把反问落到题面中的具体对象、条件或结构证据", prompt)
        self.assertNotIn("只能反问：\"你为什么会这么猜？\"", prompt)
        self.assertLess(len(prompt), 3000)

    def test_chat_output_guard_is_noop_even_for_complete_solution_or_code_words(self):
        level_control = {"bridge_redline": False}
        risk_control = {"risk_tags": []}

        guarded, trigger = noi_agent.enforce_output_guards(
            "完整做法是先树剖求 LCA，然后树上差分，完整代码如下：int main(){return 0;}",
            level_control,
            risk_control,
        )

        self.assertIsNone(trigger)
        self.assertIn("完整代码如下", guarded)
        self.assertIn("int main", guarded)

    def test_chat_type_confirm_generic_reply_is_not_backend_rewritten(self):
        level_control = {"bridge_redline": False}
        risk_control = {"risk_tags": ["type_confirm"]}
        messages = [
            {
                "role": "user",
                "content": "[学生原始问题]\n这题是不是用 trie 才对？\n\n[当前题目上下文]\n给定很多 01 消息串和拦截串，需要统计前缀包含关系，数据量较大。",
            }
        ]

        guarded, trigger = noi_agent.enforce_output_guards(
            "先别急着确认题型。你为什么会这么猜？",
            level_control,
            risk_control,
            messages=messages,
        )

        self.assertIsNone(trigger)
        self.assertEqual("先别急着确认题型。你为什么会这么猜？", guarded)

    def test_chat_analysis_ignores_injected_problem_context_instructions(self):
        message = "\n".join(
            [
                "[学生原始问题]",
                "这题是不是用 trie 才对？",
                "",
                "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                "题面/题意/约束: 给定很多 01 消息串和拦截串，需要统计前缀包含关系，数据量较大。",
                "",
                "请优先围绕学生当前问题给渐进提示；不要直接给完整题解或最终代码。",
            ]
        )

        control = noi_agent.analyze_student_turn(message, [{"role": "user", "content": message}])

        self.assertEqual("L2", control["level_control"]["max_level"])
        self.assertIn("type_confirm", control["risk_control"]["risk_tags"])
        self.assertNotIn("direct_request", control["risk_control"]["risk_tags"])

    def test_chat_full_flow_keeps_model_type_confirm_reply_without_backend_rewrite(self):
        class FakeCompletions:
            def create(self, **kwargs):
                class Message:
                    content = "先别急着确认题型。你为什么会这么猜？\n\n[LEVEL:L2]"

                class Choice:
                    message = Message()

                class Response:
                    choices = [Choice()]

                return Response()

        class FakeChat:
            completions = FakeCompletions()

        class FakeClient:
            chat = FakeChat()

        message = "\n".join(
            [
                "[学生原始问题]",
                "这题是不是用 trie 才对？",
                "",
                "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                "题面/题意/约束: 给定很多 01 消息串和拦截串，需要统计前缀包含关系，数据量较大。",
            ]
        )

        with (
            patch.object(noi_agent, "get_remaining_quota", return_value=3),
            patch.object(noi_agent, "get_client", return_value=FakeClient()),
        ):
            reply_for_display, reply_for_history, final_level = noi_agent.chat(
                [{"role": "user", "content": message}],
                "student",
                "P2922::case",
            )

        self.assertEqual("L2", final_level)
        self.assertIn("为什么会这么猜", reply_for_history)
        self.assertNotIn("01", reply_for_history)
        self.assertNotIn("前缀", reply_for_history)
        self.assertNotIn("本题还剩", reply_for_display)
        self.assertNotIn("提示配额", reply_for_display)

    def test_checkin_validation_uses_reflection_as_detail_evidence(self):
        payload = {
            "problem_url": "P2249",
            "problem_title": "查找",
            "oj_source": "other",
            "completion_status": "unfinished",
            "bottleneck_text": "不知道为什么要 r = mid",
            "error_types": ["未说明"],
            "reflection": "我试过 r = mid - 1，但是会漏掉最左边那个等于 x 的位置。",
            "problem_context": "给定一个非降序数组，多次询问某个数第一次出现的位置。",
            "problem_tags": [],
            "chat_context_summary": "",
            "submission_result": "not_submitted",
            "student_code": "",
        }

        with patch.object(api_server, "_start_review_generation_job"):
            response = self.client.post(
                "/api/checkins",
                headers=auth_headers(self.owner_id),
                json=payload,
            )

        self.assertEqual(200, response.status_code, response.text)

    def test_create_checkin_passes_handoff_payload_to_review_generation_job(self):
        handoff_payload = {
            "handoff_type": "checkin_reflection",
            "source": "aichat",
            "risk_type": "ac_unclear_in_aichat",
            "problem_ref": "P3128",
            "last_user_message": "我 P3128 AC 了但感觉是蒙的。",
            "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。",
        }
        payload = {
            "problem_url": "P3128",
            "problem_title": "P3128",
            "oj_source": "other",
            "completion_status": "independent",
            "bottleneck_text": "我已经通过了，但我不太清楚为什么这几个差分标记能还原路径经过次数。",
            "error_types": ["关键桥不稳"],
            "reflection": "我想确认端点和公共祖先附近的标记到底各自承担什么作用。",
            "problem_context": "给定一棵树和多条路径，统计每个点被路径经过的次数。",
            "problem_tags": [],
            "chat_context_summary": "",
            "submission_result": "not_submitted",
            "student_code": "",
            "handoff_payload": handoff_payload,
        }

        with patch.object(api_server, "_start_review_generation_job", return_value=None) as mocked_start:
            response = self.client.post(
                "/api/checkins",
                headers=auth_headers(self.owner_id),
                json=payload,
            )

        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual(handoff_payload, mocked_start.call_args.kwargs["handoff_payload"])

    def test_create_checkin_infers_non_luogu_source_from_problem_url(self):
        payload = {
            "problem_url": "https://codeforces.com/contest/4/problem/A",
            "problem_title": "Watermelon",
            "oj_source": "luogu",
            "completion_status": "unfinished",
            "bottleneck_text": "我不知道应该先判断奇偶还是直接枚举拆分重量。",
            "error_types": ["未说明"],
            "reflection": "我试过把重量拆成两个数，但没有先排除两个偶数必须都大于 0 的情况。",
            "problem_context": "给定一个整数 w，判断能否拆成两个正偶数之和。",
            "problem_tags": [],
            "chat_context_summary": "",
            "submission_result": "not_submitted",
            "student_code": "",
        }

        with patch.object(api_server, "_start_review_generation_job"), patch.object(api_server, "fetch_luogu_problem") as mocked_import:
            response = self.client.post(
                "/api/checkins",
                headers=auth_headers(self.owner_id),
                json=payload,
            )

        self.assertEqual(200, response.status_code, response.text)
        mocked_import.assert_not_called()
        detail_response = self.client.get(
            f"/api/checkins/{response.json()['checkin_id']}",
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(200, detail_response.status_code)
        self.assertEqual("codeforces", detail_response.json()["oj_source"])

    def test_retry_only_allowed_when_failed(self):
        checkin_id = self._create_checkin(self.owner_id, "retry-checkin")
        create_pending_review(checkin_id, self.owner_id)

        pending_response = self.client.post(
            f"/api/checkins/{checkin_id}/review/retry",
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(400, pending_response.status_code)

        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=[],
            diagnosis="ok",
            next_action="ok",
            suggested_topic="ok",
        )
        response = self.client.post(
            f"/api/checkins/{checkin_id}/review/retry",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("无需重试", response.json()["detail"])

        mark_review_failed(checkin_id, "boom")
        with patch.object(api_server, "_start_review_generation_job", return_value=None) as mocked_retry:
            failed_response = self.client.post(
                f"/api/checkins/{checkin_id}/review/retry",
                headers=auth_headers(self.owner_id),
            )
        self.assertEqual(200, failed_response.status_code)
        self.assertEqual(REVIEW_STATUS_PENDING, failed_response.json()["review_status"])
        mocked_retry.assert_called_once()

    def test_create_review_persists_guided_review_fields(self):
        checkin_id = self._create_checkin(self.owner_id, "guided-review-fields")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            main_block="旧字段问题定位",
            key_bridge="先抓住两个休息点群之间的新边。",
            next_step="旧字段下一步",
            transfer_signal="看到两个连通块用新边连接后求最长距离。",
            problem_focus="你卡在新边连通后最长路候选从哪里来。",
            visual_hint="左边: A-B-C\n右边: D-E\n新边: C-D",
            guided_walkthrough="1. 先看左边休息点群原来的最长路。\n2. 再看右边休息点群原来的最长路。\n3. 如果路径经过新边，两端都接到各自离连接点最远的休息点。",
            try_now="如果最长路经过新边，左边那一端应该接到什么样的休息点？",
        )

        stored = get_review_by_checkin(checkin_id)
        self.assertEqual("你卡在新边连通后最长路候选从哪里来。", stored["problem_focus"])
        self.assertEqual("左边: A-B-C\n右边: D-E\n新边: C-D", stored["visual_hint"])
        self.assertIn("左边休息点群", stored["guided_walkthrough"])
        self.assertEqual("如果最长路经过新边，左边那一端应该接到什么样的休息点？", stored["try_now"])

        detail_response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(200, detail_response.status_code)
        payload = detail_response.json()
        self.assertEqual(stored["problem_focus"], payload["review"]["problem_focus"])
        self.assertEqual(stored["visual_hint"], payload["review"]["visual_hint"])
        self.assertEqual(stored["guided_walkthrough"], payload["review"]["guided_walkthrough"])
        self.assertEqual(stored["try_now"], payload["review"]["try_now"])

    def test_create_review_persists_bridge_route_meta_for_observability(self):
        checkin_id = self._create_checkin(self.owner_id, "bridge-route-meta")
        bridge_route_meta = {
            "status": "candidate_bridge",
            "stable_focus": "tree_path_difference",
            "card_id": "graph.tree_path_difference",
            "route_confidence": "medium",
            "matched_signals": ["树上路径", "边经过次数"],
            "conflict_signals": ["标记 also matches lazy_semantics"],
            "suppressed_candidates": ["lazy_semantics"],
            "candidate_bridge_id": "tree_path_difference.edge_variant",
            "candidate_parent_focus": "tree_path_difference",
            "candidate_confidence": "medium",
            "open_bridge_label": "树上边贡献差分",
            "open_bridge_reason": "当前题在问边经过次数。",
        }
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["树上差分"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            problem_focus="你卡在边贡献如何差分。",
            key_bridge="先把边贡献挂到稳定父桥下观察。",
            bridge_route_meta=bridge_route_meta,
        )

        stored = get_review_by_checkin(checkin_id)
        self.assertEqual(bridge_route_meta, stored["bridge_route_meta"])

        detail_response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(200, detail_response.status_code)
        self.assertEqual(bridge_route_meta, detail_response.json()["review"]["bridge_route_meta"])

    def test_generate_and_store_review_persists_generated_bridge_route_meta(self):
        checkin_id = self._create_checkin(self.owner_id, "generated-bridge-route-meta")
        fake_json = '''
        {
            "error_tags":["模型转化"],
            "error_layer":"core_design",
            "error_layer_confidence":"high",
            "core_design_subtags":["tree_path_difference"],
            "diagnosis":"你卡在把树上边经过次数转成少量标记。",
            "next_action":"回到当前题先说清一条路径怎么打标记。",
            "suggested_topic":"树上路径贡献标记",
            "problem_focus":"你卡在边经过次数不能沿路逐条加。",
            "main_block":"你卡在边经过次数不能沿路逐条加。",
            "key_bridge":"先把一条树上边路径的贡献变成端点和公共祖先附近的差分标记。",
            "visual_hint":"u 到 v 的路\\n-> 端点附近打标记\\n-> DFS 汇总边贡献",
            "guided_walkthrough":"1. 先找一条 u 到 v 的路线。\\n2. 再看它跨过哪些道路。\\n3. 最后想哪些点标记能让 DFS 还原道路贡献。",
            "try_now":"先说 u 到 v 这条路的公共祖先是谁。",
            "next_step":"先说 u 到 v 这条路的公共祖先是谁。",
            "transfer_signal":"看到很多树上路线都要统计经过次数，先想路径差分。"
        }
        '''

        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})):
            result = api_server._generate_and_store_review(
                checkin_id=checkin_id,
                student_id=self.owner_id,
                problem_title="树上边经过次数统计",
                oj_source="luogu",
                completion_status="unfinished",
                bottleneck_text="我总想沿路把每条边加一，但题解说要用 LCA 和树上差分。",
                error_types=["模型转化"],
                reflection="不知道边贡献怎么汇总。",
                problem_context="给一棵树和很多次 u 到 v 的运输，每次会经过一串道路，最后要统计哪条边被经过最多。",
            )

        self.assertTrue(result["ok"])
        stored = get_review_by_checkin(checkin_id)
        self.assertEqual("candidate_bridge", stored["bridge_route_meta"]["status"])
        self.assertEqual("tree_path_difference", stored["bridge_route_meta"]["stable_focus"])
        self.assertEqual("tree_path_difference.edge_variant", stored["bridge_route_meta"]["candidate_bridge_id"])

    def test_student_detail_hides_review_last_error(self):
        checkin_id = self._create_checkin(self.owner_id, "error-hidden")
        create_pending_review(checkin_id, self.owner_id)
        mark_review_pending(checkin_id, "private error")

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.json()["review_last_error"])

    def test_create_checkin_returns_pending_without_waiting(self):
        payload = {
            "problem_url": "https://example.com/new-problem",
            "problem_title": "新建打卡",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "每个活动都必须同时满足时间窗口和指定地点两个条件。",
            "submission_result": "wa",
            "bottleneck_text": "我总把时间条件和地点条件当成主次关系，不知道是不是要同时满足。",
            "error_types": ["模型转化"],
            "reflection": "这里应该是并列约束。",
            "problem_tags": [],
            "chat_context_summary": "",
            "student_code": "",
        }

        with patch.object(api_server, "_start_review_generation_job", return_value=None):
            response = self.client.post(
                "/api/checkins",
                json=payload,
                headers=auth_headers(self.owner_id),
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual(REVIEW_STATUS_PENDING, response.json()["review_status"])
        self.assertTrue(response.json()["session_id"].startswith("checkin_"))
        self.assertEqual("failed_verdict", response.json()["review_mode"])
        self.assertEqual("failure_diagnosis", response.json()["review_family"])

    def test_checkin_stream_refreshes_status_after_review_completes(self):
        checkin_id = self._create_checkin(self.owner_id, "stream-refresh")
        create_pending_review(checkin_id, self.owner_id)
        api_server.update_checkin_runtime_status(
            checkin_id,
            "queued",
            REVIEW_STATUS_PENDING,
            "已进入生成队列",
        )

        sleep_calls = {"count": 0}

        def fake_sleep(_seconds):
            sleep_calls["count"] += 1
            if sleep_calls["count"] == 1:
                api_server.clear_checkin_runtime_status(checkin_id)
                create_review(
                    checkin_id=checkin_id,
                    student_id=self.owner_id,
                    error_tags=["模型转化"],
                    diagnosis="诊断",
                    next_action="行动",
                    suggested_topic="专题",
                    problem_focus="你卡在对象关系没有站稳。",
                    key_bridge="先抓住当前题里谁限制谁。",
                    guided_walkthrough="1. 先圈出题目里的两个对象。\n2. 再判断谁对谁产生限制。",
                    try_now="先回答：到底是谁限制谁？",
                    transfer_signal="看到两个对象之间有方向性约束时，先判断谁限制谁。",
                )
                return
            raise AssertionError("stream did not stop after review completed")

        with patch.object(api_server.time, "sleep", side_effect=fake_sleep):
            response = self.client.get(
                f"/api/checkins/{checkin_id}/stream",
                headers=auth_headers(self.owner_id),
            )

        self.assertEqual(200, response.status_code)
        self.assertIn("event: review_ready", response.text)
        self.assertIn('"review_status":"completed"', response.text)

    def test_student_detail_returns_review_mode_and_family(self):
        checkin_id = self._create_checkin(self.owner_id, "mode-visible")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["session_id"].startswith("checkin_"))
        self.assertEqual("failed_verdict", response.json()["review_mode"])
        self.assertEqual("failure_diagnosis", response.json()["review_family"])

    def test_student_detail_returns_submitted_checkin_content_fields(self):
        checkin_id = self._create_checkin(self.owner_id, "detail-fields")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIn("completion_status", payload)
        self.assertIn("bottleneck_text", payload)
        self.assertIn("reflection", payload)
        self.assertIn("problem_context", payload)
        self.assertIn("error_types", payload)
        self.assertIn("student_code", payload)

    def test_student_detail_returns_quiz_history_in_round_order(self):
        checkin_id = self._create_checkin(self.owner_id, "quiz-history-visible")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            problem_focus="你卡在为什么 trie 查询不需要重看所有消息。",
            key_bridge="公共前缀被提前合并后，查询时只沿当前前缀往下走。",
            guided_walkthrough="1. 先看公共前缀。\\n2. 再看查询过程。",
            try_now="查询时会不会重看所有消息？",
            transfer_signal="看到很多字符串反复做前缀匹配时，先想公共前缀能不能合并。",
        )
        review = get_review_by_checkin(checkin_id)
        main_quiz_id = create_review_quiz(
            review_id=review["id"],
            student_id=self.owner_id,
            checkin_id=checkin_id,
            round=1,
            quiz_role="main",
            quiz_type="choice",
            question_text="第一轮：为什么暴力不行？",
            options=["A", "B"],
            correct_answer="A",
            explanation="先看规模。",
            bridge_feedback="先用规模判断方法。",
            distractor_feedback={},
            target_bridge="先判断逐条比对是不是在重复重看很多条消息。",
            source_error_layer="method",
            meta={"difficulty_level": "main"},
        )
        record_quiz_attempt(main_quiz_id, self.owner_id, "B", False, "先别急着下结论。")
        followup_quiz_id = create_review_quiz(
            review_id=review["id"],
            student_id=self.owner_id,
            checkin_id=checkin_id,
            round=2,
            quiz_role="followup",
            quiz_type="choice",
            question_text="第二轮：查一条串时会不会重看所有消息？",
            options=["会", "不会，会只沿当前前缀往下走"],
            correct_answer="不会，会只沿当前前缀往下走",
            explanation="先盯查询过程这半步。",
            bridge_feedback="你真正要站稳的是“查询时不重看所有消息”。",
            distractor_feedback={},
            target_bridge="查询时不重看所有消息，只沿当前前缀往下走。",
            source_error_layer="method",
            meta={"difficulty_level": "followup"},
        )
        record_quiz_attempt(
            followup_quiz_id,
            self.owner_id,
            "不会，会只沿当前前缀往下走",
            True,
            "对，这一步已经缩到当前查询过程了。",
        )

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIn("quiz_history", payload)
        self.assertEqual(
            ["main", "followup"],
            [quiz["quiz_role"] for quiz in payload["quiz_history"]],
        )
        self.assertEqual(
            ["第一轮：为什么暴力不行？", "第二轮：查一条串时会不会重看所有消息？"],
            [quiz["question_text"] for quiz in payload["quiz_history"]],
        )
        self.assertEqual(
            [False, True],
            [quiz["latest_is_correct"] for quiz in payload["quiz_history"]],
        )

    def test_student_checkin_list_returns_review_mode_and_family(self):
        checkin_id = self._create_checkin(self.owner_id, "list-mode-visible")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            "/api/checkins/me",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        item = next(row for row in response.json()["checkins"] if row["id"] == checkin_id)
        self.assertTrue(item["session_id"].startswith("checkin_"))
        self.assertEqual("failed_verdict", item["review_mode"])
        self.assertEqual("failure_diagnosis", item["review_family"])

    def test_review_event_endpoint_records_review_feedback(self):
        checkin_id = self._create_checkin(self.owner_id, "event-checkin")
        create_pending_review(checkin_id, self.owner_id)

        detail_response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )
        session_id = detail_response.json()["session_id"]

        response = self.client.post(
            "/api/review-events",
            json={
                "checkin_id": checkin_id,
                "session_id": session_id,
                "event_name": "review_feedback_submitted",
                "student_feedback": "confused",
                "bad_reason": "no_next_step",
                "followup_clicked": True,
                "followup_question_count": 1,
            },
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])
        events = get_review_events_for_checkin(checkin_id)
        self.assertEqual(1, len(events))
        self.assertEqual("review_feedback_submitted", events[0]["event_name"])
        self.assertEqual(session_id, events[0]["session_id"])
        self.assertEqual("failed_verdict", events[0]["review_mode"])
        self.assertEqual("failure_diagnosis", events[0]["review_family"])

    def test_review_event_endpoint_records_review_request_submitted(self):
        payload = {
            "problem_url": "https://example.com/request-problem",
            "problem_title": "请求事件打卡",
            "oj_source": "other",
            "completion_status": "independent",
            "problem_context": "有 n 件纪念品，每组最多放两件且总重量不能超过 w，要求分组数最少。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我会排序后双指针，但说不清为什么最重的尽量和最轻的一组不会吃亏。",
            "error_types": ["知道算法但不知道怎么用"],
            "reflection": "应该是贪心，但我不会解释。",
            "problem_tags": [],
            "chat_context_summary": "",
            "student_code": "",
        }

        with patch.object(api_server, "_start_review_generation_job", return_value=None):
            create_response = self.client.post(
                "/api/checkins",
                json=payload,
                headers=auth_headers(self.owner_id),
            )

        body = create_response.json()
        response = self.client.post(
            "/api/review-events",
            json={
                "checkin_id": body["checkin_id"],
                "session_id": body["session_id"],
                "event_name": "review_request_submitted",
                "problem_id": "P1094",
                "problem_title": "P1094 [NOIP2007 普及组] 纪念品分组",
                "has_code": False,
                "problem_context_length": len(payload["problem_context"]),
                "bottleneck_text_length": len(payload["bottleneck_text"]),
                "latency_ms": 0,
            },
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        events = get_review_events_for_checkin(body["checkin_id"])
        self.assertEqual("review_request_submitted", events[-1]["event_name"])
        self.assertEqual("independent_reflect", events[-1]["review_mode"])
        self.assertEqual("success_reflection", events[-1]["review_family"])
        self.assertEqual("P1094", events[-1]["payload"]["problem_id"])
        self.assertEqual(False, events[-1]["payload"]["has_code"])

    def test_remedy_resolve_returns_final_micro_confirm_quiz(self):
        checkin_id = self._create_checkin(self.owner_id, "final-micro-confirm")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            error_layer="core_design",
            main_block="你卡在把约束统一成同一种关系。",
            key_bridge="先把每条不等式关系改写成统一方向的边。",
            next_step="先把每条不等式改成同向边。",
            transfer_signal="当题目要求多条不等式同时成立时，要先统一关系方向。",
        )
        review_id = get_review_by_checkin(checkin_id)["id"]

        fake_json = '{"remedy_text":"先把不等式方向统一。","micro_action":"先说一条不等式该画成哪种方向的边。"}'
        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})):
            remedy_response = self.client.post(
                f"/api/reviews/{review_id}/remedy",
                json={"action_type": "dynamic_bridge_help"},
                headers=auth_headers(self.owner_id),
            )
        self.assertEqual(200, remedy_response.status_code)
        self.assertEqual("explain", remedy_response.json()["mode"])

        resolve_response = self.client.post(
            f"/api/reviews/{review_id}/remedy/resolve",
            json={"status": "resolved"},
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, resolve_response.status_code)
        self.assertEqual("quiz_in_progress", resolve_response.json()["learning_status"])
        self.assertEqual("final_micro_confirm", resolve_response.json()["next_state"])
        self.assertEqual("remedy", resolve_response.json()["quiz"]["quiz_role"])
        self.assertEqual(3, resolve_response.json()["quiz"]["round"])

    def test_second_remedy_explanation_returns_bottom_out_visual_hint(self):
        checkin_id = self._create_checkin(self.owner_id, "bottom-out-visual-hint")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            error_layer="core_design",
            main_block="你卡在新最长路候选从哪里来。",
            key_bridge="先比较左边内部、右边内部、经过新边三种候选。",
            next_step="先判断经过新边时两端该接什么点。",
            transfer_signal="当题目把两个连通块用新边连起来，还要求最长距离时，要先比较候选来源。",
        )
        review = get_review_by_checkin(checkin_id)
        review_id = review["id"]
        update_review_learning_status(review_id, "remedy_in_progress", remedy_count=1)

        fake_json = '{"remedy_text":"先把这题缩成左右两边各一条短链。","visual_hint":"左边: A-B-C\\n右边: D-E\\n新边: C-D","micro_action":"现在只回答：左边这一端该接什么点？"}'
        with patch.object(review_engine, "_call_llm", return_value=(True, fake_json, {})):
            response = self.client.post(
                f"/api/reviews/{review_id}/remedy",
                json={"action_type": "dynamic_bridge_help"},
                headers=auth_headers(self.owner_id),
            )

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("explain", body["mode"])
        self.assertEqual("左边: A-B-C\n右边: D-E\n新边: C-D", body["visual_hint"])
        self.assertEqual(2, body["remedy_count"])

    def test_final_micro_confirm_failure_enters_knowledge_bailout(self):
        checkin_id = self._create_checkin(self.owner_id, "knowledge-bailout")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            error_layer="core_design",
            main_block="你卡在 dp[x][y] 这一格到底记录什么。",
            key_bridge="先把 dp[x][y] 这一格的状态含义站稳。",
            next_step="先说清 dp[x][y] 表示什么。",
            transfer_signal="如果题目让你在每个格子上记一个结果，就要先想清这格到底表示什么。",
            visual_hint="dp[x][y] 不是最终答案位置。",
            guided_walkthrough="先只盯这一格，再想它要存什么。",
            try_now="dp[x][y] 更像在存什么？",
        )
        review_id = get_review_by_checkin(checkin_id)["id"]
        quiz_id = create_review_quiz(
            review_id=review_id,
            student_id=self.owner_id,
            checkin_id=checkin_id,
            round=3,
            quiz_role=review_engine.QUIZ_ROLE_REMEDY,
            quiz_type="choice",
            question_text="如果只看 dp[x][y] 这一格，它是不是在记录这个状态本身对应的子问题结果？",
            options=[{"value": "A", "label": "是"}, {"value": "B", "label": "不是"}],
            correct_answer="A",
            explanation="最后只确认这一格在记什么。",
            bridge_feedback="先把状态格的含义站稳。",
            distractor_feedback={"B": "这格先存的是状态本身的结果。"},
            target_bridge="先把 dp[x][y] 这一格的状态含义站稳。",
            source_error_layer="core_design",
            meta={"difficulty_level": "final_micro_confirm", "confirm_stage": "final_micro_confirm", "focus": "state_design"},
        )

        response = self.client.post(
            f"/api/quizzes/{quiz_id}/answer",
            json={"answer_text": "B"},
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("knowledge_bailout", body["next_state"])
        self.assertEqual("knowledge_bailout", body["learning_status"])
        self.assertIn("knowledge_card", body)
        self.assertEqual("knowledge_confirm", body["quiz"]["meta"]["difficulty_level"])

    def test_knowledge_confirm_can_resolve_or_end_with_teacher_followup(self):
        checkin_id = self._create_checkin(self.owner_id, "knowledge-confirm")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            error_layer="method",
            main_block="你卡在为什么 trie 不用重看所有消息。",
            key_bridge="先说清 trie 查询时只沿当前前缀往下走。",
            next_step="先比较重看所有消息和沿前缀路径查询的区别。",
            transfer_signal="如果很多字符串共享开头，还要反复做前缀匹配，就要警惕 trie。",
        )
        review_id = get_review_by_checkin(checkin_id)["id"]
        quiz_id = create_review_quiz(
            review_id=review_id,
            student_id=self.owner_id,
            checkin_id=checkin_id,
            round=4,
            quiz_role="knowledge_confirm",
            quiz_type="choice",
            question_text="如果把很多消息先放进 trie，查询一条拦截串时，是重新看所有消息，还是只沿当前前缀往下走？",
            options=[{"value": "A", "label": "只沿当前前缀往下走"}, {"value": "B", "label": "重看所有消息"}],
            correct_answer="A",
            explanation="知识卡后的最后确认。",
            bridge_feedback="站稳 trie 的查询过程。",
            distractor_feedback={"B": "trie 省掉的就是重看所有消息。"},
            target_bridge="trie 查询时只沿当前前缀往下走。",
            source_error_layer="method",
            meta={"difficulty_level": "knowledge_confirm", "knowledge_bailout": True, "knowledge_card_id": "string.trie.shared_prefix_merging"},
        )

        ok_response = self.client.post(
            f"/api/quizzes/{quiz_id}/answer",
            json={"answer_text": "A"},
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(200, ok_response.status_code)
        self.assertEqual("resolved", ok_response.json()["next_state"])

        detail = self.client.get(f"/api/checkins/{checkin_id}", headers=auth_headers(self.owner_id))
        self.assertEqual(200, detail.status_code)
        self.assertEqual("assisted_success", detail.json()["review"]["mastery_status"])
        self.assertEqual("knowledge_bailout_success", detail.json()["review"]["bridge_path"])

        checkin_id_2 = self._create_checkin(self.owner_id, "knowledge-confirm-fail")
        create_review(
            checkin_id=checkin_id_2,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )
        review_id_2 = get_review_by_checkin(checkin_id_2)["id"]
        quiz_id_2 = create_review_quiz(
            review_id=review_id_2,
            student_id=self.owner_id,
            checkin_id=checkin_id_2,
            round=4,
            quiz_role="knowledge_confirm",
            quiz_type="choice",
            question_text="知识卡确认题",
            options=[{"value": "A", "label": "对"}, {"value": "B", "label": "错"}],
            correct_answer="A",
            explanation="知识卡后的最后确认。",
            bridge_feedback="最后确认。",
            distractor_feedback={"B": "还没站稳。"},
            target_bridge="最后确认。",
            source_error_layer="core_design",
            meta={"difficulty_level": "knowledge_confirm", "knowledge_bailout": True, "knowledge_card_id": "dp.state_design"},
        )

        fail_response = self.client.post(
            f"/api/quizzes/{quiz_id_2}/answer",
            json={"answer_text": "B"},
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(200, fail_response.status_code)
        self.assertEqual("needs_teacher_followup", fail_response.json()["next_state"])
        self.assertEqual(LEARNING_STATUS_NEEDS_TEACHER, fail_response.json()["learning_status"])

    def test_teacher_can_list_manual_review_samples(self):
        checkin_id = self._create_checkin(self.owner_id, "manual-sample")
        bridge_route_meta = {
            "status": "candidate_bridge",
            "stable_focus": "tree_path_difference",
            "candidate_bridge_id": "tree_path_difference.edge_variant",
            "route_confidence": "medium",
            "matched_signals": ["树上路径", "边经过次数"],
        }
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            bridge_route_meta=bridge_route_meta,
        )
        review_id = get_review_by_checkin(checkin_id)["id"]
        update_review_learning_status(review_id, LEARNING_STATUS_RESOLVED)
        update_review_bridge_path(review_id, "followup_correct")
        update_review_mastery_status(review_id, "assisted_success")

        response = self.client.get(
            "/api/teacher/review-samples?limit=50",
            headers=teacher_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["samples"])
        sample = next(item for item in response.json()["samples"] if item["checkin_id"] == checkin_id)
        self.assertEqual("failed_verdict", sample["review_mode"])
        self.assertEqual("failure_diagnosis", sample["review_family"])
        self.assertEqual("assisted_success", sample["mastery_status"])
        self.assertEqual(bridge_route_meta, sample["bridge_route_meta"])
        self.assertIsNone(sample["manual_review"])

    def test_teacher_stats_include_bridge_route_observability_distribution(self):
        baseline_response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers())
        self.assertEqual(200, baseline_response.status_code)
        baseline_route_stats = baseline_response.json().get("bridge_route_stats", {})

        known_checkin = self._create_checkin(self.owner_id, "route-known")
        candidate_checkin = self._create_checkin(self.owner_id, "route-candidate")
        open_checkin = self._create_checkin(self.owner_id, "route-open")

        create_review(
            checkin_id=known_checkin,
            student_id=self.owner_id,
            error_tags=["树上差分"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="graph.tree_path_difference",
            bridge_route_meta={
                "status": "known_bridge",
                "stable_focus": "tree_path_difference",
                "route_confidence": "high",
                "matched_signals": ["树上路径"],
            },
        )
        create_review(
            checkin_id=candidate_checkin,
            student_id=self.owner_id,
            error_tags=["树上差分"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="graph.tree_path_difference",
            bridge_route_meta={
                "status": "candidate_bridge",
                "stable_focus": "tree_path_difference",
                "candidate_bridge_id": "tree_path_difference.edge_variant",
                "candidate_parent_focus": "tree_path_difference",
                "route_confidence": "medium",
                "matched_signals": ["边经过次数"],
                "conflict_signals": ["标记 also matches lazy_semantics"],
            },
        )
        create_review(
            checkin_id=open_checkin,
            student_id=self.owner_id,
            error_tags=["方法选择"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="method_selection",
            bridge_route_meta={
                "status": "open_bridge",
                "stable_focus": "method_selection",
                "candidate_bridge_id": "kmp_failure_link",
                "candidate_parent_focus": "method_selection",
                "route_confidence": "medium",
                "open_bridge_label": "KMP 失配跳转 / failure link",
                "matched_signals": ["KMP"],
            },
        )

        response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers())

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertIn("bridge_route_stats", body)
        route_stats = body["bridge_route_stats"]
        baseline_status = baseline_route_stats.get("status", {})
        baseline_stable_focus = baseline_route_stats.get("stable_focus", {})
        baseline_candidate = baseline_route_stats.get("candidate_bridge", {})
        baseline_open = baseline_route_stats.get("open_bridge", {})
        baseline_conflict = baseline_route_stats.get("conflict_signals", {})
        self.assertGreaterEqual(
            route_stats["status"]["known_bridge"]["count"],
            int(baseline_status.get("known_bridge", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            route_stats["status"]["candidate_bridge"]["count"],
            int(baseline_status.get("candidate_bridge", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            route_stats["status"]["open_bridge"]["count"],
            int(baseline_status.get("open_bridge", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            route_stats["stable_focus"]["tree_path_difference"]["count"],
            int(baseline_stable_focus.get("tree_path_difference", {}).get("count", 0)) + 2,
        )
        self.assertGreaterEqual(
            route_stats["candidate_bridge"]["tree_path_difference.edge_variant"]["count"],
            int(baseline_candidate.get("tree_path_difference.edge_variant", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            route_stats["open_bridge"]["kmp_failure_link"]["count"],
            int(baseline_open.get("kmp_failure_link", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            route_stats["conflict_signals"]["标记 also matches lazy_semantics"]["count"],
            int(baseline_conflict.get("标记 also matches lazy_semantics", {}).get("count", 0)) + 1,
        )

    def test_teacher_stats_include_bridge_promotion_suggestions_without_auto_promoting(self):
        suffix = int(time.time() * 1000)
        candidate_id = f"tree_path_difference.edge_variant.p2_{suffix}"
        open_id = f"kmp_failure_link.p2_{suffix}"

        for index in range(2):
            checkin_id = self._create_checkin(self.owner_id, f"candidate-suggestion-{index}-{suffix}")
            create_review(
                checkin_id=checkin_id,
                student_id=self.owner_id,
                error_tags=["树上差分"],
                diagnosis="诊断",
                next_action="行动",
                suggested_topic="专题",
                key_bridge="graph.tree_path_difference",
                bridge_route_meta={
                    "status": "candidate_bridge",
                    "stable_focus": "tree_path_difference",
                    "candidate_bridge_id": candidate_id,
                    "candidate_parent_focus": "tree_path_difference",
                    "route_confidence": "medium",
                    "matched_signals": ["边经过次数", "道路"],
                    "conflict_signals": ["标记 also matches lazy_semantics"],
                },
            )

        open_checkin = self._create_checkin(self.owner_id, f"open-suggestion-{suffix}")
        create_review(
            checkin_id=open_checkin,
            student_id=self.owner_id,
            error_tags=["方法选择"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="method_selection",
            bridge_route_meta={
                "status": "open_bridge",
                "stable_focus": "method_selection",
                "candidate_bridge_id": open_id,
                "candidate_parent_focus": "method_selection",
                "route_confidence": "medium",
                "open_bridge_label": "KMP 失配跳转 / failure link",
                "matched_signals": ["KMP", "失配"],
            },
        )

        response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers())

        self.assertEqual(200, response.status_code)
        suggestions = response.json().get("bridge_route_promotion_suggestions", [])
        candidate = next(item for item in suggestions if item["bridge_id"] == candidate_id)
        open_suggestion = next(item for item in suggestions if item["bridge_id"] == open_id)
        self.assertEqual("candidate_bridge", candidate["route_kind"])
        self.assertEqual("tree_path_difference", candidate["parent_focus"])
        self.assertEqual(2, candidate["count"])
        self.assertEqual("teacher_review_required", candidate["decision_policy"])
        self.assertFalse(candidate["auto_promote"])
        self.assertIn("边经过次数", candidate["evidence_signals"])
        self.assertEqual("draft_only", candidate["rule_draft"]["integration_status"])
        self.assertFalse(candidate["rule_draft"]["auto_apply"])
        self.assertIn(candidate_id.replace(".", "_"), candidate["rule_draft"]["filename"])
        self.assertIn("边经过次数", candidate["rule_draft"]["trigger_signals"])
        self.assertIn("教师确认", " ".join(candidate["rule_draft"]["acceptance_checks"]))
        self.assertEqual("open_bridge", open_suggestion["route_kind"])
        self.assertEqual("method_selection", open_suggestion["parent_focus"])
        self.assertEqual("teacher_review_required", open_suggestion["decision_policy"])
        self.assertFalse(open_suggestion["auto_promote"])
        self.assertEqual("draft_only", open_suggestion["rule_draft"]["integration_status"])
        self.assertFalse(open_suggestion["rule_draft"]["auto_apply"])

    def test_teacher_can_confirm_and_export_bridge_rule_draft_without_promoting(self):
        suffix = int(time.time() * 1000)
        candidate_id = f"tree_path_difference.edge_variant.p4_{suffix}"
        checkin_id = self._create_checkin(self.owner_id, f"candidate-confirm-{suffix}")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["树上差分"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="graph.tree_path_difference",
            bridge_route_meta={
                "status": "candidate_bridge",
                "stable_focus": "tree_path_difference",
                "candidate_bridge_id": candidate_id,
                "candidate_parent_focus": "tree_path_difference",
                "route_confidence": "medium",
                "matched_signals": ["边经过次数", "道路"],
                "conflict_signals": ["标记 also matches lazy_semantics"],
            },
        )

        export_response = self.client.get(
            "/api/teacher/bridge-rule-drafts/export",
            params={"route_kind": "candidate_bridge", "bridge_id": candidate_id, "days": 30},
            headers=teacher_headers("teacher_rule_draft"),
        )

        self.assertEqual(200, export_response.status_code)
        self.assertIn("text/markdown", export_response.headers.get("content-type", ""))
        self.assertIn("integration_status: draft_only", export_response.text)
        self.assertIn("auto_apply: false", export_response.text)
        self.assertIn("边经过次数", export_response.text)

        response = self.client.post(
            "/api/teacher/bridge-rule-drafts/decision",
            json={
                "route_kind": "candidate_bridge",
                "bridge_id": candidate_id,
                "decision": "confirmed",
                "notes": "同意进入人工规则草案池，但不要自动转正。",
                "days": 30,
            },
            headers=teacher_headers("teacher_rule_draft"),
        )

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("ok", body["status"])
        self.assertEqual("confirmed", body["decision"]["decision"])
        self.assertFalse(body["decision"]["auto_promote"])
        stored = get_bridge_rule_draft_decision(
            route_kind="candidate_bridge",
            bridge_id=candidate_id,
            teacher_id="teacher_rule_draft",
        )
        self.assertIsNotNone(stored)
        self.assertEqual("confirmed", stored["decision"])
        self.assertFalse(stored["auto_promote"])

        list_response = self.client.get(
            "/api/teacher/bridge-rule-drafts/decisions",
            headers=teacher_headers("teacher_rule_draft"),
        )
        self.assertEqual(200, list_response.status_code)
        decisions = list_response.json()["decisions"]
        listed = next(item for item in decisions if item["bridge_id"] == candidate_id)
        self.assertEqual("confirmed", listed["decision"])
        self.assertEqual("teacher_rule_draft", listed["teacher_id"])
        self.assertFalse(listed["auto_promote"])
        self.assertIn("bridge_rule_draft_", listed["draft_filename"])

        registry_response = self.client.post(
            "/api/teacher/bridge-registry/entries",
            json={"decision_id": listed["id"]},
            headers=teacher_headers("teacher_rule_draft"),
        )
        self.assertEqual(200, registry_response.status_code)
        entry = registry_response.json()["entry"]
        self.assertEqual(candidate_id, entry["bridge_id"])
        self.assertEqual("registry_only", entry["registry_status"])
        self.assertFalse(entry["resolver_enabled"])
        self.assertEqual(listed["id"], entry["draft_decision_id"])

        registry_list = self.client.get(
            "/api/teacher/bridge-registry/entries",
            headers=teacher_headers("teacher_rule_draft"),
        )
        self.assertEqual(200, registry_list.status_code)
        entries = registry_list.json()["entries"]
        listed_entry = next(item for item in entries if item["bridge_id"] == candidate_id)
        self.assertEqual("registry_only", listed_entry["registry_status"])
        self.assertFalse(listed_entry["resolver_enabled"])

        patch_response = self.client.get(
            f"/api/teacher/bridge-registry/entries/{listed_entry['id']}/resolver-patch-draft",
            headers=teacher_headers("teacher_rule_draft"),
        )
        self.assertEqual(200, patch_response.status_code)
        patch_draft = patch_response.json()["patch_draft"]
        self.assertEqual(candidate_id, patch_draft["bridge_id"])
        self.assertEqual("review_engine.py", patch_draft["target_file"])
        self.assertEqual("patch_draft_only", patch_draft["patch_status"])
        self.assertFalse(patch_draft["auto_apply"])
        self.assertFalse(patch_draft["resolver_enabled"])
        self.assertIn("_resolve_bridge_decision", patch_draft["draft_markdown"])
        self.assertIn("manual patch only", patch_draft["draft_markdown"])

    def test_teacher_can_submit_manual_review(self):
        checkin_id = self._create_checkin(self.owner_id, "manual-submit")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )

        samples_response = self.client.get(
            "/api/teacher/review-samples?limit=50",
            headers=teacher_headers(),
        )
        review_id = next(item for item in samples_response.json()["samples"] if item["checkin_id"] == checkin_id)["review_id"]

        response = self.client.post(
            f"/api/teacher/reviews/{review_id}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "yes",
                "notes": "这条可以作为正样本保留",
            },
            headers=teacher_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])

        manual_review = get_review_manual_review(review_id)
        self.assertIsNotNone(manual_review)
        self.assertEqual("correct", manual_review["mode_correct"])
        self.assertEqual("grounded", manual_review["review_grounded"])
        self.assertEqual("yes", manual_review["student_can_move_next"])

    def test_teacher_stats_include_manual_review_rates(self):
        teacher_id = f"teacher_stats_{int(time.time() * 1000)}"
        first_checkin = self._create_checkin(self.owner_id, "manual-stats-1")
        second_checkin = self._create_checkin(self.owner_id, "manual-stats-2")
        create_review(
            checkin_id=first_checkin,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )
        create_review(
            checkin_id=second_checkin,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )
        first_review = get_review_by_checkin(first_checkin)["id"]
        second_review = get_review_by_checkin(second_checkin)["id"]

        self.client.post(
            f"/api/teacher/reviews/{first_review}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "yes",
                "notes": "第一条合格",
            },
            headers=teacher_headers(teacher_id),
        )
        self.client.post(
            f"/api/teacher/reviews/{second_review}/manual-review",
            json={
                "mode_correct": "incorrect",
                "review_grounded": "mixed",
                "student_can_move_next": "no",
                "notes": "第二条需要回看",
            },
            headers=teacher_headers(teacher_id),
        )

        response = self.client.get(
            "/api/teacher/stats?days=30",
            headers=teacher_headers(teacher_id),
        )

        self.assertEqual(200, response.status_code)
        manual_stats = response.json()["manual_review_stats"]
        self.assertEqual(2, manual_stats["reviewed_count"])
        self.assertEqual(0.5, manual_stats["mode_correct_rate"])
        self.assertEqual(0.5, manual_stats["grounded_rate"])
        self.assertEqual(0.5, manual_stats["student_can_move_next_rate"])

    def test_teacher_stats_include_manual_review_breakdown_by_mode_and_family(self):
        teacher_id = f"teacher_breakdown_{int(time.time() * 1000)}"

        failed_checkin = create_checkin(
            student_id=self.owner_id,
            problem_url="https://example.com/failed",
            problem_title="失败题",
            oj_source="other",
            completion_status="unfinished",
            bottleneck_text="我知道是双指针，但窗口更新顺序总写乱。",
            error_types=["实现细节"],
            reflection="我怀疑 while 里的左右端点更新顺序错了。",
            problem_context="给定正整数 m，要求输出所有和等于 m 的连续正整数区间。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="wa",
            student_code="",
            session_id=f"failed_stats_{int(time.time() * 1000)}",
        )
        success_checkin = create_checkin(
            student_id=self.owner_id,
            problem_url="https://example.com/independent",
            problem_title="理解题",
            oj_source="other",
            completion_status="independent",
            bottleneck_text="我会 BFS 求最短步数，但说不清为什么第一次到达就是最短。",
            error_types=["知道算法但不知道怎么用"],
            reflection="应该跟层次扩展有关。",
            problem_context="在 n×m 的棋盘上，马从给定起点出发，要求输出到每个格子的最少步数。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="not_submitted",
            student_code="",
            session_id=f"success_stats_{int(time.time() * 1000)}",
        )
        editorial_checkin = create_checkin(
            student_id=self.owner_id,
            problem_url="https://example.com/editorial",
            problem_title="题解题",
            oj_source="other",
            completion_status="editorial",
            bottleneck_text="题解说这是树形 DP，但我不明白为什么状态只记子树里保留多少条边。",
            error_types=["模型转化"],
            reflection="看懂了代码，但状态定义还是不稳。",
            problem_context="给定一棵有边权的树，要求删去一些边后只保留 q 条边，使留下的苹果总数最大。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="not_submitted",
            student_code="",
            session_id=f"editorial_stats_{int(time.time() * 1000)}",
        )

        create_review(failed_checkin, self.owner_id, ["实现细节"], "诊断", "行动", "专题")
        create_review(success_checkin, self.owner_id, ["知道算法但不知道怎么用"], "诊断", "行动", "专题")
        create_review(editorial_checkin, self.owner_id, ["模型转化"], "诊断", "行动", "专题")

        failed_review = get_review_by_checkin(failed_checkin)["id"]
        success_review = get_review_by_checkin(success_checkin)["id"]
        editorial_review = get_review_by_checkin(editorial_checkin)["id"]

        self.client.post(
            f"/api/teacher/reviews/{failed_review}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "yes",
                "notes": "failed ok",
            },
            headers=teacher_headers(teacher_id),
        )
        self.client.post(
            f"/api/teacher/reviews/{success_review}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "unsure",
                "notes": "success ok",
            },
            headers=teacher_headers(teacher_id),
        )
        self.client.post(
            f"/api/teacher/reviews/{editorial_review}/manual-review",
            json={
                "mode_correct": "incorrect",
                "review_grounded": "mixed",
                "student_can_move_next": "no",
                "notes": "editorial needs work",
            },
            headers=teacher_headers(teacher_id),
        )

        response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers(teacher_id))

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertIn("manual_review_stats_by_mode", body)
        self.assertIn("manual_review_stats_by_family", body)
        self.assertEqual(1, body["manual_review_stats_by_mode"]["failed_verdict"]["reviewed_count"])
        self.assertEqual(1.0, body["manual_review_stats_by_mode"]["failed_verdict"]["mode_correct_rate"])
        self.assertEqual(1, body["manual_review_stats_by_mode"]["independent_reflect"]["reviewed_count"])
        self.assertEqual(1.0, body["manual_review_stats_by_mode"]["independent_reflect"]["grounded_rate"])
        self.assertEqual(2, body["manual_review_stats_by_family"]["failure_diagnosis"]["reviewed_count"])
        self.assertEqual(0.5, body["manual_review_stats_by_family"]["failure_diagnosis"]["mode_correct_rate"])
        self.assertEqual(0.5, body["manual_review_stats_by_family"]["failure_diagnosis"]["grounded_rate"])
        self.assertEqual(1, body["manual_review_stats_by_family"]["success_reflection"]["reviewed_count"])

    def test_teacher_stats_include_mastery_and_bridge_path_distribution(self):
        baseline_response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers())
        self.assertEqual(200, baseline_response.status_code)
        baseline_body = baseline_response.json()
        baseline_mastery = baseline_body.get("mastery_status_stats", {})
        baseline_bridge_paths = baseline_body.get("bridge_path_stats", {})
        baseline_bridges = baseline_body.get("bridge_stats", {})
        baseline_knowledge_bailout = baseline_body.get("knowledge_bailout_stats", {})
        baseline_topic_l1 = baseline_body.get("topic_l1_stats", {})
        baseline_topic_l2 = baseline_body.get("topic_l2_stats", {})

        first_checkin = self._create_checkin(self.owner_id, "mastery-stats-1")
        second_checkin = self._create_checkin(self.owner_id, "mastery-stats-2")
        third_checkin = self._create_checkin(self.owner_id, "mastery-stats-3")

        create_review(
            checkin_id=first_checkin,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="dp.state_design",
        )
        create_review(
            checkin_id=second_checkin,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="binary_search.check_condition",
        )
        create_review(
            checkin_id=third_checkin,
            student_id=self.owner_id,
            error_tags=["模型转化"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
            key_bridge="string.trie.shared_prefix_merging",
        )

        first_review = get_review_by_checkin(first_checkin)["id"]
        second_review = get_review_by_checkin(second_checkin)["id"]
        third_review = get_review_by_checkin(third_checkin)["id"]

        update_review_bridge_path(first_review, "main_clear")
        update_review_mastery_status(first_review, "independent_success")

        update_review_bridge_path(second_review, "followup_remedy")
        update_review_mastery_status(second_review, "assisted_success")

        update_review_bridge_path(third_review, "knowledge_bailout_failed")
        update_review_mastery_status(third_review, "not_mastered")

        response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers())

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertIn("mastery_status_stats", body)
        self.assertIn("bridge_path_stats", body)
        self.assertIn("bridge_stats", body)
        self.assertIn("knowledge_bailout_stats", body)
        self.assertIn("topic_l1_stats", body)
        self.assertIn("topic_l2_stats", body)
        self.assertGreaterEqual(
            body["mastery_status_stats"]["independent_success"]["count"],
            int(baseline_mastery.get("independent_success", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["mastery_status_stats"]["assisted_success"]["count"],
            int(baseline_mastery.get("assisted_success", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["mastery_status_stats"]["not_mastered"]["count"],
            int(baseline_mastery.get("not_mastered", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["bridge_path_stats"]["main_clear"]["count"],
            int(baseline_bridge_paths.get("main_clear", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["bridge_path_stats"]["followup_remedy"]["count"],
            int(baseline_bridge_paths.get("followup_remedy", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["bridge_path_stats"]["knowledge_bailout_failed"]["count"],
            int(baseline_bridge_paths.get("knowledge_bailout_failed", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["bridge_stats"]["dp.state_design"]["count"],
            int(baseline_bridges.get("dp.state_design", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["bridge_stats"]["binary_search.check_condition"]["count"],
            int(baseline_bridges.get("binary_search.check_condition", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["bridge_stats"]["string.trie.shared_prefix_merging"]["count"],
            int(baseline_bridges.get("string.trie.shared_prefix_merging", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["knowledge_bailout_stats"]["entered"]["count"],
            int(baseline_knowledge_bailout.get("entered", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["knowledge_bailout_stats"]["not_entered"]["count"],
            int(baseline_knowledge_bailout.get("not_entered", {}).get("count", 0)) + 2,
        )
        self.assertGreaterEqual(
            body["topic_l1_stats"]["dp"]["count"],
            int(baseline_topic_l1.get("dp", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["topic_l1_stats"]["basic"]["count"],
            int(baseline_topic_l1.get("basic", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["topic_l1_stats"]["string"]["count"],
            int(baseline_topic_l1.get("string", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["topic_l2_stats"]["dp_basic"]["count"],
            int(baseline_topic_l2.get("dp_basic", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["topic_l2_stats"]["binary_search"]["count"],
            int(baseline_topic_l2.get("binary_search", {}).get("count", 0)) + 1,
        )
        self.assertGreaterEqual(
            body["topic_l2_stats"]["trie"]["count"],
            int(baseline_topic_l2.get("trie", {}).get("count", 0)) + 1,
        )


if __name__ == "__main__":
    unittest.main()
