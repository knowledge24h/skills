# -*- coding: utf-8 -*-
"""根据模板生成《系统需求规格说明书》docx。

用法:
    python gen_srs_docx.py <content.json> <output.docx> [template.docx]

- content.json: 结构化需求内容，schema 见 SKILL.md / references/template-structure.md
- template.docx 缺省使用脚本同级 ../assets/SRS模板.docx
- 仅依赖 Python 标准库（zipfile + xml.etree），在模板副本上填充，
  保留模板原有样式、页眉页脚与附录A信息定义。
- 生成后目录(TOC)为模板旧内容，需在 Word/WPS 中全选后按 F9 更新域。
"""
import copy
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'


def q(tag):
    return '{%s}%s' % (W, tag)


def register_namespaces(xml_text):
    for m in re.finditer(r'xmlns:([A-Za-z0-9_]+)="([^"]+)"', xml_text):
        ET.register_namespace(m.group(1), m.group(2))


def get_text(el):
    return ''.join(t.text or '' for t in el.iter(q('t')))


def get_style(p):
    pPr = p.find(q('pPr'))
    if pPr is not None:
        ps = pPr.find(q('pStyle'))
        if ps is not None:
            return ps.get(q('val'))
    return None


def set_par_text(p, text):
    """替换段落文本：保留 pPr 与首个 run 的 rPr，清空其余 run。text 中的换行忽略（一个段落一行）。"""
    proto_r = None
    for r in p.iter(q('r')):
        proto_r = copy.deepcopy(r)
        break
    for child in list(p):
        if child.tag in (q('r'), q('hyperlink'), q('fldSimple'), q('smartTag'), q('bookmarkStart'), q('bookmarkEnd')):
            p.remove(child)
    if proto_r is not None:
        r = proto_r
        for c in list(r):
            if c.tag != q('rPr'):
                r.remove(c)
        p.append(r)
    else:
        r = ET.SubElement(p, q('r'))
    t = ET.SubElement(r, q('t'))
    t.text = text
    t.set(XML_SPACE, 'preserve')


def set_cell(tc, text):
    """设置单元格文本，支持多行（每行一个段落，沿用首段样式）。"""
    text = '' if text is None else str(text)
    ps = tc.findall(q('p'))
    proto = copy.deepcopy(ps[0])
    for p in ps[1:]:
        tc.remove(p)
    lines = text.split('\n')
    set_par_text(ps[0], lines[0])
    for ln in lines[1:]:
        np = copy.deepcopy(proto)
        set_par_text(np, ln)
        tc.append(np)


def make_par(proto, text):
    p = copy.deepcopy(proto)
    set_par_text(p, text)
    return p


