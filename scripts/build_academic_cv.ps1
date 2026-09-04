param(
    [string]$PythonExecutable
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $PythonExecutable) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        $pythonCommand = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $pythonCommand) {
        throw 'Python was not found on PATH. Install Python or pass -PythonExecutable with the full executable path.'
    }
    $PythonExecutable = $pythonCommand.Source
}

& $PythonExecutable -c 'import docx, pypdf'
if ($LASTEXITCODE -ne 0) {
    throw 'The selected Python must provide python-docx and pypdf. Install those packages or pass -PythonExecutable for an environment that includes them.'
}

$builder = Join-Path $PSScriptRoot 'build_academic_cv.py'
$docx = Join-Path $repoRoot 'files\Guo-Lu-CV.docx'
$canonicalPdf = Join-Path $repoRoot 'files\Guo-Lu-CV.pdf'
$legacyPdf = Join-Path $repoRoot 'paper\GuoLu.pdf'
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ('guo-lu-cv-' + [guid]::NewGuid().ToString('N'))
$tempPdf = Join-Path $tempDir 'Guo-Lu-CV.pdf'

New-Item -ItemType Directory -Path $tempDir | Out-Null
try {
    & $PythonExecutable $builder
    if ($LASTEXITCODE -ne 0) { throw 'DOCX generation failed.' }

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    try {
        $document = $word.Documents.Open($docx, $false, $true)
        $document.ExportAsFixedFormat($tempPdf, 17)
        $document.Close($false)
    } finally {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }

    & $PythonExecutable $builder --verify-pdf $tempPdf
    if ($LASTEXITCODE -ne 0) { throw 'Rendered PDF verification failed.' }

    New-Item -ItemType Directory -Force -Path (Split-Path $canonicalPdf), (Split-Path $legacyPdf) | Out-Null
    Copy-Item -LiteralPath $tempPdf -Destination $canonicalPdf -Force
    Copy-Item -LiteralPath $tempPdf -Destination $legacyPdf -Force
} finally {
    if (Test-Path -LiteralPath $tempDir) {
        Remove-Item -LiteralPath $tempDir -Recurse -Force
    }
}
