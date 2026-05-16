# Bridge Taxonomy Coverage Review v1

This document answers a taxonomy-design question:

> Should bridge subtypes / forbidden content keep expanding by concrete algorithm, or should they be abstract bridge shapes that cover most competitive-programming cases?

Conclusion: **do not enumerate concrete algorithms. Keep a small set of abstract bridge shapes, and record concrete algorithm context through `algorithm_topic`, `registered_focus_id`, and notes.**

## External Reference Check

CP-Algorithms organizes competitive-programming knowledge into broad areas such as Algebra, Data Structures, Dynamic Programming, String Processing, Combinatorics, Numerical Methods, Geometry, and Graphs; its graph section further includes traversal, connectivity, shortest paths, spanning trees, cycles, LCA, flows, and matching. OI Wiki similarly organizes content under algorithm basics, search, dynamic programming, strings, math, data structures, graph theory, computational geometry, miscellaneous topics, and special topics. USACO Guide’s Gold page groups topics into Math, Dynamic Programming, Graphs, Data Structures, Trees, and Additional Topics, and explicitly notes that its topic list is not exhaustive.

These references show that competitive-programming knowledge is open-ended. If bridge subtypes are named after concrete algorithms such as `Dijkstra stale-entry guard`, `Floyd intermediate-loop order`, or `SPFA enqueue condition`, the taxonomy will keep expanding and coaches may assume that unlisted algorithms have no valid label.

Sources:

- CP-Algorithms main page: https://cp-algorithms.com/
- OI Wiki main page: https://oiwiki.com/
- USACO Guide Gold topics: https://usaco.guide/gold

## Recommended Three-Layer Structure

| Layer | Purpose | Examples |
| --- | --- | --- |
| `algorithm_topic` | Records algorithm domain or knowledge point | `graph.shortest_path.dijkstra`, `dp.interval`, `string.kmp`, `geometry.convex_hull` |
| `bridge_subtype` | Records the transferable reasoning shape the student is missing | `predicate.obsolete_candidate_guard`, `ordering.dependency_satisfaction_order` |
| `forbidden_content` | Records the leakage shape that must not be directly completed | `no_exact_guard_condition`, `no_full_invariant_proof` |

Coaches should first identify the missing reasoning bridge, then record the specific algorithm in topic / focus / notes instead of adding an algorithm-specific subtype.

## Recommended Coverage Map

The table below is a coverage map, not a requirement to add every row to the dropdown immediately. Rows marked “existing” are already covered by the current schema; rows marked “candidate” should be added only if repeated cases appear.

