# OI Topic Taxonomy For Review System

## Purpose

This document defines a practical `topic taxonomy` for the current NOI review system.

It is meant to answer:

- `review_mode`: the student is stuck in what way
- `error_layer`: the student is stuck at what abstraction layer
- `topic taxonomy`: the student is stuck in what knowledge topic

The goal is not to copy all of OI Wiki into prompts. The goal is to give the system a stable knowledge map so future retrieval, prompting, remediation, teacher analytics, and case coverage can all align to the same topic language.

Reference source for topic coverage direction:
- [OI Wiki GitHub repository](https://github.com/OI-wiki/OI-wiki)

## What The Taxonomy Is Not

This taxonomy is not:

- a full dump of all competitive programming knowledge
- a replacement for `review_mode`
- a replacement for `error_layer`
- a prompt that tries to teach every algorithm directly

The current `review_prompt` should continue to focus on pedagogy:

- evidence use
- bridge diagnosis
- scaffolding strength
- quiz progression

The taxonomy should focus on knowledge organization.

## Why The Current System Needs It

The current system already has:

- `review_mode`
  - `failed_verdict`
  - `stuck_bridge`
  - `editorial_transfer`
  - `independent_reflect`
- `review_family`
  - `failure_diagnosis`
  - `success_reflection`
- `error_layer`
  - `reading`
  - `method`
  - `modeling`
  - `core_design`
  - `implementation`

These answer:

- how the student is stuck
- how deep the problem is

But they do not answer:

- what knowledge area the student is stuck in

Example:

- `review_mode = stuck_bridge`
- `error_layer = core_design`

This still does not tell us whether the student is stuck on:

- trie prefix merging
- tree diameter candidate reasoning
- DP state meaning
- binary search `check(mid)`
- greedy exchange argument

That missing layer is what the taxonomy fills.

## Design Principles

### 1. Three levels are enough

Use three levels:

- `L1`: major domain
- `L2`: subdomain
- `L3`: bridge-level concept

This is enough for:

- routing
- retrieval
- teacher stats
- case design
- quiz templates

### 2. Bridge-level concepts should match the current review system

The finest-grained topics should line up with the kinds of bridges your system already teaches, such as:

- state meaning
- transition completeness
- check meaning
- enumeration order
- greedy reason
- prefix sharing
- candidate set reasoning

### 3. Prefer practical grouping over textbook purity

This taxonomy should be optimized for:

- student review
- micro-remediation
- teacher analytics

not for encyclopedic completeness.

## Proposed Taxonomy

### L1: Dynamic Programming

Suggested `topic_key`: `dp`

#### L2

- `linear_dp`
- `interval_dp`
- `tree_dp`
- `knapsack`
- `digit_dp`
- `memoized_search`
- `state_compression_dp`
- `probability_dp`
- `optimization_dp`

#### L3 bridge concepts

- `state_design`
- `transition_design`
- `enumeration_order`
- `boundary_initialization`
- `state_compression_meaning`
- `subproblem_definition`
- `memoization_meaning`
- `answer_extraction`

### L1: Graph Theory

Suggested `topic_key`: `graph`

#### L2

- `graph_traversal`
- `shortest_path`
- `union_find`
- `mst`
- `tree_basics`
- `tree_diameter`
- `toposort`
- `bipartite_graph`
- `network_flow`
- `scc`

#### L3 bridge concepts

- `reachability_reasoning`
- `connected_component_linking`
- `tree_diameter_candidates`
- `path_candidate_reasoning`
- `union_find_meaning`
- `bfs_layer_meaning`
- `dfs_state_meaning`
- `graph_modeling`

### L1: Data Structures

Suggested `topic_key`: `data_structure`

#### L2

- `prefix_sum`
- `difference`
- `monotonic_stack`
- `monotonic_queue`
- `heap`
- `segment_tree`
- `fenwick`
- `disjoint_set`
- `balanced_tree`
- `sparse_table`

#### L3 bridge concepts

- `range_info_meaning`
- `lazy_tag_meaning`
- `query_update_split`
- `structure_choice`
- `merge_rule`
- `maintenance_invariant`
- `offline_vs_online`

### L1: String Algorithms

Suggested `topic_key`: `string`

#### L2

- `trie`
- `kmp`
- `string_hash`
- `suffix_array`
- `automaton`
- `manacher`

#### L3 bridge concepts

- `prefix_query`
- `shared_prefix_merging`
- `node_count_meaning`
- `failure_link_meaning`
- `pattern_matching_window`
- `hash_collision_awareness`
- `string_modeling`

### L1: Greedy

Suggested `topic_key`: `greedy`

#### L2

- `interval_greedy`
- `sorting_greedy`
- `construction_greedy`
- `exchange_argument`
- `priority_rule`

#### L3 bridge concepts

- `greedy_basis`
- `local_choice_reason`
- `exchange_reasoning`
- `priority_order_meaning`
- `future_damage_check`

### L1: Search

Suggested `topic_key`: `search`

#### L2

- `dfs`
- `bfs`
- `backtracking`
- `iterative_deepening`
- `state_search`
- `pruning`

#### L3 bridge concepts

- `search_state_definition`
- `pruning_condition`
- `visited_meaning`
- `branching_order`
- `state_encoding`

### L1: Binary Search And Feasibility

Suggested `topic_key`: `binary_search`

#### L2

- `binary_search_answer`
- `binary_search_index`
- `feasibility_check`
- `parametric_search`

#### L3 bridge concepts

- `check_condition`
- `monotonicity_reason`
- `mid_meaning`
- `check_true_meaning`
- `search_boundary_update`

### L1: Math And Number Theory

Suggested `topic_key`: `math`

#### L2

- `modular_arithmetic`
- `gcd_lcm`
- `prime`
- `combinatorics`
- `probability`
- `matrix`
- `game_theory`

#### L3 bridge concepts

- `formula_source`
- `counting_model`
- `mod_meaning`
- `proof_step_reason`
- `number_property_use`

### L1: Modeling And Complexity

Suggested `topic_key`: `modeling`

#### L2

- `problem_translation`
- `complexity_estimation`
- `method_selection`
- `constraint_reading`
- `simulation`

#### L3 bridge concepts

- `scale_estimation`
- `candidate_method_rejection`
- `constraint_signal`
- `object_relation_mapping`
- `operation_count_reasoning`

### L1: Implementation

Suggested `topic_key`: `implementation`

#### L2

- `boundary_cases`
- `indexing`
- `overflow`
- `precision`
- `input_output`
- `debugging`

#### L3 bridge concepts

- `off_by_one`
- `loop_boundary`
- `overflow_risk`
- `type_choice`
- `corner_case_coverage`
- `debug_observation`

## Recommended Mapping Into The Current System

Each review item should eventually support these parallel labels:

- `review_mode`
- `review_family`
- `error_layer`
- `topic_l1`
- `topic_l2`
- `topic_l3`

Example:

```json
{
  "review_mode": "stuck_bridge",
  "review_family": "failure_diagnosis",
  "error_layer": "core_design",
  "topic_l1": "string",
  "topic_l2": "trie",
  "topic_l3": "shared_prefix_merging"
}
```

Another example:

```json
{
  "review_mode": "failed_verdict",
  "review_family": "failure_diagnosis",
  "error_layer": "method",
  "topic_l1": "binary_search",
  "topic_l2": "feasibility_check",
  "topic_l3": "check_true_meaning"
}
```

## Recommended First-Wave Topics

Do not try to align all of OI Wiki at once.

The best first-wave topics are the ones already appearing often in your system:

- `dp.state_design`
- `dp.transition_design`
- `dp.enumeration_order`
- `binary_search.check_condition`
- `greedy.greedy_basis`
- `string.trie.shared_prefix_merging`
- `graph.tree_diameter.tree_diameter_candidates`
- `modeling.scale_estimation`
- `modeling.method_selection`
- `implementation.boundary_cases`

## How This Should Help The Product

### 1. Better retrieval

Instead of injecting all knowledge into prompt, future retrieval can use:

- current problem tags
- student bottleneck
- topic taxonomy labels

Then fetch only a small related knowledge slice.

### 2. Better remediation

Different bridge types can use different scaffolds:

- `dp.state_design`
  - focus on what one state cell means
- `binary_search.check_condition`
  - focus on what `check(mid)` means when true
- `string.trie.shared_prefix_merging`
  - focus on why shared prefix avoids repeated scanning

### 3. Better teacher analytics

Teachers can see not only:

- who is stuck

but also:

- which topics produce the most `assisted_success`
- which bridge concepts produce the most `not_mastered`

### 4. Better evaluation coverage

Cases can be sampled by:

- topic family
- bridge concept
- mode
- mastery outcome

This gives a much better evaluation grid than only checking generic output quality.

## What Should Stay Out Of Prompt

Do not expand `review_prompt` to include:

- the whole OI Wiki
- long algorithm definitions
- large theory catalogs
- topic encyclopedias

Prompt should continue to answer:

- how to teach this step

The taxonomy and retrieval layer should answer:

- what knowledge this step belongs to

## Suggested Next Step

After adopting this taxonomy draft, the next practical step should be:

1. add taxonomy labels to high-frequency bridges already in use
2. build a small mapping from current problem tags and bridge types to `topic_l1/l2/l3`
3. only then design selective OI Wiki snippet retrieval

That sequence is much safer than trying to inject all knowledge into prompt first.
