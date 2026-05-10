import argparse
import csv
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

from evals.aichat.export_coach_response_review_workbook import REVIEW_COLUMNS


DEFAULT_INPUT_CSV = Path("docs/research/coach_response_review_workbook_v1.csv")
DEFAULT_OUTPUT_XLSX = Path("docs/research/coach_response_review_workbook_v1.zh.xlsx")

CHINESE_HEADERS = {
    "case_id": "样本编号",
    "anonymized_response_id": "匿名回复编号",
    "problem_ref": "题目编号",
    "student_message": "学生当前问题",
    "problem_context": "题目/上下文",
    "recent_dialogue": "近期对话",
    "response_text": "AI 回复（要评分）",
    "coach_bridge_identification_score": "是否抓住卡点 0-2",
    "coach_groundedness_score": "是否贴合题目/对话 0-2",
    "coach_scaffold_appropriateness_score": "帮助强度是否合适 0-2",
    "coach_bridge_leakage_control_score": "是否控制关键桥泄露 0-2",
    "coach_next_step_clarity_score": "下一步是否清楚 0-2",
    "coach_single_focus_coherence_score": "是否保持单一焦点 0-2",
    "coach_bridge_oriented_micro_example_score": "桥梁导向微型例子 0-2",
    "coach_leakage_label": "泄露标签",
    "coach_preference_rank": "同题回复排序",
    "coach_notes": "备注",
    "review_status": "评审状态",
}

FIELD_HELP = {
    "coach_bridge_identification_score": "这条回复有没有抓住学生当前真正缺的桥梁/卡点。不是看讲得多不多，而是看是否对准。",
    "coach_groundedness_score": "这条回复是否利用了题目、学生话语和近期对话证据，而不是泛泛讲算法。",
    "coach_scaffold_appropriateness_score": "帮助强度是否适合当前学生状态。太弱、太强、直接给答案都要扣分。",
    "coach_bridge_leakage_control_score": "是否避免说穿当前关键桥。关键桥指学生这一轮本该自己构造的状态、转移、check、公式、局部条件等。",
    "coach_next_step_clarity_score": "学生看完是否知道下一步具体做什么，且这个下一步能实际回答或执行。",
    "coach_single_focus_coherence_score": "回复是否围绕一个主要卡点推进，避免同时讲多个方向让学生更乱。",
    "coach_bridge_oriented_micro_example_score": "如果回复使用小例子，例子是否引导学生提炼可迁移的桥梁关系，而不是只完成一次临时任务。没有小例子但回复合理时可评 2。",
    "coach_leakage_label": "判断这条回复实际有没有泄露当前关键桥或完整答案/代码。",
    "coach_preference_rank": "同一个样本如果有多条匿名回复，可按质量排序。1 表示最好，可留空。",
    "review_status": "评完后选“已评完”；不确定就选“需要讨论”。",
}

BRIDGE_IDENTIFICATION_OPTIONS = [
    "2｜好：直接针对学生当前缺失的桥梁/卡点",
    "1｜一般：相关但偏宽、绕了一点，或只抓到部分卡点",
    "0｜差：没有抓住当前卡点，或答非所问",
]

GROUNDEDNESS_OPTIONS = [
    "2｜好：明显利用题目、学生话语或近期对话证据",
    "1｜一般：有一些贴合，但仍偏泛",
    "0｜差：像通用回答，和上下文关系弱",
]

SCAFFOLD_OPTIONS = [
    "2｜好：帮助强度合适，不太弱也不过强",
    "1｜一般：略弱或略强，但仍有教学价值",
    "0｜差：直接给答案/代码，或只是空泛追问",
]

LEAKAGE_CONTROL_OPTIONS = [
    "2｜好：没有说穿当前关键桥",
    "1｜一般：给了偏强线索，但学生仍需自己推理",
    "0｜差：直接补完关键桥，或给完整答案/代码",
]