class SRSBuilder(object):
    def __init__(self, template_path):
        self.template_path = template_path
        with zipfile.ZipFile(template_path) as z:
            self.names = z.namelist()
            self.files = {n: z.read(n) for n in self.names}
        xml_text = self.files['word/document.xml'].decode('utf-8')
        register_namespaces(xml_text)
        self.root = ET.fromstring(xml_text)
        self.body = self.root.find(q('body'))
        self._collect_prototypes()

    # ---------- 模板原型采集 ----------
    def _collect_prototypes(self):
        children = list(self.body)
        self.h1 = self.h2 = self.h3 = self.p_body = None
        self.req_tbl = self.ref_tbl = self.term_tbl = self.log_tbl = None
        for i, ch in enumerate(children):
            if ch.tag == q('p'):
                s, t = get_style(ch), get_text(ch).strip()
                if s == '1' and self.h1 is None and t:
                    self.h1 = ch
                elif s == '2' and self.h2 is None and t:
                    self.h2 = ch
                elif s == '3' and self.h3 is None and t:
                    self.h3 = ch
                elif s == 'a7' and self.p_body is None and t.strip():
                    self.p_body = ch
            elif ch.tag == q('tbl'):
                rows = ch.findall(q('tr'))
                if not rows:
                    continue
                head = get_text(rows[0])
                if self.req_tbl is None and len(rows) == 12 and head.startswith('PRS_ID'):
                    self.req_tbl = ch
                elif self.ref_tbl is None and '序号' in head:
                    self.ref_tbl = ch
                elif self.term_tbl is None and '术语' in head:
                    self.term_tbl = ch
                elif self.log_tbl is None and 'Contents Revised' in head:
                    self.log_tbl = ch
        missing = [n for n, v in [('h1', self.h1), ('h2', self.h2), ('h3', self.h3),
                                  ('p_body', self.p_body), ('req_tbl', self.req_tbl),
                                  ('ref_tbl', self.ref_tbl), ('term_tbl', self.term_tbl),
                                  ('log_tbl', self.log_tbl)] if v is None]
        if missing:
            raise RuntimeError('模板中未找到原型元素: %s' % ', '.join(missing))

    # ---------- 定位 ----------
    def _find_range(self):
        start = end = None
        for i, ch in enumerate(self.body):
            if ch.tag == q('p'):
                s, t = get_style(ch), get_text(ch).strip()
                if start is None and s == '1' and t.startswith('引言'):
                    start = i
                elif s == '11' and t.startswith('附录A'):
                    end = i
                    break
        if start is None or end is None:
            raise RuntimeError('未定位到正文起始（1引言）或附录A')
        return start, end

    # ---------- 构件 ----------
    def heading(self, level, text):
        proto = {1: self.h1, 2: self.h2, 3: self.h3}[level]
        return make_par(proto, text)

    def para(self, text):
        out = []
        for ln in str(text).split('\n'):
            out.append(make_par(self.p_body, ln))
        return out

    def requirement_table(self, req):
        tbl = copy.deepcopy(self.req_tbl)
        rows = tbl.findall(q('tr'))
        mapping = [
            ('PRS_ID', req.get('prsId', '')),
            ('Type', req.get('type', 'Valid')),
            ('Description', req.get('description', '')),
            ('Upstream ID', req.get('upstreamId', '无')),
            ('Dependencies', req.get('dependencies', '无')),
            ('ASIL', req.get('asil', 'QM(A)')),
            ('Status', req.get('status', 'Draft')),
            ('Priority', req.get('priority', 'M')),
            ('Verification Criteria', req.get('verification', '无')),
            ('Risk', req.get('risk', '无')),
            ('Change Type', req.get('changeType', '新增')),
            ('CR', req.get('cr', '无')),
        ]
        assert len(mapping) == len(rows), '需求表行数不匹配'
        for row, (label, value) in zip(rows, mapping):
            tcs = row.findall(q('tc'))
            set_cell(tcs[1], value)
        return tbl

    def fill_3col_table(self, proto_tbl, data_rows):
        tbl = copy.deepcopy(proto_tbl)
        rows = tbl.findall(q('tr'))
        data_proto = copy.deepcopy(rows[1])
        for r in rows[1:]:
            tbl.remove(r)
        for vals in data_rows:
            tr = copy.deepcopy(data_proto)
            tcs = tr.findall(q('tc'))
            for j, v in enumerate(vals[:len(tcs)]):
                set_cell(tcs[j], v)
            tbl.append(tr)
        return tbl

    def fill_change_log(self, entries):
        tbl = copy.deepcopy(self.log_tbl)
        rows = tbl.findall(q('tr'))
        data_proto = copy.deepcopy(rows[1])
        for r in rows[1:]:
            tbl.remove(r)
        for e in entries:
            tr = copy.deepcopy(data_proto)
            tcs = tr.findall(q('tc'))
            vals = [e.get('no', ''), e.get('version', ''), e.get('content', ''),
                    e.get('status', 'Draft'), e.get('author', ''), e.get('date', '')]
            for j, v in enumerate(vals[:len(tcs)]):
                set_cell(tcs[j], v)
            tbl.append(tr)
        return tbl

    # ---------- 封面 ----------
    def update_cover(self, meta):
        replaces = {
            'Project Name': meta.get('projectName', ''),
            'Version：1.0.0': 'Version：%s' % meta.get('version', '1.0.0'),
            '2021-7-29': meta.get('date', ''),
            '(Division)': meta.get('division', '') or '(Division)',
        }
        for ch in self.body:
            if ch.tag != q('p'):
                continue
            t = get_text(ch).strip()
            if t in replaces and replaces[t]:
                set_par_text(ch, replaces[t])

    # ---------- 组装 ----------
    def build(self, content):
        self.update_cover(content.get('project', {}))
        if content.get('changeLog'):
            for idx, ch in enumerate(list(self.body)):
                if ch.tag == q('tbl'):
                    rows = ch.findall(q('tr'))
                    if rows and 'Contents Revised' in get_text(rows[0]):
                        new_tbl = self.fill_change_log(content['changeLog'])
                        self.body.remove(ch)
                        self.body.insert(idx, new_tbl)
                        break

        start, end = self._find_range()
        for ch in list(self.body)[start:end]:
            self.body.remove(ch)

        new_elements = []
        intro = content.get('intro', {})
        new_elements.append(self.heading(1, '引言（Introduction）'))
        new_elements.append(self.heading(2, '目的（Goal）'))
        new_elements.extend(self.para(intro.get('purpose', '无')))
        new_elements.append(self.heading(2, '范围（Scope）'))
        new_elements.extend(self.para(intro.get('scope', '无')))
        new_elements.append(self.heading(2, '参考文档（Reference）'))
        new_elements.extend(self.para(intro.get('referenceNote', '无')))
        refs = intro.get('references') or [['1', '无', '无']]
        new_elements.append(self.fill_3col_table(self.ref_tbl, refs))
        new_elements.append(self.heading(2, '术语及缩略语（Terms And Abbreviations）'))
        new_elements.extend(self.para(intro.get('termsNote', '无')))
        terms = intro.get('terms') or [['无', '无', '无']]
        new_elements.append(self.fill_3col_table(self.term_tbl, terms))

        ov = content.get('overview', {})
        new_elements.append(self.heading(1, '软件系统概述（Software System Overview）'))
        new_elements.append(self.heading(2, '软件系统背景（Software System Background）'))
        new_elements.extend(self.para(ov.get('background', '无')))
        new_elements.append(self.heading(2, '软件系统目标（Software System Goal）'))
        new_elements.extend(self.para(ov.get('goal', '无')))
        new_elements.append(self.heading(2, '外部关联（External Association）'))
        new_elements.extend(self.para(ov.get('external', '无')))

        new_elements.append(self.heading(1, '功能需求（Functional Requirement）'))
        for group in content.get('functional', []):
            new_elements.append(self.heading(2, group['title']))
            if group.get('desc'):
                new_elements.extend(self.para(group['desc']))
            for req in group.get('requirements', []):
                new_elements.append(self.heading(3, req['title']))
                new_elements.append(self.requirement_table(req))

        nf = content.get('nonFunctional', {})
        new_elements.append(self.heading(1, '非功能需求(Non-Functional Requirements)'))
        for sub_title, key in [('制约（Constraint）', 'constraints'),
                               ('性能（Performance）', 'performance')]:
            sec = nf.get(key, {})
            new_elements.append(self.heading(2, sub_title))
            if sec.get('desc'):
                new_elements.extend(self.para(sec['desc']))
            for req in sec.get('requirements', []):
                new_elements.append(self.heading(3, req['title']))
                new_elements.append(self.requirement_table(req))

        pos = start
        for el in new_elements:
            self.body.insert(pos, el)
            pos += 1

    def save(self, out_path):
        doc_xml = ET.tostring(self.root, encoding='UTF-8', xml_declaration=True)
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for n in self.names:
                if n == 'word/document.xml':
                    z.writestr(n, doc_xml)
                else:
                    z.writestr(n, self.files[n])


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    content_path, out_path = sys.argv[1], sys.argv[2]
    template = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'SRS模板.docx')
    with open(content_path, 'r', encoding='utf-8-sig') as f:
        content = json.load(f)
    builder = SRSBuilder(template)
    builder.build(content)
    builder.save(out_path)
    print('OK ->', out_path)


if __name__ == '__main__':
    main()
