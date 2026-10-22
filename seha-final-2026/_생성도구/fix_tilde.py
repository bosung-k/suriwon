import re, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
n = 0
for f in glob.glob(sys.argv[1] + '/content/s?.py'):
    t = open(f, encoding='utf-8').read()
    t2, k = re.subn(r'\$(-?\d+) ~ (-?\d+)\$', r'$\1$부터 $\2$까지', t)
    t2 = t2.replace("'imgw': 15000", "'imgw': 24000")
    n += k
    open(f, 'w', encoding='utf-8').write(t2)
print('replaced', n)
for f in glob.glob(sys.argv[1] + '/content/s?.py'):
    for ln in open(f, encoding='utf-8'):
        if re.search(r'\$[^$]* ~ [^$]*\$', ln) and 'LEFT' not in ln: print(f[-5:], ln.strip()[:120])
