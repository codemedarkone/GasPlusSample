<#
.SYNOPSIS
  Unified build menu for GasPlusSample (UE 5.6).

.DESCRIPTION
  Interactive, one-click style menu that:
    - Validates Unreal install & project path
    - Builds the Editor target
    - Optionally runs the GasPlus commandlet (Effects preset by default)
    - Optionally runs Automation tests (headless) and exports reports
    - Optionally packages a Win64 build (BuildCookRun)
  Uses UE_ROOT / UE5_ROOT / UPROJECT_PATH if set, but also allows on-the-fly overrides.

.NOTES
  Keep environment values without extra quotes (e.g., UE_ROOT=C:\Program Files\Epic Games\UE_5.6)
  so nested quoting doesn’t break PowerShell expansion.
#>

param(
  [string]$UERoot = $null,
  [string]$ProjectPath = $null
)

#-------------------------------
# Helpers
#-------------------------------
function Fail($msg) {
  Write-Host "ERROR: $msg" -ForegroundColor Red
  exit 1
}

function Pause-ForUser {
  Write-Host ""
  Read-Host "Press ENTER to continue"
}

function Resolve-Environment {
  param([string]$UERootArg, [string]$ProjectPathArg)

  $resolved = @{}

  # UE root precedence: param -> UE_ROOT -> UE5_ROOT
  if ($UERootArg) { $resolved.UERoot = $UERootArg }
  elseif ($env:UE_ROOT) { $resolved.UERoot = $env:UE_ROOT }
  elseif ($env:UE5_ROOT) { $resolved.UERoot = $env:UE5_ROOT }

  if (-not $resolved.UERoot) {
    Write-Host "Unreal root not found in args or env. Please enter your UE 5.6 path (e.g., C:\Program Files\Epic Games\UE_5.6):" -ForegroundColor Yellow
    $resolved.UERoot = Read-Host "UE Root"
  }

  if (-not (Test-Path $resolved.UERoot)) { Fail "UE root not found: $($resolved.UERoot)" }

  $resolved.UECmd     = Join-Path $resolved.UERoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
  $resolved.UEEditor  = Join-Path $resolved.UERoot "Engine\Binaries\Win64\UnrealEditor.exe"
  $resolved.UEBuild   = Join-Path $resolved.UERoot "Engine\Build\BatchFiles\Build.bat"
  $resolved.RunUAT    = Join-Path $resolved.UERoot "Engine\Build\BatchFiles\RunUAT.bat"

  foreach ($p in @($resolved.UECmd, $resolved.UEBuild, $resolved.RunUAT)) {
    if (-not (Test-Path $p)) { Fail "Missing tool: $p" }
  }

  # Project path precedence: param -> UPROJECT_PATH -> default to local
  if ($ProjectPathArg) { $resolved.ProjectPath = $ProjectPathArg }
  elseif ($env:UPROJECT_PATH) { $resolved.ProjectPath = $env:UPROJECT_PATH }
  else { $resolved.ProjectPath = (Resolve-Path "$PWD\GasPlusSample.uproject").Path }

  if (-not (Test-Path $resolved.ProjectPath)) { Fail "Project .uproject not found: $($resolved.ProjectPath)" }

  return $resolved
}

function Build-Editor {
  param($Resolved)
  Write-Host "`n==> Building Editor target..." -ForegroundColor Yellow
  & "$($Resolved.UEBuild)" GasPlusSampleEditor Win64 Development "-project=$($Resolved.ProjectPath)" -NoHotReload -Verbose
  if ($LASTEXITCODE -ne 0) { Fail "Editor build failed." }
  Write-Host "Build OK." -ForegroundColor Green
}

function Run-Commandlet {
  param($Resolved, [string]$Preset = "Effects")
  Write-Host "`n==> Running GasPlusCommandlet (Preset=$Preset)..." -ForegroundColor Yellow
  & "$($Resolved.UECmd)" "$($Resolved.ProjectPath)" -run=GasPlusCommandlet -Preset="$Preset" -unattended -nop4 -nosplash -NullRHI --quiet
  if ($LASTEXITCODE -ne 0) { Fail "Commandlet failed." }
  Write-Host "Commandlet OK." -ForegroundColor Green
}

