# Manuscript Human Revision Checklist

## 使用边界

投稿或外部公开前使用本清单。它是人类作者 checklist；AI 生成文本只有经过对应人工核验后，才可视为 submission-ready。

| Section | Human line edit done | AI meta-comments removed | Citations verified | Numbers reproduced | Forbidden wording avoided | Tone is restrained | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Abstract | no | no | n/a | no | no | no | 检查是否只写 framework / trade-off claim。 |
| Introduction | no | no | no | n/a | no | no | 核对 related-work 定位，避免系统胜利叙事。 |
| Related Work | no | no | no | n/a | no | no | 打开每篇 cited paper，核验 BibTeX。 |
| Task Definition | no | no | n/a | n/a | no | no | 精确定义 missing bridge 和 critical bridge leakage。 |
| Dataset / Protocol | no | no | n/a | no | no | no | 不把 50 cases 写成 universal 或 final gold。 |
| Baselines | no | no | no | n/a | no | no | DBox-inspired 不是 faithful DBox reproduction。 |
| Results | no | no | n/a | no | no | no | 主 headline 使用 `main_scaffold_eval`；all-50 只放 appendix。 |
| Repair Stress | no | no | n/a | no | no | no | 因果只引用 same-candidate stress；必须写 burden trade-off。 |
| LLM Grader Calibration | no | no | no | no | no | no | 只能写 auxiliary，不能替代 human coaches。 |
| Discussion | no | no | n/a | no | no | no | 限制要正面写，不藏在小字。 |
| Limitations | no | no | n/a | n/a | no | no | 包含 rater sensitivity、coverage、DBox+Repair、LLM grader 限制。 |
| Ethics / AI Use | no | no | n/a | n/a | no | no | 加入 AI writing disclosure 和 data governance statement。 |

## 必需人工动作

1. 只有人类作者完成逐节检查后，才能把 `no` 改成 `yes`。
2. 用 `citation_verification_log.csv` 核验引用。
3. 用 `result_number_verification_log.csv` 核验结果数字。
4. 投稿前运行 final claim gate scan。
