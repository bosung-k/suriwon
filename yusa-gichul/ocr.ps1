param([string]$ListFile, [string]$OutDir)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$lang = [Windows.Globalization.Language]::new('ko')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
foreach ($path in Get-Content $ListFile -Encoding UTF8) {
    $name = [IO.Path]::GetFileNameWithoutExtension($path)
    $out = Join-Path $OutDir ($name + '.json')
    if (Test-Path $out) { continue }
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
    $lines = @()
    foreach ($l in $res.Lines) {
        $xs = $l.Words | % { $_.BoundingRect.X }; $ys = $l.Words | % { $_.BoundingRect.Y }
        $x2 = $l.Words | % { $_.BoundingRect.X + $_.BoundingRect.Width }; $y2 = $l.Words | % { $_.BoundingRect.Y + $_.BoundingRect.Height }
        $lines += [pscustomobject]@{ t = $l.Text; x0 = ($xs | Measure -Min).Minimum; y0 = ($ys | Measure -Min).Minimum; x1 = ($x2 | Measure -Max).Maximum; y1 = ($y2 | Measure -Max).Maximum }
    }
    $stream.Dispose()
    ConvertTo-Json -InputObject @($lines) -Depth 3 | Set-Content -Path $out -Encoding UTF8
}

