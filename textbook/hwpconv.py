"""Convert with Hangul COM: python hwpconv.py src dst FORMAT  (FORMAT: HWP, HWPX, PDF)"""
import sys, os
import win32com.client as win32

src, dst, fmt = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
hwp = win32.dynamic.Dispatch('HWPFrame.HwpObject')
try:
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
except Exception as e:
    print('register failed', e)
hwp.XHwpWindows.Item(0).Visible = False
ok = hwp.Open(src, '', 'forceopen:true')
print('open', ok)
ok = hwp.SaveAs(dst, fmt, '')
print('save', ok)
hwp.Clear(1)
hwp.Quit()

