import re, sys
from hx import *
from scan import top_paras, plain
f, o = read_hwpx(sys.argv[1])
x = f['Contents/section0.xml'].decode()
pr = top_paras(x)
a0, b0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 40
print(len(pr), pr[0][0])
for k, (a, b) in enumerate(pr[a0:b0], a0):
    s = x[a:b]; t = re.match(r'<hp:p [^>]*>', s).group(0)
    fl = [n for n, c in (('PB', 'pageBreak="1"' in t), ('CB', 'columnBreak="1"' in t), ('EN', 'endNote' in s), ('PIC', '<hp:pic' in s),
                         ('TBL', '<hp:tbl' in s), ('COLPR', 'colPr' in s), ('SECPR', 'secPr' in s), ('LINE', '<hp:line' in s)) if c]
    cps = re.findall(r'charPrIDRef="(\d+)"', s)[:4]
    print(k, re.search(r'paraPrIDRef="(\d+)"', t).group(1), cps, ' '.join(fl), len(s), repr(plain(s)[:70]))
