# 模板结构与字段规范

本 skill 的两份成果物均基于 `assets/` 下的官方模板生成，生成脚本会保留模板原有样式、页眉页脚与附录。

## 一、《系统需求规格说明书》结构（assets/SRS模板.docx）

```
封面（项目名 / Version / 日期 / 部门）
变更履历表（No. | Version | Contents Revised | Status | Reviser/Date | Approve/Date）
文档状态说明表（Draft/In Review/Approved/Released/Modified）
目录（TOC 域，生成后需在 Word/WPS 中 F9 更新）
1 引言（Introduction）
  1.1 目的（Goal）          —— 文档编写目的
  1.2 范围（Scope）         —— 使用者与使用方法
  1.3 参考文档（Reference）  —— 三列表格：序号 | 文档名 | 版本名
  1.4 术语及缩略语          —— 三列表格：术语 | Term/Abbreviation | 描述
2 系统概述（Software System Overview）
  2.1 软件系统背景（Background）
  2.2 软件系统目标（Goal）   —— 开发范围、模块框图职责
  2.3 外部关联（External Association）
3 功能需求（Functional Requirement）
  3.x 功能需求分组（h2）
    3.x.y 需求条目（h3）+ 12 行字段表
4 非功能需求(Non-Functional Requirements)
  4.1 制约（Constraint）    —— 运行环境/接口/硬件/法规/交付/配置数据等
  4.2 性能（Performance）   —— 可用性/效率/可维护性/可移植性/可扩展性/性能
附录A- 信息定义（模板自带，无需改动）
```

### 需求条目字段表（12 行，顺序固定）

| 字段 | 说明 | 缺省值 |
|---|---|---|
| PRS_ID | 需求编号，规则见下 | 必填 |
| Type | Valid / InValid / TBD | Valid |
| Description | 需求描述。判断逻辑必须写明条件满足/不满足两个分支；取值范围用 ()[] >= <= 描述，禁用"大于"等口语 | 必填 |
| Upstream ID | 上游相关方需求 ID（如客户需求/CR号） | 无 |
| Dependencies | 依赖的其它需求 ID | 无 |
| ASIL | 功能安全等级，见附录A（QM(A)~ASIL D） | QM(A) |
| Status | Draft → In Review → Approved → Released；变更后为 Modified | Draft |
| Priority | H / M / L | M |
| Verification Criteria | 验证方法/验证环境/前提条件/主要测试点/成功标准，无内容填"无"，不得删行 | 无 |
| Risk | 技术之外还需考虑质量、成本、进度风险，无则填"无" | 无 |
| Change Type | 新增 / 修改 / 删除 / 不变 | 新增 |
| CR | 需求变更对应的 CR 号 | 无 |

### PRS_ID 编号规则（附录A）

```
PRS_{需求类型}_{功能简称}_流水号
- 需求类型：功能需求为空，非功能需求为 NF，接口为 API
- 功能简称：项目自定义的小写英文简称（如 volt、comm），需在文档中保持一致
- 流水号：从 00001 起的 5 位数字
例：PRS_volt_00001、PRS_NF_volt_00001、PRS_API_volt_00001
```

## 二、《系统需求列表》结构（assets/系统需求列表模板.xlsx）

| Sheet | 列 |
|---|---|
| 变更履历 | 编号 | 版本 | 修改条款及内容 | 修改人 | 修改日期（数据从 C 列开始） |
| 需求List | 客户/系统需求ID | 软件需求ID | 一级功能 | 需求描述 | 对运行环境的影响 | 优先级（高/中/低） | 可验证性 | QlistID | 变更编号 | 备注 |

映射关系：
- `软件需求ID` = SRS 中的 PRS_ID
- `客户/系统需求ID` = SRS 中的 Upstream ID（非"无"时）
- `优先级`：H/M/L → 高/中/低
- `可验证性`：填「是/否」（详细验证方法只写在 SRS 的 Verification Criteria 中）
- `一级功能`：所属功能分组标题（建议在分组 JSON 中提供 `shortName` 简称）

## 三、content.json schema（两个脚本共用）

```jsonc
{
  "project": { "projectName": "", "version": "1.0.0", "date": "YYYY-MM-DD", "division": "" },
  "changeLog": [ { "no": 1, "version": "0.1", "content": "新做成", "author": "", "date": "" } ],
  "intro": {
    "purpose": "", "scope": "",
    "referenceNote": "", "references": [["1", "文档名", "V1.0"]],
    "termsNote": "", "terms": [["术语", "EN", "描述"]]
  },
  "overview": { "background": "", "goal": "", "external": "" },
  "functional": [
    {
      "title": "功能需求分组标题",
      "shortName": "用于需求列表一级功能的简称",
      "desc": "分组整体描述（可省略）",
      "requirements": [ { /* 需求条目 */ } ]
    }
  ],
  "nonFunctional": {
    "constraints":  { "desc": "", "requirements": [ /* 需求条目 */ ] },
    "performance":  { "desc": "", "requirements": [ /* 需求条目 */ ] }
  }
}
```

需求条目字段（均可在 requirements 数组元素中提供）：

```jsonc
{
  "title": "需求条目标题（编号由模板样式自动生成）",
  "prsId": "PRS_xxx_00001",
  "type": "Valid",
  "description": "支持\\n换行",
  "upstreamId": "无",
  "dependencies": "无",
  "asil": "QM(A)",
  "status": "Draft",
  "priority": "H",
  "verification": "验证方法：…\\n验证环境：…",
  "risk": "无",
  "changeType": "新增",
  "cr": "无",
  "verifiable": "是",       // 仅用于需求列表
  "envImpact": ""           // 仅用于需求列表：对运行环境的影响
}
```
