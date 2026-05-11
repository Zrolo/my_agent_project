# Prompt-Controlled Ablation Blind-Review Analysis 2026-05-11

This report analyzes a 3-case × 5-variant blind review designed to test whether Bridge Contract improvements come from modular structure, concrete diagnostic information, or stronger generic tutoring prompt wording.

> This is development / pilot evidence only. The sample size is three cases, so it should guide the next experiment rather than support final held-out claims.

## System Summary

| Variant | N | Overall | Core6 | Micro7 | Rank1 | Ready | No leak | Minor | Major |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single_llm_structured | 3 | 3.3333 | 1.6667 | 1.6667 | 0 | 2 | 2 | 1 | 0 |
| enhanced_prompt_only | 3 | 4.3333 | 2.0 | 2.0 | 1 | 3 | 3 | 0 | 0 |
| bridge_contract_predicted | 3 | 4.0 | 1.8333 | 1.7619 | 2 | 2 | 2 | 0 | 1 |
| bridge_contract_shuffled | 3 | 2.6667 | 1.5555 | 1.4286 | 0 | 1 | 0 | 1 | 2 |
| bridge_contract_oracle | 3 | 3.3333 | 1.6667 | 1.5714 | 0 | 1 | 1 | 1 | 1 |

## Effect Decomposition

| Effect | Comparison | Overall Δ | Core6 Δ | Micro7 Δ | W/T/L |
| --- | --- | --- | --- | --- | --- |
| prompt_effect | enhanced_prompt_only - single_llm_structured | 1.0 | 0.3333 | 0.3333 | 2/0/1 |
| predicted_contract_vs_prompt | bridge_contract_predicted - enhanced_prompt_only | -0.3333 | -0.1667 | -0.2381 | 2/0/1 |
| predicted_contract_vs_shuffled | bridge_contract_predicted - bridge_contract_shuffled | 1.3333 | 0.2778 | 0.3333 | 2/1/0 |
| oracle_contract_vs_predicted | bridge_contract_oracle - bridge_contract_predicted | -0.6667 | -0.1667 | -0.1905 | 1/0/2 |
| oracle_contract_vs_shuffled | bridge_contract_oracle - bridge_contract_shuffled | 0.6667 | 0.1111 | 0.1429 | 2/1/0 |

## Case-Level Best / Worst

| Case | Best Variant | Best Quality | Best Leakage | Worst Variant | Worst Quality | Worst Leakage |
| --- | --- | --- | --- | --- | --- | --- |
| cp_bridge_001 | bridge_contract_predicted | 5.0 | no_leakage | bridge_contract_shuffled | 2.0 | major_bridge_leakage |
| cp_bridge_002 | bridge_contract_predicted | 5.0 | no_leakage | single_llm_structured | 1.0 | no_leakage |
| cp_bridge_003 | enhanced_prompt_only | 5.0 | no_leakage | bridge_contract_shuffled | 2.0 | major_bridge_leakage |

## Interpretation

1. **Prompt wording likely explains a substantial part of the quality gain.** In this 3-case smoke review, `enhanced_prompt_only` achieved the highest mean overall quality and no major leakage, so Bridge Contract gains should not be attributed to architecture alone.
2. **Concrete contracts still appear meaningful.** `bridge_contract_predicted` ranked first in 2/3 cases and outperformed `bridge_contract_shuffled`, suggesting that incorrect contracts can harm quality and that the contract content is not merely decorative.
3. **Oracle contracts are not automatically an upper bound.** In this small sample, `bridge_contract_oracle` did not outperform predicted contracts, likely because contract injection, micro-example design, and leakage control remain important even when the contract is correct.
4. **The next step is a larger paired blind review.** The same design should be expanded to 10–20 cases before making paper-level claims.

## Paper Implication

The paper should not claim that Bridge Contract architecture alone caused quality improvements. A safer claim is that Bridge Contract variants combine generic prompt effects, concrete missing-bridge diagnostic information, and modular control signals; prompt-controlled ablations are needed to separate these factors.