NEXT_STEP_OPTIONS = [
    "2｜好：学生下一步明确、具体、可回答",
    "1｜一般：有下一步，但较宽、较多或不够具体",
    "0｜差：没有可执行下一步",
]

SINGLE_FOCUS_OPTIONS = [
    "2｜好：始终围绕一个主要焦点推进",
    "1｜一般：基本单焦点，但有少量漂移",
    "0｜差：多个目标混在一起，容易让学生更乱",
]

BRIDGE_ORIENTED_MICRO_EXAMPLE_OPTIONS = [
    "2｜好：例子能引导学生抽象可迁移的桥梁关系",
    "1｜一般：例子相关，但更像一次临时小任务",
    "0｜差：例子和卡点关系弱，或直接替学生补完关键桥",
    "N/A｜没有使用微型例子，无法单独评价",
]

LEAKAGE_LABEL_OPTIONS = [
    "no_leakage｜无泄露：没有说穿当前关键桥",
    "minor_bridge_leakage｜轻微桥梁泄露：提示偏强但学生仍要推理",
    "major_bridge_leakage｜严重桥梁泄露：直接补完当前关键桥",
    "answer_leakage｜答案/代码泄露：给出完整题解、完整步骤或可提交代码",
]

PREFERENCE_RANK_OPTIONS = [
    "1｜同题中最好",
    "2｜同题中第二",
    "3｜同题中第三",
    "tie｜并列/无法区分",
]

REVIEW_STATUS_OPTIONS = [
    "unlabeled｜未评",
    "labeled｜已评完",
    "needs_discussion｜不确定，需要讨论",
    "ai_prelim_reviewed｜AI 预评，待教练复核",
]

OPTION_LISTS = {
    "bridge_identification": BRIDGE_IDENTIFICATION_OPTIONS,
    "groundedness": GROUNDEDNESS_OPTIONS,
    "scaffold": SCAFFOLD_OPTIONS,
    "leakage_control": LEAKAGE_CONTROL_OPTIONS,
    "next_step": NEXT_STEP_OPTIONS,
    "single_focus": SINGLE_FOCUS_OPTIONS,
    "bridge_oriented_micro_example": BRIDGE_ORIENTED_MICRO_EXAMPLE_OPTIONS,
    "leakage_label": LEAKAGE_LABEL_OPTIONS,
    "preference_rank": PREFERENCE_RANK_OPTIONS,
    "review_status": REVIEW_STATUS_OPTIONS,
}

COLUMN_WIDTHS = {
    "A": 14,
    "B": 18,
    "C": 14,
    "D": 36,
    "E": 42,
    "F": 34,
    "G": 58,
    "H": 24,
    "I": 26,
    "J": 28,
    "K": 30,
    "L": 24,
    "M": 26,
    "N": 30,
    "O": 34,
    "P": 18,
    "Q": 34,
    "R": 18,
}


def load_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _add_options_sheet(workbook: Workbook) -> dict[str, str]:
    sheet = workbook.create_sheet("下拉选项")
    ranges = {}
    for col_idx, (name, values) in enumerate(OPTION_LISTS.items(), 1):
        sheet.cell(row=1, column=col_idx, value=name)
        sheet.cell(row=1, column=col_idx).font = Font(bold=True)
        for row_idx, value in enumerate(values, 2):
            sheet.cell(row=row_idx, column=col_idx, value=value)
        col_letter = sheet.cell(row=1, column=col_idx).column_letter
        ranges[name] = f"'下拉选项'!${col_letter}$2:${col_letter}${len(values) + 1}"
        sheet.column_dimensions[col_letter].width = 42
    return ranges


def _add_data_validation(sheet, cell_range: str, formula_range: str) -> None:
    validation = DataValidation(type="list", formula1=f"={formula_range}", allow_blank=True)
    validation.error = "请从下拉列表中选择，或留空。"
    validation.errorTitle = "无效选项"
    sheet.add_data_validation(validation)
    validation.add(cell_range)


