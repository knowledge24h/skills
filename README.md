# skills

> 汇集好用的 AI Agent Skill，也记录我自己创作 Skill 的过程与成果。
>
> GitHub：[knowledge24h/skills](https://github.com/knowledge24h/skills.git)
> 账号：[knowledge24h](https://github.com/knowledge24h)

## 仓库简介

本仓库围绕 **Skill（技能）** 展开，主要做两件事：

1. **推荐好的 Skill**：整理 GitHub 及社区中高质量、实用性强的 Skill，按场景分类，方便按需取用。
2. **创作自己的 Skill**：把日常重复的工作流程、专业经验沉淀为可复用的 Skill，并在此持续更新。

适合人群：使用 AI Agent 提效的开发者、工程师，以及想把个人经验固化成技能的创作者。

## 目录结构

```text
skills/
├── README.md              # 仓库说明与 Skill 推荐清单
├── recommended/           # 社区优质 Skill 推荐与点评
├── custom/                 # 自己创作的 Skill
└── references/            # Skill 编写规范、模板与参考资料
```

## 一、Skill 推荐

### GitHub 全球热门 Skill Top 10

按仓库 Star 降序整理，仅供选型参考；具体数据请以 GitHub 实际仓库为准。

| 排名 | Skill 名称 | 功能说明 | Star 数 |
|:---:|---|---|---:|
| 01 | karpaty-guidelines | 澄清编程需求，让代码改动更有边界 | 217.8k |
| 02 | pony tail | 复用现有代码，用更少改动完成需求 | 159.9k |
| 03 | ui-ux-pro-max | 把配色、字体与布局整理成统一方案 | 134.3k |
| 04 | graphify | 把代码与文档连成可查询知识图谱 | 125.1k |
| 05 | archify | 将想法与代码库转成交互图页面 | 81.3k |
| 06 | impeccable | 从排版到交互，逐项打磨产品界面 | 79.1k |
| 07 | i-have-adhd | 先说结论与行动，降低阅读负担 | 56.2k |
| 08 | humanizer | 删去套话和重复，让文字具体自然 | 55.3k |
| 09 | diagram-design | 把流程与关系画成风格统一的图表 | 48.2k |
| 10 | book-to-skill | 提炼书籍与文档，生成可复用技能 | 34.3k |

### 按场景分类

| 场景方向 | 推荐 Skill | 适用说明 |
|---|---|---|
| 需求与代码边界 | karpaty-guidelines | 先澄清需求，再限定改动范围，避免需求蔓延 |
| 代码复用 | pony tail | 优先复用现有实现，以最小改动完成需求 |
| 界面与设计 | ui-ux-pro-max、impeccable | 统一配色字体布局，逐项打磨排版与交互 |
| 知识与架构 | graphify、archify | 代码文档图谱化，想法转交互页面 |
| 阅读与表达 | i-have-adhd、humanizer | 结论先行、去套话，降低阅读负担 |
| 图表可视化 | diagram-design | 流程、关系图风格统一出图 |
| 经验沉淀 | book-to-skill | 从书籍、文档中提炼可复用技能 |

## 二、自定义 Skill

> 以下为本人原创 Skill，持续补充中。

| Skill 名称 | 功能说明 | 状态 |
|---|---|---|
| _待补充_ | 把日常工作流程沉淀为可复用技能 | 规划中 |

## 三、Skill 创作规范

一个标准 Skill 由以下部分组成：

```text
skill-name/
├── SKILL.md               # 必需：技能说明（元信息 + 使用流程）
├── scripts/               # 可选：可执行脚本
├── references/            # 可选：参考文档、规范、模板
└── assets/                # 可选：输出用模板、图标、字体等资源
```

### SKILL.md 基本要求

- 顶部 YAML 元信息必须包含 `name` 和 `description`；`description` 写清技能用途与触发场景。
- 正文只保留必要流程与示例，保持精简；细节内容拆到 `references/`。
- 脚本用于确定性、可重复执行的逻辑；参考资料按需加载，避免占用上下文。

### 创作流程

1. 明确使用场景与典型示例，判断哪些流程会重复发生。
2. 规划可复用内容：脚本、参考文档、模板资源。
3. 初始化 Skill 目录并编写 `SKILL.md`。
4. 补充脚本与资源，实际运行测试。
5. 在真实任务中迭代优化。

## 四、快速开始

### 克隆仓库

```bash
git clone https://github.com/knowledge24h/skills.git
cd skills
```

### 使用推荐 Skill

进入对应 Skill 目录，阅读其 `SKILL.md`，按说明加载到你的 AI Agent 环境中使用。

### 提交自定义 Skill

1. 在 `custom/` 下新建 Skill 目录。
2. 编写 `SKILL.md` 及配套资源。
3. 本地测试通过后提交并推送。

## 五、更新计划

- [ ] 持续补充社区优质 Skill 推荐与点评
- [ ] 沉淀工程、写作、电商等方向的原创 Skill
- [ ] 完善 Skill 模板与编写参考资料

## 许可证

本仓库内容仅供学习与参考使用；第三方 Skill 的版权与许可证以其原始仓库为准。

## 联系方式

- GitHub：[knowledge24h](https://github.com/knowledge24h)
- 仓库地址：<https://github.com/knowledge24h/skills.git>
