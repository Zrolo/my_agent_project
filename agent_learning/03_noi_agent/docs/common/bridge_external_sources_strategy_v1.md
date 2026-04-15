# Bridge External Sources Strategy v1

## 目标

这份文档定义：

- 外部资料该怎么接入我们现在的 bridge 系统
- 哪些来源适合做主知识源
- 哪些来源只适合做补充、校对或老师参考

当前纳入讨论的来源有：

- `OI Wiki`
- `cp-pdf`
- 《算法竞赛入门经典》PDF
- 《算法竞赛入门经典 第 2 版》PDF
- 《算法竞赛入门经典 习题与解答》PDF

## 总结结论

| 来源 | 建议角色 | 是否适合直接检索 |
| --- | --- | --- |
| `OI Wiki` | bridge 正确知识底稿 / 轻量章节检索源 | 适合，但必须先教学化改写 |
| `cp-pdf` | 主外部知识源 | 适合优先接入 |
| 《算法竞赛入门经典》系列扫描版 PDF | 补充来源 / 校对来源 / 老师参考 | 不适合直接做主检索 |

一句话：

- **先把 `OI Wiki` 接成 `topic_l1/topic_l2/bridge` 的章节来源层**
- **先用 `cp-pdf` 做第一版 bridge 检索源**
- **三本扫描版书先不做主 RAG，只在后面做桥级补卡和人工校对**

## 为什么 `OI Wiki` 也要接进来

### 1. 它最适合做“正确知识底稿”

仓库：

