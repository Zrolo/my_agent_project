# Human Review Reliability Section Draft 20260517

## 论文小节草稿

Dialogue-state v3 的 response review 采用双教练盲评和高优先级裁决，而不是把单一评分者当作 gold。Coach A 与 Coach B 都完成了 50 cases × 7 conditions 的全量复评，共 350 条匿名回复。我们随后从 A/B 分歧中抽取 60 条高优先级样本进行裁决，优先覆盖 critical leakage disagreement、student-ready flip、would-show flip、overall delta >= 2、rank delta >= 4 和 headline comparison 相关行。

A/B agreement 显示，开放式教学质量判断具有明显评分者敏感性。`overall exact` 为 0.2829，但 `overall within 1` 为 0.8429，说明两位教练的整体质量判断多数差在 1 分以内。`leakage exact` 为 0.6714；`critical binary exact` 为 0.9029，但 `critical binary kappa` 只有 0.2511，说明 critical leakage 的二值一致率较高，但在低基率和不同严格程度下，校正后的一致性仍有限。`rank mean Spearman by case` 为 0.0264，top-1 / last-place agreement 均为 10/50，说明同题 7 条回复的偏好排序不稳定。共有 244 条 flagged disagreement rows。

Priority60 adjudication 的结果进一步说明不能把 Coach A 或 Coach B 任一方视为 gold。在 60 条裁决样本中，裁决结果为 `use_A=29`、`use_B=9`、`new_label=22`。其中 22 条需要 new_label，表明高分歧样本不是简单地由某一位教练更可靠解释，而是需要独立裁决口径重新判断。

因此本文将人工评分作为 expert reference，而不是绝对真值。主结果同时报告 Coach A only、Coach B only、priority60 adjudicated + Coach A 和 priority60 adjudicated + Coach B 四种口径，并按 `main_scaffold_eval`、`main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 分层报告。我们不把 priority60 adjudicated 合并表称为 final gold，也不只给出单一均值表。

## 方法解释

该分歧不应被写成项目失败。更准确的解释是：pedagogical judgment is inherently rater-sensitive。学生是否已经准备好继续、回复是否过度替学生完成关键桥、以及下一步负担是否过高，都依赖教练对学生状态和教学时机的判断。因此本项目使用 double review、priority adjudication、slice analysis 和 sensitivity reporting 来控制这种不可避免的主观性。

## 可写进论文的短版

```text
Human review was intentionally treated as rater-sensitive expert judgment rather than gold truth. Both coaches reviewed all 350 anonymized responses. Exact overall agreement was low, but most overall scores were within one point. Critical-leakage binary agreement was high in raw exact agreement but modest under kappa, and rank agreement was low. We therefore adjudicated 60 high-priority disagreement rows and report all main results under both original and adjudicated sensitivity views.
```

## 不应写

- Coach A 是 gold。
- Coach B 是 gold。
- priority60 裁决后的合并表是 final gold。
- A/B disagreement 说明评测无效。
- 只报告 `priority60 adjudicated + Coach A` 一个表，不报告 sensitivity。
