# -*- coding: utf-8 -*-
"""Edit ONLY print 5 figure and print 14 (figure + text) in the user's 원 file."""
import re, itertools
from xml.sax.saxutils import escape
from PIL import Image
from hx import *
from scan import top_paras, plain

f, o = read_hwpx(r'work\u\C_user.hwpx'); x = f['Contents/section0.xml'].decode()
pr = top_paras(x)
para = lambda k: x[pr[k][0]:pr[k][1]]
k5 = next(i for i, (a, b) in enumerate(pr) if '원주각 5번]' in plain(x[a:b]))
k14 = next(i for i, (a, b) in enumerate(pr) if '원주각 14번]' in plain(x[a:b]))
assert 'image11' in para(k5 + 2) and 'image37' in para(k14 + 2) and '내접원이다.' in plain(para(k14 + 1))


def repic(s, iid, path, keep_height=True):
    m = re.search(r'<hp:pic [^>]*>.*?binaryItemIDRef="%s".*?</hp:pic>' % iid, s, re.S)
    pic = m.group(0)
    w, h = Image.open(path).size
    cw0, ch0 = map(int, re.search(r'<hp:curSz width="(\d+)" height="(\d+)"', pic).groups())
    ch = ch0; cw = int(round(ch0 * w / h))
    ow, oh = w * 75, h * 75
    p = re.sub(r'<hp:orgSz width="\d+" height="\d+"/>', '<hp:orgSz width="%d" height="%d"/>' % (ow, oh), pic)
    p = re.sub(r'<hp:curSz width="\d+" height="\d+"/>', '<hp:curSz width="%d" height="%d"/>' % (cw, ch), p)
    p = re.sub(r'centerX="\d+" centerY="\d+"', 'centerX="%d" centerY="%d"' % (cw // 2, ch // 2), p)
    p = re.sub(r'<hc:scaMatrix e1="[\d.]+" e2="0" e3="0" e4="0" e5="[\d.]+" e6="0"/>',
               '<hc:scaMatrix e1="%.6f" e2="0" e3="0" e4="0" e5="%.6f" e6="0"/>' % (cw / ow, ch / oh), p)
    p = re.sub(r'<hp:imgRect>.*?</hp:imgRect>', '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/></hp:imgRect>' % (ow, ow, oh, oh), p, flags=re.S)
    p = re.sub(r'<hp:imgClip left="\d+" right="\d+" top="\d+" bottom="\d+"/>', '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/>' % (ow, oh), p)
    p = re.sub(r'<hp:imgDim dimwidth="\d+" dimheight="\d+"/>', '<hp:imgDim dimwidth="%d" dimheight="%d"/>' % (ow, oh), p)
    p = re.sub(r'<hp:sz width="\d+" widthRelTo="ABSOLUTE" height="\d+"', '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d"' % (cw, ch), p)
    f['BinData/%s.png' % iid] = open(path, 'rb').read()
    print(iid, (cw0, ch0), '->', (cw, ch))
    return s.replace(pic, p)


new = {}
new[k5 + 2] = repic(para(k5 + 2), 'image11', r'work\pr\C_img\p05_fixed.png')
new[k14 + 2] = repic(para(k14 + 2), 'image37', r'work\pr\C_img\p14_fixed.png')

# text: insert side lengths after '내접원이다. '
s = para(k14 + 1)
tmpl = re.search(r'<hp:equation .*?</hp:equation>', s, re.S).group(0)
ids = itertools.count(1970000001); zs = itertools.count(5000)


def eq(script):
    e = re.sub(r'<hp:script>.*?</hp:script>', '<hp:script>%s</hp:script>' % escape(script), tmpl, flags=re.S)
    e = re.sub(r'<hp:equation id="\d+" zOrder="\d+"', lambda m: '<hp:equation id="%d" zOrder="%d"' % (next(ids), next(zs)), e)
    vis = re.sub(r'\b(rm|overline)\b|[{}~` ]', '', script)
    e = re.sub(r'<hp:sz width="\d+"', '<hp:sz width="%d"' % (560 * len(vis)), e, count=1)
    return e


ins = (eq('overline {rm A B} =8 rm cm') + '<hp:t>, </hp:t>' + eq('overline {rm B C} =10 rm cm') + '<hp:t>, </hp:t>' +
       eq('overline {rm C A} =7 rm cm') + '<hp:t>이고 </hp:t>')
m = re.search(r'(<hp:t>[^<]*내접원이다\. ?)([^<]*</hp:t>)', s)
assert m, 'text not found'
head, tail = m.group(1), m.group(2)
if not head.endswith(' '):
    head += ' '
s2 = s[:m.start()] + head + '</hp:t>' + ins + '<hp:t>' + tail + s[m.end():]
s2 = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', s2, flags=re.S)
new[k14 + 1] = s2
for k in new:
    new[k] = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', new[k], flags=re.S)

out = []; last = 0
for k in sorted(new):
    a, b = pr[k]; out.append(x[last:a]); out.append(new[k]); last = b
out.append(x[last:])
f['Contents/section0.xml'] = ''.join(out).encode('utf-8')
write_hwpx(r'work\u\C_fixed.hwpx', f, o)
print(plain(s2)[:200])
