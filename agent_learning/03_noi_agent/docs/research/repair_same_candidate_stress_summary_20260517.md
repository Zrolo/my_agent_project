# Repair Same-Candidate Stress Summary

This is an offline summary of filled before/after Repair review labels.

| metric | value |
| --- | ---: |
| total rows | 30 |
| labeled pairs | 30 |
| unlabeled pairs | 0 |
| mean overall delta | +0.267 |
| before overall mean | 3.367 |
| after overall mean | 3.633 |
| repair win/tie/loss | 12/11/7 |
| repair preferred/original preferred/tie | 15/11/4 |
| leakage improved/same/worse | 16/14/0 |
| burden improved/same/worse | 2/16/12 |
| still-leaks rate | 0.000 |
| too-vague-after-repair rate | 0.067 |

Interpretation: this supports same-candidate Repair stress evidence, not a main-experiment condition-level causal proof. Report quality and burden trade-offs alongside leakage reduction.

## Source Condition Split

| source condition | n | mean overall delta | quality W/T/L | leakage improved/same/worse | burden improved/same/worse | repair preferred/original/tie |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_compact_guard_repair` | 13 | -0.077 | 3/6/4 | 5/8/0 | 1/9/3 | 4/6/3 |
| `dbox_inspired_guard_repair` | 17 | 0.529 | 9/5/3 | 11/6/0 | 1/7/9 | 11/5/1 |
