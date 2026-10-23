import sys
sys.path.insert(0, '..')
from hwpx import ptext
def plain(d):
    return ptext(d).replace('\u27e6', '').replace('11\u27e7', '')
