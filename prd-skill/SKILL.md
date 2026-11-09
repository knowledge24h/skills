---
name: prd-skill
description: 需求分析技能。当用户需要做需求分析、编写《系统需求规格说明书》（SRS）、整理《系统需求列表》、把客户需求/调研材料拆解为功能需求与非功能需求条目时使用。基于标准模板产出两份成果物：一份《系统需求规格说明书》docx 和一份《系统需求列表》xlsx，格式与官方模板完全一致。
agent_created: true
---

# 需求分析技能（prd-skill）

基于 `assets/` 下的官方模板，完成需求分析并生成两份成果物：

1. **《系统需求规格说明书》.docx** —— 按模板章节（引言/系统概述/功能需求/非功能需求）填充
2. **《系统需求列表》.xlsx** —— 变更履历 + 需求List 两个 sheet，与 SRS 内容一一对应

模板细节、字段规范、PRS_ID 编号规则与 content.json schema 见 `references/template-structure.md`（生成内容前必读）。

## 工作流程

### 1. 收集与澄清输入

可接受的输入：用户口述、会议纪要、已有文档（docx/md/txt）、竞品资料等。

- 输入信息不足时，先向用户澄清关键缺口（系统目标、主要功能点、运行环境、约束），**不得虚构需求**；确实无法确认的字段填 TBD 并在交付说明中列出让用户确认。
- 用户提供了参考文件时先读取再分析。

### 2. 需求分析与整理

- 把输入拆解为：功能需求（按功能分组）+ 非功能需求（制约 Constraint / 性能 Performance）。
- 每条需求按 12 字段结构化（PRS_ID / Type / Description / Upstream ID / Dependencies / ASIL / Status / Priority / Verification Criteria / Risk / Change Type / CR）。
- 按 PRS_ID 规则编号：`PRS_{类型}_{功能简称}_{5位流水号}`；非功能需求类型为 NF。功能简称需与用户确认或按系统域合理命名。
- Description 写作规范：判断逻辑必须写明条件满足与不满足两个分支（"当…时，判断…；否则，…"）；取值范围用 ()[] >= <= 符号描述。
- 优先级：被依赖的需求设 H，核心流程 M 或 H，其余 L。
- 非汽车电子类项目 ASIL 统一填 QM(A)。

### 3. 编写 content.json

按 `references/template-structure.md` 中的 schema 编写完整内容文件（建议写到临时目录，如 `<系统临时目录>/prd-skill/content.json`）。要求：

- intro（目的/范围/参考文档/术语）、overview（背景/目标/外部关联）用简洁的正式书面语，不得保留模板占位符文字。
- 每条需求的 description 独立成句，可验证、无歧义。
- changeLog 首条固定为：`{"no":1,"version":"0.1","content":"新做成","author":"","date":"<当天日期>"}`。

### 4. 生成成果物

两个脚本只依赖 Python 标准库，用受管 Python 运行：

```bash
python <skill目录>/scripts/gen_srs_docx.py      <content.json> <输出目录>/系统需求规格说明书.docx
python <skill目录>/scripts/gen_req_list_xlsx.py <content.json> <输出目录>/系统需求列表.xlsx
```

- 生成到用户当前工作目录（或用户指定目录），不要留在临时目录。
- 文件名可按项目命名，如《XX系统需求规格说明书.docx》《XX系统需求列表.xlsx》。

### 5. 校验与交付

- 用脚本或读取工具复查生成的 docx：章节标题齐全、需求表 12 行都已填充、封面项目名/版本/日期已替换、附录A 完整保留。
- 复查 xlsx：需求List 行数 = SRS 需求条目总数，ID 一一对应。
- **提示用户**：docx 的目录是模板旧内容，需在 Word/WPS 中打开后 `Ctrl+A` → `F9`（或右键→更新域）刷新目录和页码。
- 用 present_files 交付两份文件，并简要列出需求条目数、分组情况和待用户确认的 TBD 项。

## 注意事项

- 模板 docx 使用真实 TOC 域与多级编号样式，脚本仅替换正文与封面，勿改动模板结构本身。
- xlsx 模板单元格使用共享字符串（sharedStrings），修改模板逻辑时注意解析 `t="s"` 单元格。
- xlsx 模板表头下方预置了大量带格式的空白行：生成脚本会把需求行填到表头正下方并复用这些空白行的样式（边框/字体），禁止简单地在文件末尾 append（会导致数据与表头隔开几十行且无格式）。数据列按表头行中有文字的单元格定位（变更履历数据从 C 列开始）。
- 需求List 的「一级功能」列必须填 SRS 功能分组的中文标题（去掉括号内英文），不能填英文简称。
- 两份成果物必须保持一致：SRS 中每条需求都要出现在需求列表中，PRS_ID 完全相同。