def _style_review_sheet(sheet, headers: list[str]) -> None:
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    machine_fill = PatternFill("solid", fgColor="F2F5F7")
    input_fill = PatternFill("solid", fgColor="FFF7D6")
    source_fill = PatternFill("solid", fgColor="FFFFFF")
    thin = Side(style="thin", color="D7DEE8")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for cell in sheet[1]:
        cell.font = Font(bold=True, color="17324D")
        cell.fill = header_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = border
    for cell in sheet[2]:
        cell.font = Font(size=9, color="667085")
        cell.fill = machine_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = border
    for row in sheet.iter_rows(min_row=3, max_row=sheet.max_row, max_col=len(headers)):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = border
            cell.fill = input_fill if cell.column >= 8 else source_fill
    for col_letter, width in COLUMN_WIDTHS.items():
        sheet.column_dimensions[col_letter].width = width
    sheet.row_dimensions[1].height = 38
    sheet.row_dimensions[2].height = 28
    sheet.row_dimensions[2].hidden = True
    for row_idx in range(3, sheet.max_row + 1):
        sheet.row_dimensions[row_idx].height = 96
    sheet.freeze_panes = "H3"
    sheet.auto_filter.ref = f"A2:{sheet.cell(row=2, column=len(headers)).coordinate}"


def _add_instruction_sheet(workbook: Workbook) -> None:
    sheet = workbook.active
    sheet.title = "开始这里"
    rows = [
        ["怎么使用", "进入“盲评表”，先看学生当前问题、题目/上下文和 AI 回复，再填写黄色评分列。"],
        ["是否盲评", "匿名回复编号隐藏了系统来源。不要根据模型名评分，只看回复本身。"],
        ["评分方式", "六个维度都用 0/1/2：2=好，1=一般，0=差。每格都有中文下拉解释。"],
        ["泄露判断", "关键问题是：看完 AI 回复后，学生是否还需要自己构造当前关键桥？如果不需要，通常就是严重桥梁泄露。"],
        ["不确定怎么办", "review_status 选“不确定，需要讨论”，备注写原因。"],
    ]
    sheet.append(["AIChat 回复盲评说明", ""])
    for row in rows:
        sheet.append(row)
    sheet["A1"].font = Font(bold=True, size=16, color="17324D")
    sheet["A1"].fill = PatternFill("solid", fgColor="D9EAF7")
    for row_cells in sheet.iter_rows(min_row=2, max_col=2):
        row_cells[0].font = Font(bold=True, color="17324D")
        for cell in row_cells:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    sheet.column_dimensions["A"].width = 18
    sheet.column_dimensions["B"].width = 96


def _add_guide_sheet(workbook: Workbook) -> None:
    sheet = workbook.create_sheet("评分说明")
    rows = [
        ["0-2 评分总原则", "2=好，1=一般，0=差。评分对象是 AI 回复，不是学生。"],
        ["是否抓住卡点", "看 AI 是否对准学生当前缺失的桥梁/卡点，而不是泛泛讲题解。"],
        ["是否贴合题目/对话", "看 AI 是否利用了题目、学生原话、近期对话或代码证据。"],
        ["帮助强度是否合适", "看 AI 是否给了合适脚手架；直接补答案/代码或只空泛追问都不好。"],
        ["是否控制关键桥泄露", "看 AI 是否避免说穿学生本轮应该自己构造的状态、转移、check、公式、局部条件等。"],
        ["下一步是否清楚", "看学生读完后是否知道接下来要回答/尝试哪一步。"],
        ["是否保持单一焦点", "看回复是否围绕一个核心卡点，不同时抛出多个无关任务。"],
        ["桥梁导向微型例子", "如果用了例子，看它是否帮助学生提炼可迁移关系；只是让学生算一下/选一下但没有抽象方向，通常只能给 1。"],
        ["泄露标签", "no_leakage=无泄露；minor=偏强但仍需推理；major=补完关键桥；answer=完整题解/步骤/代码泄露。"],
        ["同题回复排序", "如果同一个 case 有多条回复，可填 1/2/3；只评单条时可留空。"],
    ]
    for row in rows:
        sheet.append(row)
    sheet["A1"].font = Font(bold=True, size=13, color="17324D")
    sheet["A1"].fill = PatternFill("solid", fgColor="D9EAF7")
    for row_cells in sheet.iter_rows():
        row_cells[0].font = Font(bold=True, color="17324D")
        for cell in row_cells:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    sheet.column_dimensions["A"].width = 24
    sheet.column_dimensions["B"].width = 100


