"""pgimg.py src outprefix -- render each page of an HWP to PNG via CreatePageImage (works for 배포용 docs?)"""
import sys, os
import win32com.client.dynamic
hwp = win32com.client.dynamic.Dispatch("HWPFrame.HwpObject")
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModuleExample")
try:
    hwp.XHwpWindows.Item(0).Visible = False
except Exception:
    pass
try:
    for i in range(1, len(sys.argv), 2):
        src, pre = sys.argv[i], sys.argv[i + 1]
        ok = hwp.Open(os.path.abspath(src), "", "forceopen:true")
        n = hwp.PageCount
        for p in range(n):
            fn = os.path.abspath('%s_p%02d.bmp' % (pre, p + 1))
            r = hwp.CreatePageImage(fn, p, 158, 24, "bmp")
            print(src, p + 1, r)
        hwp.Clear(1)
finally:
    hwp.Quit()
