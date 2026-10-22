"""세화고 1학년 기말 대비 교재 생성 (수리원 HWPX 양식 + content/s*.py).

Usage: python gen_seh.py student <out.hwpx>   # 학생용 본문 + 빠른 정답 + 미주 해설
       python gen_seh.py teacher <out.hwpx>   # 강사용 대응표·발상 묶음·검수 기록
content/sN.py : S = {'no','title','bundles': [(학습 제목, [문항 dict, ...]), ...]}
문항 dict : id, src, role, idea, q, cond, bogi, choices, img, imgw, full, ans, sol, (변형) rule, step, keep, change
"""
import sys, os, copy, zipfile, importlib.util, glob, shutil
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen
import gen_sc
from gen import E, para, table, grid_table, load_tpl, set_texts, section_header, ns, HP

SCHOOL = '세화고'


def load_sessions(cdir):
    out = []
    for f in sorted(glob.glob(os.path.join(cdir, 's?.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        out.append(m.S)
    return out


def show_src(src):
    """학생용에는 학교 부교재·교과서·세화고 기출 원문만 출처를 보인다."""
    return src.startswith(('부교재', '교과서', '2025 기말')) and '변형' not in src and '유사' not in src


def number(sessions):
    n = 0
    for s in sessions:
        s['range'] = [n + 1, None]
        for bt, items in s['bundles']:
            for pr in items:
                n += 1
                pr['no'] = n
                pr['tag'] = ('%s   |   %s' % (bt, pr['src'])) if show_src(pr['src']) else bt
        s['range'][1] = n
    return n


def problem_page(parent, probs):
    para(parent, '', 23, 0, 6, pageBreak=1)
    p = E('p', {'id': 0, 'paraPrIDRef': 23, 'styleIDRef': 0, 'pageBreak': 0, 'columnBreak': 0, 'merged': 0}, parent)
    run = E('run', {'charPrIDRef': 9}, p)
    H = 81620
    t = table(run, len(probs), 3, 60360, H, 20)
    for i, pr in enumerate(probs):
        tr = E('tr', None, t)
        gen_sc.problem_cell(tr, i, H // len(probs), pr)
    E('t', None, run)


def package(sec, out, title_hpf, master_reps):
    tmp = out + '.dir'
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(gen.TPL, tmp)
    sec.write(os.path.join(tmp, 'Contents', 'section0.xml'), xml_declaration=True, encoding='UTF-8', standalone=True)
    for mp, rr in master_reps.items():
        f = os.path.join(tmp, 'Contents', mp)
        s = open(f, encoding='utf-8').read()
        for a, b in rr:
            s = s.replace(a, b)
        open(f, 'w', encoding='utf-8').write(s)
    f = os.path.join(tmp, 'Contents', 'content.hpf')
    s = open(f, encoding='utf-8').read().replace('공통수학2 III. 유리함수와 무리함수 50제', title_hpf)
    items = ''.join('<opf:item id="%s" href="BinData/%s.png" media-type="image/png" isEmbeded="1"/>' % (b, b) for b, _ in gen_sc._pics)
    s = s.replace('<opf:item id="section0"', items + '<opf:item id="section0"')
    open(f, 'w', encoding='utf-8').write(s)
    for b, pth in gen_sc._pics:
        shutil.copy(pth, os.path.join(tmp, 'BinData', b + '.png'))
    with zipfile.ZipFile(out, 'w') as z:
        z.write(os.path.join(tmp, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
        for dp, dn, fn in os.walk(tmp):
            for name in fn:
                full = os.path.join(dp, name)
                arc = os.path.relpath(full, tmp).replace('\\', '/')
                if arc != 'mimetype' and name != 'desktop.ini':
                    z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)


MASTER = {'masterpage0.xml': [('III. 유리함수와 무리함수', '공통수학2  집합 ~ 무리함수')],
          'masterpage1.xml': [('>03<', '>기말<'), ('유리함수와 무리함수', '세화고 1학년')]}


def cover(root, ps, sessions, sub):
    head_tpl, toc_tpl = ps[26], ps[18]
    keep, tail_cover = ps[:18], ps[21:26]
    for p in ps:
        root.remove(p)
    for p in keep:
        root.append(p)
    set_texts(keep[10], ['공통수학2'])
    set_texts(keep[11], ['집합 ~ 무리함수'])
    set_texts(keep[12], [sub])
    set_texts(keep[14], ['2026년 1학년 2학기 기말고사 대비'])
    for s in sessions:
        toc = copy.deepcopy(toc_tpl)
        set_texts(toc, ['%s   ' % s['no'], '%s     ' % s['title'], '%d – %d번' % tuple(s['range'])])
        root.append(toc)
    for p in tail_cover:
        root.append(p)
    return head_tpl


def build_student(out):
    sessions = load_sessions(os.path.join(HERE, 'content'))
    total = number(sessions)
    sec, root, ps = load_tpl()
    cover(root, ps, sessions, '%s 기말고사 대비 (%d제)' % (SCHOOL, total))

    para(root, [(21, '교재 구성')], 38, 11, 21, pageBreak=1)
    para(root, '(1) 시험 범위(집합 ~ 무리함수)를 교과서 단원 순서로 배열하고, 단원 안에서는 풀이 아이디어가 비슷한 문항끼리 묶었다.', 40, 12, 6)
    para(root, '(2) 각 묶음은 대표 문항 → 같은 아이디어의 확인 → 학교 시험형 응용 순서이다. 학교 부교재, 교과서, 세화고 기출 원문에는 문항 위에 출처를 적었다.', 40, 12, 6)
    rows = [['단원', '학습 묶음', '문항 번호']]
    for s in sessions:
        first = True
        for bt, items in s['bundles']:
            a, b = items[0]['no'], items[-1]['no']
            rows.append([('%s %s' % (s['no'], s['title'])) if first else '', bt, '%d ~ %d번' % (a, b) if a != b else '%d번' % a])
            first = False
    grid_table(root, rows, [13000, 33000, 13000])
    para(root, '(3) 출처 표기: ‘부교재’는 절대등급 공통수학2, ‘교과서’는 비상교육 공통수학2, ‘2025 기말’은 2025학년도 세화고 1학년 2학기 기말고사이다. 정답은 빠른 정답에, 풀이는 책의 맨 뒤(미주)에 있다.', 40, 12, 6)

    for s in sessions:
        probs = [pr for _, items in s['bundles'] for pr in items]
        i = 0
        while i < len(probs):
            if probs[i].get('full'):
                problem_page(root, probs[i:i + 1]); i += 1
                continue
            chunk = [probs[i]]
            if i + 1 < len(probs) and not probs[i + 1].get('full'):
                chunk.append(probs[i + 1])
            problem_page(root, chunk)
            i += len(chunk)

    para(root, [(21, '빠른 정답')], 38, 11, 21, pageBreak=1)
    allp = [pr for s in sessions for _, items in s['bundles'] for pr in items]
    rows = [['번호', '정답'] * 4]
    per = (len(allp) + 3) // 4
    for r in range(per):
        row = []
        for c in range(4):
            k = c * per + r
            if k < len(allp):
                row += [str(allp[k]['no']), allp[k].get('quick', allp[k]['ans'])]
            else:
                row += ['', '']
        rows.append(row)
    grid_table(root, rows, [3000, 11800] * 4)
    package(sec, out, '공통수학2 집합~무리함수 %s 기말 대비' % SCHOOL, MASTER)
    print('written', out, 'problems', total, 'endnotes', gen._en[0], 'pics', len(gen_sc._pics))


def build_teacher(out):
    sessions = load_sessions(os.path.join(HERE, 'content'))
    total = number(sessions)
    sec, root, ps = load_tpl()
    cover(root, ps, sessions, '%s 기말 대비 — 강사용 대응표' % SCHOOL)

    para(root, [(21, '강사용 안내')], 38, 11, 21, pageBreak=1)
    for ln in ['(1) 이 문서는 학생용 본문의 최종 번호와 고정 문항 ID·출처·발상 묶음·변형 규칙을 대응시킨 표이다. 학생에게 배포하지 않는다.',
               '(2) 변형 규칙 R1~R7의 정의와 근거 문항은 00_분석/세화고_기말대비_제작기록.md B-3절에 있다.',
               '(3) 상태: 검수 완료 초안(같은 모델의 재풀이와 계산 검산만 거침, 독립 검수자 검토 아님). 강사 승인 전.',
               '(4) 강사 표시가 있는 부교재가 제공되지 않아 강사 아이디어 반영 항목은 없다. 필기본을 받으면 C표를 채워 배치를 조정한다.']:
        para(root, ln, 40, 12, 6)

    for s in sessions:
        para(root, [(21, '%s %s  (%d ~ %d번)' % (s['no'], s['title'], s['range'][0], s['range'][1]))], 38, 11, 21, pageBreak=1)
        for bt, items in s['bundles']:
            para(root, [(21, '■ ' + bt)], 39, 11, 21)
            ideas = '; '.join('%d번 %s' % (pr['no'], pr.get('idea', '')) for pr in items if pr.get('role') in ('대표',))
            if ideas:
                para(root, '대표 문항의 결정적 발상: ' + ideas, 40, 12, 6)
            rows = [['번호', '문항 ID', '출처', '역할', '핵심 발상 / 변형 정보', '정답']]
            for pr in items:
                info = pr.get('idea', '')
                if pr.get('rule'):
                    info += '\n[%s · %s] 유지: %s / 변경: %s' % (pr['rule'], pr.get('step', ''), pr.get('keep', ''), pr.get('change', ''))
                rows.append([str(pr['no']), pr['id'], pr['src'], pr.get('role', ''), info, pr.get('quick', pr['ans'])])
            grid_table(root, rows, [3200, 7600, 9800, 5200, 25000, 9200])
    package(sec, out, '공통수학2 집합~무리함수 %s 기말 대비 강사용' % SCHOOL, MASTER)
    print('written', out, 'problems', total)


if __name__ == '__main__':
    gen_sc.FIGS = os.path.join(HERE, 'figs')
    if sys.argv[1] == 'student':
        build_student(sys.argv[2])
    else:
        # 강사용에는 미주를 만들지 않으므로 problem_cell을 쓰지 않는다.
        build_teacher(sys.argv[2])