def export_xlsx(
    *,
    input_csv: Path = DEFAULT_INPUT_CSV,
    output_xlsx: Path = DEFAULT_OUTPUT_XLSX,
) -> int:
    rows = load_csv_rows(input_csv)
    if not rows:
        raise ValueError(f"No rows found in {input_csv}")

    headers = [header for header in REVIEW_COLUMNS if header in rows[0]]
    workbook = Workbook()
    _add_instruction_sheet(workbook)
    ranges = _add_options_sheet(workbook)
    _add_guide_sheet(workbook)

    sheet = workbook.create_sheet("盲评表", 1)
    sheet.append([CHINESE_HEADERS.get(header, header) for header in headers])
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header, "") for header in headers])
    _style_review_sheet(sheet, headers)

    field_to_col = {field: idx + 1 for idx, field in enumerate(headers)}
    max_row = sheet.max_row
    validations = {
        "coach_bridge_identification_score": ranges["bridge_identification"],
        "coach_groundedness_score": ranges["groundedness"],
        "coach_scaffold_appropriateness_score": ranges["scaffold"],
        "coach_bridge_leakage_control_score": ranges["leakage_control"],
        "coach_next_step_clarity_score": ranges["next_step"],
        "coach_single_focus_coherence_score": ranges["single_focus"],
        "coach_bridge_oriented_micro_example_score": ranges["bridge_oriented_micro_example"],
        "coach_leakage_label": ranges["leakage_label"],
        "coach_preference_rank": ranges["preference_rank"],
        "review_status": ranges["review_status"],
    }
    for field, formula_range in validations.items():
        col_idx = field_to_col.get(field)
        if col_idx:
            col = sheet.cell(row=1, column=col_idx).column_letter
            _add_data_validation(sheet, f"{col}3:{col}{max_row}", formula_range)
    for field, help_text in FIELD_HELP.items():
        col_idx = field_to_col.get(field)
        if col_idx:
            sheet.cell(row=1, column=col_idx).comment = Comment(help_text, "Codex")

    status_col_idx = field_to_col.get("review_status")
    if status_col_idx:
        status_col = sheet.cell(row=1, column=status_col_idx).column_letter
        sheet.conditional_formatting.add(
            f"A3:{sheet.cell(row=3, column=len(headers)).column_letter}{max_row}",
            FormulaRule(
                formula=[f'LEFT(${status_col}3,7)="labeled"'],
                fill=PatternFill("solid", fgColor="E9F7EF"),
            ),
        )
        sheet.conditional_formatting.add(
            f"A3:{sheet.cell(row=3, column=len(headers)).column_letter}{max_row}",
            FormulaRule(
                formula=[f'LEFT(${status_col}3,16)="needs_discussion"'],
                fill=PatternFill("solid", fgColor="FFF1CC"),
            ),
        )

    workbook["下拉选项"].sheet_state = "hidden"
    output_xlsx.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_xlsx)
    return len(rows)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Chinese coach response-review XLSX workbook.")
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT_CSV)
    parser.add_argument("--output-xlsx", type=Path, default=DEFAULT_OUTPUT_XLSX)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    row_count = export_xlsx(input_csv=args.input_csv, output_xlsx=args.output_xlsx)
    print(json.dumps({"output_xlsx": str(args.output_xlsx), "row_count": row_count}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
