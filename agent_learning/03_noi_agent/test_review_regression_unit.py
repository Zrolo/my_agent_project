import unittest

import test_review_regression as regression


class ReviewRegressionGateTests(unittest.TestCase):
    def test_b1_structure_gate_accepts_parallel_constraints_with_action(self):
        review = {
            "main_block": "你现在不是没看到条件，而是没把时间和地点当成同一层要求。",
            "key_bridge": "这题里时间条件和地点条件是平级的，两个条件都要满足，少一个都不行。",
            "next_step": "先把时间条件和地点条件分别列出来，再拿一个活动逐项检查它是不是同时满足。",
            "transfer_signal": "以后看到合法安排，要先看是不是几个条件一起卡合法性。",
        }

        self.assertEqual(regression.evaluate_b1_structure_gate(review), [])

    def test_b1_structure_gate_accepts_boolean_expression_action(self):
        review = {
            "main_block": "你把两个条件看成了主次关系。",
            "key_bridge": "关键是时间窗口和指定地点都必须同时满足，它们是并列的与关系。",
            "next_step": "拿出草稿纸，把时间窗口和指定地点分别改写成两个布尔表达式，然后检查 check 函数是不是同时检验了这两个表达式。",
            "transfer_signal": "看到同时满足两个条件时，要先写出联合判定。",
        }

        self.assertEqual(regression.evaluate_b1_structure_gate(review), [])

    def test_b1_structure_gate_accepts_handwritten_sample_check_action(self):
        review = {
            "main_block": "你没有把两个条件平等对待。",
            "key_bridge": "时间条件和地点条件是并列的，两个都满足才合法。",
            "next_step": "先手写10个活动样本，对每个样本标注时间OK、地点OK、两者都OK，再对照代码检查哪里漏了并列判断。",
            "transfer_signal": "看到同时满足两个条件时，要先检查是不是联合判定。",
        }

        self.assertEqual(regression.evaluate_b1_structure_gate(review), [])

    def test_b1_structure_gate_rejects_sequential_structure_even_if_keywords_hit(self):
        review = {
            "main_block": "你知道这题有两个条件。",
            "key_bridge": "时间条件和地点条件都要看，但先把时间条件排除掉不满足的，再去看地点。",
            "next_step": "先筛时间，再补地点。",
            "transfer_signal": "以后遇到两个条件都要判断。",
        }

        failures = regression.evaluate_b1_structure_gate(review)
        self.assertTrue(failures)
        self.assertTrue(any("顺序结构" in item or "先满足 A，再检查 B" in item for item in failures))

    def test_b1_structure_gate_allows_negated_sequential_phrase(self):
        review = {
            "main_block": "你不是不会设计状态，而是没有先把时间和地点这两个限制翻译成必须同时满足。",
            "key_bridge": "这道题的关键桥在于把时间窗口和指定地点看作两个独立的必要条件，即两个约束是并列的与关系，而非先时间后主从检查。",
            "next_step": "拿纸笔把时间满足和地点满足画成两个必须都打的勾，列出合格情况。",
            "transfer_signal": "下次看到同时满足下列所有条件时，要先确认各约束之间是逻辑与的并列关系。",
        }

        self.assertEqual(regression.evaluate_b1_structure_gate(review), [])

    def test_b1_structure_gate_allows_sequential_phrase_when_used_as_wrong_example(self):
        review = {
            "main_block": "你把时间和地点看成了先满足时间再顺便看看地点的层级关系，但实际上两个条件必须同时满足。",
            "key_bridge": "关键是把时间窗口约束和地点约束看成并列的与关系，而不是主次条件。",
            "next_step": "拿出纸笔，把活动合法改写成时间和地点都满足的条件式，然后检查代码是不是逻辑与。",
            "transfer_signal": "看到同时满足X和Y时，要先判断是不是并列硬约束。",
        }

        self.assertEqual(regression.evaluate_b1_structure_gate(review), [])

    def test_d1_structure_gate_accepts_scale_first_human_readable_output(self):
        review = {
            "main_block": "你不是不会方法，而是没先看题目给的规模。",
            "key_bridge": "先看 n<=20 这个范围，2^20 大约一百万，所以这里可以直接枚举子集，不用先上 DP。",
            "next_step": "先确认 n 的范围，再算一下 2^20，最后写出你要枚举的是哪些子集。",
            "transfer_signal": "以后见到规模很小的最优值题，先算规模能不能直接枚举。",
        }

        self.assertEqual(regression.evaluate_d1_structure_gate(review), [])

    def test_d1_structure_gate_rejects_scale_keyword_that_slides_back_to_dp(self):
        review = {
            "main_block": "你要看规模。",
            "key_bridge": "先估一下规模，如果太大就用 DP。",
            "next_step": "先估规模，再考虑 DP。",
            "transfer_signal": "以后先看规模。",
        }

        failures = regression.evaluate_d1_structure_gate(review)
        self.assertTrue(failures)
        self.assertTrue(any("先上 DP" in item or "泛方法建议" in item or "规模判断" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
