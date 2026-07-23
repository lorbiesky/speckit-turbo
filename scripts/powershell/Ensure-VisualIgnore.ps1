param([string]$ProjectRoot = ".")

$gitignore = Join-Path $ProjectRoot ".gitignore"
$start = '# speckit-turbo:visual-references:start'
$end = '# speckit-turbo:visual-references:end'
$rule = '.specify/visual-references/'
$content = if (Test-Path $gitignore) { Get-Content -Raw $gitignore } else { '' }

if (($content.Contains($start) -and -not $content.Contains($end)) -or ($content.Contains($end) -and -not $content.Contains($start))) {
  throw "Spec Kit Turbo visual ignore block is corrupted in $gitignore"
}
if (-not $content.Contains($start)) {
  $prefix = if ($content.Length -gt 0 -and -not $content.EndsWith("`n")) { "`n`n" } elseif ($content.Length -gt 0) { "`n" } else { '' }
  Add-Content -Path $gitignore -Value "$prefix$start`n$rule`n$end"
}
git -C $ProjectRoot check-ignore -q .specify/visual-references/.speckit-turbo-probe
if ($LASTEXITCODE -ne 0) { throw "Visual references are not ignored by Git." }
