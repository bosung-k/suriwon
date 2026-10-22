"""conv.py src dst fmt [src dst fmt ...]  -- convert via Hancom COM (fmt: HWP, HWPX, PDF)"""
import sys, os
import win32com.client as win32

args = sys.argv[1:]
import win32com.client.dynamic
hwp = win32com.client.dynamic.Dispatch("HWPFrame.HwpObject")
print("register:", hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModuleExample"))
try:
    hwp.XHwpWindows.Item(0).Visible = False
except Exception as e:
    print("visible err", e)
try:
    for i in range(0, len(args), 3):
        src, dst, fmt = args[i], args[i + 1], args[i + 2]
        ok = hwp.Open(os.path.abspath(src), "", "forceopen:true")
        print("open", src, ok, "pages", hwp.PageCount)
        if fmt == "PDF":
            hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
            hwp.HParameterSet.HFileOpenSave.filename = os.path.abspath(dst)
            hwp.HParameterSet.HFileOpenSave.Format = "PDF"
            ok = hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
        else:
            ok = hwp.SaveAs(os.path.abspath(dst), fmt, "")
        print("save", dst, ok)
        hwp.Clear(1)
finally:
    hwp.Quit()
