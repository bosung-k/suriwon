import sys, kc_spec_t, kc_spec_c
from kc_ans import DROP
for kind, spec, nmax in (('T', kc_spec_t.T, 29), ('C', kc_spec_c.C, 33)):
    n = 0; out = []
    for p in range(1, nmax + 1):
        n += 1; out.append('%d=P%d' % (n, p))
        for it in [i for i in spec.get(p, []) if i['k'] not in DROP]:
            n += 1; out.append('%d=%s(P%d)' % (n, it['k'], p))
    print(kind, n, ' '.join(out))