| Abstract bridge shape | Status | Common student wording | Algorithm examples | Coach explanation |
| --- | --- | --- | --- | --- |
| Goal / constraint decomposition | Existing | “What is the problem asking me to optimize?” | All domains | Clarify inputs, outputs, optimize/count/feasibility targets, and constraints. |
| Object-relation modeling | Existing | “What is a vertex? What is an edge?” | Graph modeling, interval modeling, state modeling | Convert problem objects, relations, and operations into computable structure. |
| Method-selection signal | Existing | “Is this binary search / DP / graph?” | DP, binary search, greedy, graph, data structures | Let students validate the algorithm direction from problem features instead of receiving a direct label. |
| State / representation semantics | Existing | “What does dp[j] / dist / mask mean?” | DP, bitmask BFS, shortest path, automata | Define what an array cell, node field, mask, or auxiliary state stores. |
| Prefix / fallback / failure-link semantics | Existing | “What does next[i] mean?” | KMP, Aho-Corasick, suffix automaton, Trie fallback | Explain mismatch fallback, shared prefix, or compressed history information. |
| Transition / recurrence source | Existing | “Where does this state come from?” | DP, tree DP, combinatorial recurrence, graph DP | Identify predecessor states, decisions, or subproblems that form the current state. |
| Predicate-condition semantics | Existing | “What is check testing?” | Binary search, if conditions, relax, validity checks | Clarify true/false, update/no-update, valid/invalid meaning. |
| Obsolete / invalid candidate guard | Existing | “Should I skip old queue entries?” | Dijkstra heap, A*, repeated-enqueue BFS, lazy-deletion heaps | Decide whether the popped candidate still matches the current state. |
| Dependency / update order | Existing | “Why reverse / topological / by length?” | Compressed knapsack, interval DP, DAG DP, Floyd intermediate loop | Ensure dependencies are ready, or avoid contaminating old states in the same round. |
| Single-use update order | Existing | “Why does forward update reuse the same item?” | 0/1 knapsack, rolling arrays, in-place DP | Prevent a just-written state from being read again in the same update round. |
| Contribution aggregation / difference marking | Existing | “Why only mark endpoints?” | Prefix sums, difference arrays, tree difference, BIT range tricks | Compress repeated effects and recover them through prefix/DFS/query aggregation. |
| Data-structure operation mapping | Existing | “Does this action map to push or pop?” | Heap, DSU, segment tree, Fenwick, monotonic stack | Map problem actions to query, update, merge, pop, etc. |
| Maintained-summary semantics | Candidate | “What should each segment-tree node store?” | Segment tree, Fenwick, Sparse Table, Treap | Clarify the summary maintained by each node/block/table and how children maintain it. |
| Monotonic / dominance elimination | Existing | “Why is the popped element never useful again?” | Monotonic stack/queue, convex hull optimization, greedy elimination | Explain why one candidate dominates another. |
| Settled-candidate invariant | Existing | “Why is it final after popping?” | Dijkstra, BFS layers, topological processing, Prim/Kruskal partial choices | Explain why a selected/settled result will not be overturned later. |
| Exchange / replacement argument | Existing | “Why does this greedy choice not hurt?” | Activity selection, sorting greedy, MST cut/cycle arguments | Use exchange, replacement, cut, or cycle reasoning to justify a local choice. |
| Mathematical property / modular invariant | Candidate | “Why does parity/mod/gcd decide it?” | Number theory, modular arithmetic, parity, gcd, CRT | Turn arithmetic constraints into preserved mathematical relations. |
| Counting partition / inclusion-exclusion | Candidate | “Why add this and subtract that?” | Combinatorics, inclusion-exclusion, Catalan, basic generating functions | Partition cases and prevent double-counting or omissions. |
| Geometric predicate / relation | Candidate | “What does the cross-product sign mean?” | Convex hull, segment intersection, point-in-polygon, geometric sweep line | Convert geometry relations into orientation, area, ordering, or intersection predicates. |
| Search pruning / deduplication | Candidate | “How should visited be defined? Why can we prune?” | DFS/BFS, backtracking, IDA*, meet-in-the-middle | Decide which branches are equivalent, repeated, impossible, or dominated. |
| Complexity bottleneck localization | Existing | “Will two loops pass?” | Brute-force optimization, preprocessing, replacing inner loops | Identify the slow layer or operation before choosing an optimization. |
| Implementation boundary / initialization | Existing | “Should i go to n or n-1? What is the base case?” | All implementation tasks | Handle indices, intervals, base cases, sentinels, types, and I/O. |
| Debugging evidence / minimal counterexample | Existing | “WA but I do not know where.” | All debugging scenarios | Collect a minimal failing case, actual output, expected output, and suspicious location before guessing a fix. |
| Reflection / transfer signal | Existing | “How do I recognize this next time?” | Review and transfer | Summarize trigger conditions, typical structure, and reusable questions. |

## What Not To Expand Right Now

Do not add separate subtypes for:

- SPFA;
- Floyd;
- Tarjan;
- Dinic;
- Kruskal;
- KMP;
- segment-tree lazy propagation;
- digit DP;
- tree difference;
- concrete knapsack variants.

These should be distinguished through `algorithm_topic` or `registered_focus_id`; the bridge subtype should record the abstract reasoning shape.

| Concrete algorithm issue | Recommended subtype | Recommended forbidden content |
| --- | --- | --- |
| SPFA repeated enqueue / stale candidate | `predicate.obsolete_candidate_guard` or `predicate.feasibility_truth_direction` | `no_exact_guard_condition` |
| Why Floyd enumerates `k` | `ordering.subproblem_size_dependency_order` or approximate with `ordering.topological_dependency` | `no_exact_iteration_template` |
| KMP prefix-array meaning | `state.failure_link_or_prefix_semantics` | `no_exact_state_definition` |
| Why Dinic advances through a level graph | combination of `representation_state_bridge` and `predicate_condition_bridge` | `no_exact_modeling_plan` / `no_exact_check_condition` |
| Why Kruskal can take the next edge | `correctness.settled_candidate_invariant` or `correctness.local_choice_exchange_argument` | `no_full_invariant_proof` |

## Recommendation For The Current Schema

The current Research v1 schema already covers most common tutoring cases. Do not add many more dropdown items in the short term, or annotation burden will rise again.

Track these five candidates during 50-case labeling:

1. `math.property_invariant_bridge`: number theory / modular / parity / gcd property bridges.
2. `counting.partition_inclusion_bridge`: counting partitions, inclusion-exclusion, overcount/undercount control.
3. `geometry.predicate_relation_bridge`: cross product, orientation, intersection, convexity, geometric predicates.
4. `search.pruning_dedup_bridge`: search deduplication, pruning, and visited-state design.
5. `ds.maintained_summary_semantics`: maintained summaries in nodes, blocks, or tables.

If one candidate appears repeatedly in the 50-case set or real logs, add it to v3. Otherwise record it in `primary_bridge_subtype_note`.

## Short Coach Rule

```text
First ask: what reasoning relation is the student missing?
Then ask: can this relation transfer to other algorithms?
If yes, choose an abstract subtype.
Put concrete algorithm names in topic / focus / notes.
For forbidden content, label the type of relation that must not be revealed, not an algorithm-specific rule.
```
