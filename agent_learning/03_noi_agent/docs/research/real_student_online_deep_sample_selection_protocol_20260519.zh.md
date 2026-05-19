# Real-Student Online Deep Sample Selection Protocol 20260519

## 使用边界

本协议说明如何从 137 条 real-student online AIChat substantial candidate turns 中选择 30 条 pilot candidate cases，用于后续 deep pilot annotation。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 137 或 30 写成 learning outcome study。

137 条 candidate turns 是 lightweight screening pool，不是深度标注样本。30 条 selected cases 是 selected pilot candidate cases pending consent/reporting gate，不是全部线上 AIChat 数据。它们只用于后续 taxonomy / rubric ecological validity check；在 consent/status gate 完成前，不能写成可公开报告的 deep-pilot evidence，也不能作为 main result。

## 输入与输出

输入：

- Layer 1 online log corpus summary: 1156 AIChat message rows, 87 sessions, 578 paired user-assistant turns。
- Layer 2 candidate-turn screening pool: 137 substantial candidate turns, 59 candidate sessions。
- Candidate screening schema: `real_student_online_candidate_screening_schema_v1.json`。

输出：

- 30 条 selected pilot case annotation candidates。
- 每条 case 使用 `real_student_online_case_schema_v1.json` 做完整 case-specific rubric annotation。
- 每条 selected candidate case 在 screening form 中必须填写非空 `candidate_selection_reason`，说明它被选入后续 deep annotation 候选集的覆盖性或可标注性理由。
- 每条 case 必须通过 privacy review 和 consent/status 检查后才能进入正式 reporting。

## 筛选原则

### 1. 覆盖 Bridge Families

优先让 30 条 selected pilot candidate cases 覆盖多个 rough bridge families，包括但不限于：

- state / representation；
- transition / recurrence；
- predicate / check；
- boundary / ordering；
- modeling relation；
- aggregation / contribution；
- data-structure operation；
- correctness / invariant；
- implementation boundary；
- debugging evidence；
- policy / direct-answer handling。

如果某些 family 在 137 条中自然缺失，不强行补造案例。

### 2. 覆盖 Surface Anchors

选择时关注真实线上问题中的表面场景多样性，例如：

- DP state / recurrence；
- binary-search check；
- tree / graph marking or traversal；
- data-structure operation；
- local code implementation；
- debugging trace；
- sample-output mismatch；
- direct-answer or direct-code request；
- insufficient-context help seeking。

Surface anchor 只用于覆盖真实问题形态，不等同于 taxonomy 本体。

### 3. 覆盖 Context Sufficiency

30 条 selected pilot candidate cases 不应只选上下文最完整的 case。建议覆盖：

- `sufficient`：能完整标注 missing bridge 和 forbidden content；
- `partial`：能大致标注，但需要谨慎；
- `insufficient`：更适合检查 clarification safety；
- `unclear`：仅少量保留，用于说明真实线上对话的不确定性。

上下文不足的 case 不应强行写成 ordinary scaffold case。

### 4. 覆盖 Debugging / Implementation / Policy Risks

selected pilot candidate cases 应包含真实线上 AIChat 中常见的高风险帮助场景：

- debugging request：学生贴错误、样例不对、运行结果异常；
- implementation request：学生知道大方向但卡在局部代码边界；
- policy risk：学生直接要答案、完整代码或可提交方案；
- conceptual hint request：学生请求思路但尚未完成关键桥。

这些风险类别用于生态效度覆盖，不用于新增主实验 condition。

### 5. 覆盖不同 Students / Problems

选择时尽量避免 30 条都来自同一学生、同一题或同一 session。报告中只使用 hashed students / hashed problems，不公开真实身份或原始账号。

当前 deep candidate extraction 覆盖 11 个 hashed students 和 15 个 hashed problems；正式 reporting 应说明这只是覆盖描述，不是随机抽样代表性声明。

## 禁止筛选依据

选择 30 条 selected pilot candidate cases 时不得按以下因素选择：

- 不按模型表现选择；
- 不按当前 AIChat 是否显得好或坏选择；
- 不按是否支持主结论选择；
- 不按是否能证明 Bridge Contract / Guard / Repair 有效选择；
- 不按是否能让 LLM grader 表现更好选择；
- 不按是否让论文数字更漂亮选择。

选择依据只能是 privacy feasibility、context sufficiency、bridge-family coverage、surface-anchor coverage、help-seeking diversity、student/problem diversity 和 annotation feasibility。

## 推荐选择流程

1. 用 `real_student_online_candidate_screening_form_v1.csv` 对 137 条 candidate turns 做轻量筛查。
2. 标记 `context_sufficiency`、`rough_bridge_family`、`surface_anchor`、`help_seeking_type`、`likely_slice` 和 `candidate_for_deep_annotation`。
3. 排除隐私风险无法处理、上下文完全不可恢复、或不是 CP tutoring dialogue-state 的 turns。
4. 在可用候选中按覆盖性选择 30 条。
5. 对所有 `candidate_for_deep_annotation=yes` 的候选填写 `candidate_selection_reason`。理由应对应 bridge-family coverage、surface-anchor coverage、context-sufficiency coverage、help-seeking diversity、student/problem diversity 或 annotation feasibility。
6. 将 30 条转换为 `real_student_online_case_schema_v1.json` 的 deep annotation candidate cases。
7. 完成 privacy review、consent/status 检查和 coach annotation。
8. 在 reporting template 中报告三层漏斗，并明确 137 是 screening pool、30 是 pending consent/reporting gate 的 pilot candidate cases。只有 consent/status gate 完成后，才可报告 deep-pilot findings、示例或个案结论。

## 报告边界句

```text
We use a three-layer real-student online AIChat pilot design. The online log corpus summary describes 1156 message rows, 87 sessions, and 578 paired user-assistant turns. A lightweight screening layer identifies 137 substantial candidate turns across 59 candidate sessions. From this screening pool, 30 candidate cases covering 11 hashed students and 15 hashed problems are selected for possible privacy-reviewed deep annotation. The 137 candidate turns are not deeply annotated, and the 30 selected cases are not the full online corpus, not reportable deep-pilot evidence before consent/status completion, and not a learning-outcome study.
```
