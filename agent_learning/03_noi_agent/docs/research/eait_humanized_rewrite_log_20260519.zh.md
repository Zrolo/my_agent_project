# EAIT Humanized Rewrite Log 20260519

## 输出文件

- `docs/research/paper_submission_manuscript_dialogue_state_v3_eait_v0_3_humanized.zh.md`
- `docs/research/eait_reference_integration_plan_20260519.zh.md`

## 洗稿原则

- 只做学术表达打磨，不做事实扩写。
- 减少模板化句式、机械边界句和重复的 “本文/This study” 起手。
- 保留必要的 evidence boundary，但改成更自然的论证节奏。
- 保留技术标签、condition 名称、slice 名称、metric 名称和所有数字。
- 不新增正文 citation，不把 recent corpus 的外部事实写入 Results。

## 主要语言改动

- Introduction 从定义式开头改为问题张力开头，减少“评测框架说明书”味道。
- Related Work 保留五小节结构，但弱化泛泛综述口吻，转为服务本文缺口的短段。
- Methods 中把若干解释性句子改成“为什么这样评”的自然说明。
- Results 保留全部数字和表格，但减少机械的 evidence-class 重复。
- Discussion 改为 implication-first，减少 checklist 式边界堆叠。
- Conclusion 改为 bounded close，减少“不能做什么”的密集排比，同时仍保留核心禁区。

## Claim Gate Check

- 是否新增实验 condition：no
- 是否修改线上 AIChat、active mode、prompt 或主实验数据：no
- 是否新增 manuscript citation：no
- 是否新增 empirical claim：no
- 是否修改实验数字：no
- 是否改变 evidence class：no
- 是否把 sensitivity / stress / calibration 写成 main result：no
- 是否把 Coach A、Coach B、priority60 adjudication 写成 final gold：no
- 是否把 all 50 cases aggregate 写成 headline：no
- 是否说 Bridge Contract 显著全面优于所有 baseline：no
- 是否说 Guard-only 修复最终输出：no
- 是否说 Repair 因果由主实验均值证明：no
- 是否说 LLM grader 可以替代人类教练：no
- 是否违反 final claim gate：no