- [OI Wiki](https://github.com/OI-wiki/OI-wiki)

`OI Wiki` 最强的地方不是“学生能直接看懂”，而是：

- 章节完整
- 术语标准
- 主目录稳定
- 很适合映射成：
  - `topic_l1`
  - `topic_l2`
  - `bridge`

### 2. 它比 `cp-pdf` 更适合做章节级定位

对我们当前 bridge 系统来说，`OI Wiki` 很适合帮助系统回答：

- 这座桥属于哪个知识域
- 这座桥应该挂在哪个小专题下
- 后面长尾 bridge 应该优先去哪一章找

### 3. 但它不适合直接给学生看

原因很明确：

- 偏百科
- 术语密
- 解释更完整，但不够“桥级教学”

所以 `OI Wiki` 的正确用法不是：

- 原文直接展示给学生

而是：

- 作为底层知识来源
- 再经过 bridge 级教学改写

## 为什么 `cp-pdf` 先做主知识源

### 1. 它已经是结构化 PDF 仓库

仓库：

- [cp-pdf](https://github.com/EndlessCheng/cp-pdf)

当前仓库内已经有很多可直接利用的资料，例如：

- `Competitive Programmer’s Handbook.pdf`
- `Guide to Competitive Programming - Learning and Improving Algorithms Through Contests.pdf`
- `挑战程序设计竞赛(第2版).pdf`
- `背包问题九讲 2.0 beta1.2.pdf`
- `字符串算法选讲-金策.pdf`
- `后缀数组——处理字符串的有力工具.pdf`
- `国家集训队2016论文集.pdf`

这些文件更适合：

- 提取文字
- 做章节切片
- 做桥级片段
- 做轻量检索

### 2. 它覆盖面比单本书更广

对于我们当前 bridge 系统来说，`cp-pdf` 更容易覆盖：

- `shared_prefix_merging`
- `lazy_semantics`
- `check_condition`
- `left_bound_update`
- `state_design`
- `transition_design`
- `greedy_basis`
- `constraint_modeling`

### 3. 它更适合长尾 bridge

单本入门书更适合讲基础桥。
但 `cp-pdf` 里同时有：

- 基础教材
- 专题讲义
- 论文集

这意味着后面碰到：

- `shared_prefix_merging`
- `suffix-array` 相关桥
- 更细的数据结构语义桥

时，不需要重新换源。

## 为什么三本《算法竞赛入门经典》系列不适合先做主检索

### 1. 当前拿到的是扫描版

实际检查结果：

- 这三本 PDF 用 `fitz` 直接抽文本，前若干页基本拿不到可用文本
- 说明它们当前更接近扫描图像版，而不是可复制文本版

这意味着：

- 不能直接做高质量全文检索
- 不能直接做稳定切片
- 公式、代码、目录都容易 OCR 出错

### 2. OCR 成本高

如果现在就把它们当主源，会遇到这些问题：

- 需要先 OCR
- 需要人工校对
- 需要手动切章节
- 需要清洗公式和代码

这会拖慢我们当前真正重要的目标：

- 先让学生端 bridge 补课更稳

### 3. 它们更适合做“精修桥”的补充

这三本书仍然有价值，但更适合：

- 做高频桥的精修补充
- 做知识卡文案校对
- 做老师审查参考

而不是现在就做：

- 大规模自动化 bridge 检索主源

## 最终分工

### A. `cp-pdf`

定位：

- `bridge_snippet_source`

主要用途：

- 第一版 bridge 轻量检索
- 长尾 bridge 扩覆盖
- 长尾 bridge 的老师参考

### B. `OI Wiki`

定位：

- `bridge_taxonomy_source`
- `bridge_grounding_source`

主要用途：

- `topic_l1 / topic_l2 / bridge` 的章节映射
- 长尾 bridge 的章节定位
- 知识卡和补课文案的正确知识底稿

限制：

- 不直接把原文给学生看
- 必须先转成：
  - `misconception`
  - `bridge_explanation`
  - `mini_example`
  - `algorithm_overview`

### C. 《算法竞赛入门经典》三本扫描版

定位：

- `manual_bridge_reference`

主要用途：

- 高频 bridge 的人工补卡
- 知识卡文案打磨
- 经典例子的校对来源

不建议当前用途：

- 不建议现在直接做全文 RAG
- 不建议现在直接做大规模自动切片

## 推荐接入顺序

### 第一阶段

先做：

- `OI Wiki`
- `cp-pdf`

选第一批 6 到 8 个 bridge：

- `shared_prefix_merging`
- `lazy_semantics`
- `left_bound_update`
- `check_condition`
- `state_design`
- `transition_design`
- `complexity_fit`
- `constraint_modeling`

从 `OI Wiki / cp-pdf` 里给每个 bridge 建：

- `source_title`
- `chapter_or_section`
- `excerpt`
- `topic_l1`
- `topic_l2`
- `bridge`

### 第二阶段

再把三本《算法竞赛入门经典》作为人工补充源接入：

- 只补高频 bridge
- 只补我们已经证明学生最常卡的桥

### 第三阶段

如果后面 OCR 和清洗质量足够稳定，再考虑：

- 从扫描版书里继续抽更多桥级片段

## 最小数据结构

建议先统一成：

```json
{
  "source_family": "cp-pdf",
  "source_title": "Competitive Programmer’s Handbook",
  "chapter_or_section": "Binary Search",
  "topic_l1": "basic",
  "topic_l2": "binary_search",
  "bridge": "left_bound_update",
  "excerpt": "......",
  "priority": "high"
}
```

扫描版书如果后面接进来，就改成：

```json
{
  "source_family": "book_scan",
  "source_title": "算法竞赛入门经典 第2版",
  "chapter_or_section": "二分查找",
  "topic_l1": "basic",
  "topic_l2": "binary_search",
  "bridge": "left_bound_update",
  "excerpt": "......",
  "needs_manual_review": true
}
```

## 当前最实际的下一步

不是立刻去 OCR 三本书。

而是：

1. 从 `cp-pdf` 里挑第一批最适合的 PDF
2. 建第一版 bridge 片段索引
3. 只接高频 bridge
4. 三本扫描版书先保留为人工补充源

## 一句话

当前最稳的路线是：

- **`OI Wiki` 做 bridge taxonomy 与正确知识底稿**
- **`cp-pdf` 做主外部知识源**
- **三本扫描版书只做精修桥的补充和校对**
