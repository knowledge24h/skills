# -*- coding: utf-8 -*-
"""根据模板生成《系统需求列表》xlsx。

用法:
    python gen_req_list_xlsx.py <content.json> <output.xlsx> [template.xlsx]

- content.json: 与 gen_srs_docx.py 相同的内容文件，本脚本自动抽取：
    * 变更履历 sheet <- changeLog
    * 需求List sheet <- functional/constraints/performance 中所有需求
  也可以直接传 {"changeLog":[...], "reqList":[...]} 自定义。
- template.xlsx 缺省使用脚本同级 ../assets/系统需求列表模板.xlsx
- 仅依赖 Python 标准库；在模板副本上追加行，保留原有格式。
"""
import copy
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


def q(tag):
    return '{%s}%s' % (NS, tag)


def col_letter(idx):
    s = ''
    while idx > 0:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def register_namespaces(xml_text):
    for m in re.finditer(r'xmlns:([A-Za-z0-9_]+)="([^"]+)"', xml_text):
        ET.register_namespace(m.group(1), m.group(2))


def cell_text(c, shared=None):
    t = c.get('t')
    if t == 'inlineStr':
        is_el = c.find(q('is'))
        if is_el is not None:
            return ''.join(x.text or '' for x in is_el.iter(q('t')))
    v = c.find(q('v'))
    if v is None or v.text is None:
        return ''
    if t == 's' and shared is not None:
        try:
            return shared[int(v.text)]
        except (ValueError, IndexError):
            return ''
    return v.text


def row_text(row, shared=None):
    return ' '.join(cell_text(c, shared) for c in row.iter(q('c')))


def make_cell(col_idx, row_num, text):
    c = ET.Element(q('c'))
    c.set('r', '%s%d' % (col_letter(col_idx), row_num))
    c.set('t', 'inlineStr')
    is_el = ET.SubElement(c, q('is'))
    t = ET.SubElement(is_el, q('t'))
    t.text = '' if text is None else str(text)
    return c


def append_rows(sheet_root, rows_data, start_col=1):
    """在 sheet 末尾追加行（按现有最大行号续）。rows_data: list[list[str]]"""
    sheet_data = sheet_root.find(q('sheetData'))
    max_row = 0
    for row in sheet_data.findall(q('row')):
        try:
            max_row = max(max_row, int(row.get('r', '0')))
        except ValueError:
            pass
    r = max_row
    for vals in rows_data:
        r += 1
        row = ET.SubElement(sheet_data, q('row'))
        row.set('r', str(r))
        for j, v in enumerate(vals):
            row.append(make_cell(start_col + j, r, v))
    return r


def fill_after_header(sheet_root, shared, header_text, rows_data, overwrite_example=False):
    """把数据填到表头正下方：复用模板已有空行的样式（边框等），
    覆盖表头之后的空白行区域；不足时按原型行样式新建。

    - header_text: 用于定位表头行的文本
    - overwrite_example: True 时以表头下第一个非空示例行作为样式原型并覆盖它
    """
    sheet_data = sheet_root.find(q('sheetData'))
    rows = list(sheet_data.findall(q('row')))
    header = None
    for row in rows:
        if header_text in row_text(row, shared):
            header = row
            break
    if header is None:
        raise RuntimeError('未找到表头行: %s' % header_text)
    hnum = int(header.get('r'))
    after = [r for r in rows if int(r.get('r', '0')) > hnum]

    # 数据目标列 = 表头行中有文字的单元格所在列（跳过行首的空样式格，如变更履历的A/B列）
    target_cols = []
    for c in header.findall(q('c')):
        if cell_text(c, shared).strip():
            m = re.match(r'([A-Z]+)', c.get('r') or '')
            if m:
                target_cols.append(m.group(1))

    # 样式原型行：优先取示例数据行（overwrite_example），否则取第一个带样式的空行
    proto = None
    if overwrite_example and after and row_text(after[0], shared).strip():
        proto = after[0]
    if proto is None:
        for r in after:
            if not row_text(r, shared).strip() and r.findall(q('c')):
                proto = r
                break
    if proto is None:
        proto = after[0] if after else header

    # 删除表头之后的所有行（本场景模板表头之后均为空白格式行/示例行）
    for r in after:
        sheet_data.remove(r)

    n_cols = max(len(target_cols), 1)
    rnum = hnum
    for vals in rows_data:
        rnum += 1
        new_row = copy.deepcopy(proto)
        new_row.set('r', str(rnum))
        col_val = {}
        for j in range(max(len(vals), n_cols)):
            if j < len(target_cols) and j < len(vals):
                col_val[target_cols[j]] = vals[j]
        for c in new_row.findall(q('c')):
            ref = c.get('r') or ''
            m = re.match(r'([A-Z]+)', ref)
            if not m:
                continue
            col = m.group(1)
            for child in list(c):
                c.remove(child)
            c.set('r', '%s%d' % (col, rnum))
            if col in col_val:
                c.set('t', 'inlineStr')
                is_el = ET.SubElement(c, q('is'))
                t = ET.SubElement(is_el, q('t'))
                t.text = '' if col_val[col] is None else str(col_val[col])
        # 数据列多于原型列时补空单元格
        existing = set(re.match(r'([A-Z]+)', c.get('r')).group(1) for c in new_row.findall(q('c')) if re.match(r'([A-Z]+)', c.get('r')))
        for j in range(len(target_cols), len(vals)):
            col = col_letter(j + 1)
            if col not in existing:
                new_row.append(make_cell(j + 1, rnum, vals[j]))
        sheet_data.append(new_row)
    return rnum


