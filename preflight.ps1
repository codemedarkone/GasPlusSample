
<# ============================
 preflight.ps1 (run from repo root)
 - Loads .env 
 - Verifies UE + project + plugin paths
 - Validates Codex config (agents/spec)
 - Optional: runs headless UE smoke test
 - Optional: simulates label→agent routing
================================ #>

param(
  [switch]$RunSmoke = $false,
  [string]$Labels = "epic2-codegen,epic3-effects,docs",
  [switch]$VerboseLog = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

function Write-Section($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Ok($msg)        { Write-Host "✔ $msg" -ForegroundColor Green }
function Warn($msg)      { Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Fail($msg)      { Write-Host "✖ $msg" -ForegroundColor Red }

function Require-Cmd($cmd, $friendly) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "$friendly not found on PATH (missing command: $cmd)"
  }
}

function Load-DotEnv($path = ".env") {
  if (-not (Test-Path $path)) { throw ".env not found at $path" }
  $count = 0

  # Supports KEY="value" and KEY=value (ignores comments/blank lines)
  Get-Content $path | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^\s*#') { return }
    if ([string]::IsNullOrWhiteSpace($line)) { return }

    if ($line -match '^\s*([^=\s]+)\s*=\s*"(.*)"\s*$') {
      $k = $matches[1]; $v = $matches[2]
      Set-Item -Path "Env:$k" -Value $v
      $count++
    } elseif ($line -match '^\s*([^=\s]+)\s*=\s*(.+)\s*$') {
      $k = $matches[1]; $v = $matches[2]
      Set-Item -Path "Env:$k" -Value $v
      $count++
    }
  }
  return $count
}

function Show-EnvSummary() {
  Write-Host ("`nUE_ROOT:       {0}" -f $Env:UE_ROOT)
  Write-Host ("UE_CMD:         {0}" -f $Env:UE_CMD)
  Write-Host ("UPROJECT_PATH:  {0}" -f $Env:UPROJECT_PATH)
  Write-Host ("PLUGIN_DIR:     {0}" -f $Env:PLUGIN_DIR)
  Write-Host ("CODEX flags ->  fail_fast={0} parallel={1} log={2}" -f `
    $Env:CODEX_FAIL_FAST, $Env:CODEX_PARALLEL_JOBS, $Env:CODEX_LOG_LEVEL)
}

function Test-Paths() {
  if (-not (Test-Path "$Env:UE_CMD"))          { throw "UnrealEditor-Cmd.exe not found at `"$Env:UE_CMD`"" }
  if (-not (Test-Path "$Env:UPROJECT_PATH"))   { throw ".uproject not found at `"$Env:UPROJECT_PATH`"" }
  if (-not (Test-Path "$Env:PLUGIN_DIR"))      { throw "Plugin directory not found at `"$Env:PLUGIN_DIR`"" }
}

function Validate-Codex() {
  # codex presence is optional; we warn if missing and keep going
  if (-not (Get-Command "codex" -ErrorAction SilentlyContinue)) {
    Warn "Codex CLI not found on PATH. Skipping Codex validation/plan."
    return $false
  }
  $args = @("config","validate","--env",".env","--spec","AGENTS.md","--quiet")
  if ($VerboseLog) { $args = @("config","validate","--env",".env","--spec","AGENTS.md") }
  & codex @args | Out-Null
  Ok "Codex config validated (env + agents spec recognized)."
  return $true
}

function Plan-Agents([string]$labelsCsv) {
  if (-not (Get-Command "codex" -ErrorAction SilentlyContinue)) { return }
  $labelsCsv = ($labelsCsv -replace '\s','')
  if ([string]::IsNullOrWhiteSpace($labelsCsv)) { $labelsCsv = "docs" }
  & codex agents plan --labels $labelsCsv --env .env --spec AGENTS.md
  Ok "Label → agent routing plan generated."
}

function Smoke-Unreal() {
  # Use -testonly flags if present in your commandlet; otherwise a quick dry-run
  $flags = $Env:UE_CMD_FLAGS
  if ([string]::IsNullOrWhiteSpace($flags)) { $flags = "-stdout -unattended -nosplash" }

  $cmd = @(
    "$Env:UE_CMD",
    "$Env:UPROJECT_PATH",
    "-run=GasPlusCommandlet",
    "--preset=Effects",
    $flags.Split(' ')
  )

  if ($VerboseLog) {
    Write-Host "Running: `n& `"$($cmd[0])`" `"$($cmd[1])`" $($cmd[2..($cmd.Length-1)] -join ' ')" -ForegroundColor DarkGray
  }

  & $cmd[0] $cmd[1] $cmd[2] $cmd[3] $cmd[4..($cmd.Length-1)]
  Ok "Unreal headless smoke completed."
}

# ------------------ MAIN ------------------

Write-Section "Preflight: .env → Unreal → Codex"
try {
  $loaded = Load-DotEnv ".env"
  Ok "Loaded $loaded environment variables from .env"
  Show-EnvSummary

  Test-Paths
  Ok "Unreal and project paths validated"

  $codexOk = Validate-Codex
  if ($codexOk) {
    Plan-Agents -labelsCsv $Labels
  } else {
    Warn "Skip agent plan (Codex not detected)."
  }

  if ($RunSmoke) {
    Write-Section "Headless Unreal Smoke"
    Smoke-Unreal
  } else {
    Warn "Skipping Unreal smoke run (use -RunSmoke to enable)."
  }

  Write-Section "All checks passed"
  Ok "Environment is ready."

} catch {
  Fail $_.Exception.Message
  if (-not $VerboseLog) {
    Warn "Re-run with -VerboseLog for expanded output."
  }
  exit 1
}