function Run-Tests {
  param($Resolved)
  $reportDir = Join-Path (Split-Path $Resolved.ProjectPath -Parent) "Saved\Automation"
  if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }
  Write-Host "`n==> Running Automation tests (export to $reportDir)..." -ForegroundColor Yellow
  & "$($Resolved.UECmd)" "$($Resolved.ProjectPath)" -ExecCmds="Automation RunTests GasPlus; Quit" -ReportExportPath="$reportDir" -unattended -nop4 -nosplash -NullRHI
  if ($LASTEXITCODE -ne 0) { Fail "Automation tests failed." }
  Write-Host "Tests OK. Reports in $reportDir" -ForegroundColor Green
}

function Package-Win64 {
  param($Resolved)
  Write-Host "`n==> Packaging Win64 (BuildCookRun)..." -ForegroundColor Yellow
  & "$($Resolved.RunUAT)" BuildCookRun -project="$($Resolved.ProjectPath)" -build -stage -pak -targetplatform=Win64 -nop4 -unattended -utf8output
  if ($LASTEXITCODE -ne 0) { Fail "Packaging failed." }
  Write-Host "Package OK." -ForegroundColor Green
}

#-------------------------------
# Menu
#-------------------------------
function Show-Menu {
  Clear-Host
  Write-Host "=========================================" -ForegroundColor Cyan
  Write-Host "  GasPlusSample – UE 5.6 Build Menu"       -ForegroundColor Cyan
  Write-Host "=========================================`n" -ForegroundColor Cyan
  Write-Host "1) Build only"
  Write-Host "2) Build + Commandlet (Effects) + Tests"
  Write-Host "3) Build + Commandlet + Tests + Package (Win64)"
  Write-Host "4) Custom: Choose Preset and Steps"
  Write-Host "Q) Quit`n"
}

function Do-Choice {
  param($choice, $Resolved)

  switch ($choice) {
    '1' {
      Build-Editor -Resolved $Resolved
    }
    '2' {
      Build-Editor -Resolved $Resolved
      Run-Commandlet -Resolved $Resolved -Preset "Effects"
      Run-Tests -Resolved $Resolved
    }
    '3' {
      Build-Editor -Resolved $Resolved
      Run-Commandlet -Resolved $Resolved -Preset "Effects"
      Run-Tests -Resolved $Resolved
      Package-Win64 -Resolved $Resolved
    }
    '4' {
      $preset = Read-Host "Enter Commandlet preset (default: Effects)"
      if (-not $preset) { $preset = "Effects" }
      $doCmd = Read-Host "Run Commandlet? (y/n)"
      $doTst = Read-Host "Run Tests? (y/n)"
      $doPkg = Read-Host "Package Win64? (y/n)"

      Build-Editor -Resolved $Resolved
      if ($doCmd -match 'y') { Run-Commandlet -Resolved $Resolved -Preset $preset }
      if ($doTst -match 'y') { Run-Tests -Resolved $Resolved }
      if ($doPkg -match 'y') { Package-Win64 -Resolved $Resolved }
    }
    default {
      Write-Host "Unknown selection: $choice" -ForegroundColor Red
    }
  }

  Write-Host "`nAll done." -ForegroundColor Green
  Pause-ForUser
}

#-------------------------------
# Entry
#-------------------------------
try {
  $resolved = Resolve-Environment -UERootArg $UERoot -ProjectPathArg $ProjectPath
  Write-Host "UE Root     : $($resolved.UERoot)" -ForegroundColor DarkCyan
  Write-Host "Project     : $($resolved.ProjectPath)" -ForegroundColor DarkCyan
  Write-Host "UE-Cmd      : $($resolved.UECmd)" -ForegroundColor DarkCyan
  Write-Host ""

  do {
    Show-Menu
    $choice = Read-Host "Select an option"
    if ($choice -match '^[Qq]$') { break }
    Do-Choice -choice $choice -Resolved $resolved
  } while ($true)

} catch {
  Fail $_.Exception.Message
}