def cn_title(title):
    """取分组标题的中文部分（去掉括号内的英文），如 '用户与账户(User & Account)' -> '用户与账户'"""
    return re.split(r'[(（]', str(title))[0].strip()


def extract_from_srs_content(content):
    """从 SRS 内容 JSON 抽取需求列表行。"""
    rows = []
    for group in content.get('functional', []):
        fn = cn_title(group['title'])
        for req in group.get('requirements', []):
            rows.append(req_to_row(req, fn, '功能需求'))
    nf = content.get('nonFunctional', {})
    for key, label in [('constraints', '非功能需求-制约'), ('performance', '非功能需求-性能')]:
        for req in nf.get(key, {}).get('requirements', []):
            rows.append(req_to_row(req, label, '非功能需求'))
    return rows


def req_to_row(req, function, nf_label):
        pr = {'H': '高', 'M': '中', 'L': '低'}.get(req.get('priority', ''), req.get('priority', '中'))
        return [
            req.get('upstreamId', '') if req.get('upstreamId', '无') != '无' else '',
            req.get('prsId', ''),
            function,
            req.get('description', ''),
            req.get('envImpact', ''),
            pr,
            req.get('verifiable', '是'),
            '',
            req.get('cr', '') if req.get('cr', '无') != '无' else '',
            nf_label,
        ]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    content_path, out_path = sys.argv[1], sys.argv[2]
    template = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'assets', '系统需求列表模板.xlsx')
    with open(content_path, 'r', encoding='utf-8-sig') as f:
        content = json.load(f)

    if 'reqList' in content:
        req_rows = content['reqList']
        change_log = content.get('changeLog', [])
    else:
        req_rows = extract_from_srs_content(content)
        change_log = content.get('changeLog', [])

    with zipfile.ZipFile(template) as z:
        names = z.namelist()
        files = {n: z.read(n) for n in names}

    # --- 解析共享字符串 ---
    shared = []
    if 'xl/sharedStrings.xml' in files:
        sst = ET.fromstring(files['xl/sharedStrings.xml'])
        for si in sst.findall(q('si')):
            shared.append(''.join(t.text or '' for t in si.iter(q('t'))))

    # --- 变更履历 sheet ---
    for n in names:
        if not re.match(r'xl/worksheets/sheet\d+\.xml$', n):
            continue
        xml_text = files[n].decode('utf-8')
        register_namespaces(xml_text)
        root = ET.fromstring(xml_text)
        text_all = ' '.join(row_text(r, shared) for r in root.iter(q('row')))
        if '变更履历' in text_all:
            rows = [[e.get('no', ''), e.get('version', ''), e.get('content', ''),
                     e.get('author', ''), e.get('date', '')] for e in change_log]
            if rows:
                fill_after_header(root, shared, '修改条款及内容', rows, overwrite_example=True)
            files[n] = ET.tostring(root, encoding='UTF-8', xml_declaration=True)
        elif '客户/系统需求ID' in text_all or '需求List' in text_all:
            if req_rows:
                fill_after_header(root, shared, '客户/系统需求ID', req_rows)
            files[n] = ET.tostring(root, encoding='UTF-8', xml_declaration=True)

    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.writestr(n, files[n])
    print('OK ->', out_path, '| 需求行数:', len(req_rows))


if __name__ == '__main__':
    main()
