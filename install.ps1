<#
.SYNOPSIS
    Universal Agent Skills & Brain - 1-Click Multi-Agent Installer for Windows
.DESCRIPTION
    Safely installs and integrates the 22 production skills into Google Antigravity, Cursor, or Claude Code.
.PARAMETER Target
    Destination environment: 'antigravity' (default), 'cursor', 'claude', or 'all'.
.PARAMETER DryRun
    Simulate installation without writing any files.
#>

[CmdletBinding()]
param (
    [ValidateSet('antigravity', 'cursor', 'claude', 'all')]
    [string]$Target = 'antigravity',

    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsSrc = Join-Path $ScriptDir "skills"
$RulesSrc = Join-Path $ScriptDir "rules"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "⚡ Universal Agent Skills & Autonomous Brain - Installer" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[*] Source: $ScriptDir" -ForegroundColor Gray
Write-Host "[*] Target Mode: $Target" -ForegroundColor Yellow

if (-not (Test-Path $SkillsSrc)) {
    Write-Error "Source 'skills' directory not found at: $SkillsSrc"
    exit 1
}

$Timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")

function Install-Antigravity {
    $HomeGemini = Join-Path $env:USERPROFILE ".gemini"
    $DestSkills = Join-Path $HomeGemini "config\skills"
    
    Write-Host "`n[*] Installing into Google Antigravity 2.0 ($HomeGemini)..." -ForegroundColor Green
    
    if ($DryRun) {
        Write-Host "[DRY-RUN] Would create: $DestSkills and copy 22 skills." -ForegroundColor Gray
        return
    }

    if (-not (Test-Path $DestSkills)) {
        New-Item -ItemType Directory -Path $DestSkills -Force | Out-Null
    } else {
        # Safe backup if directory already exists
        $BackupDir = Join-Path $HomeGemini "config\skills_backup_$Timestamp"
        Write-Host "[*] Creating safety backup of existing skills at: $BackupDir" -ForegroundColor Yellow
        Copy-Item -Path $DestSkills -Destination $BackupDir -Recurse -Force
    }

    Copy-Item -Path "$SkillsSrc\*" -Destination $DestSkills -Recurse -Force
    Write-Host "[✓] 22 Skills successfully deployed to: $DestSkills" -ForegroundColor Green

    # Copy rules
    $GeminiMdSrc = Join-Path $RulesSrc "GEMINI.md"
    if (Test-Path $GeminiMdSrc) {
        Copy-Item -Path $GeminiMdSrc -Destination (Join-Path $HomeGemini "GEMINI.md") -Force
        Write-Host "[✓] Workspace rules deployed to: $HomeGemini\GEMINI.md" -ForegroundColor Green
    }
}

function Install-Cursor {
    $LocalCursorRules = ".cursorrules"
    $DestCursorDir = ".cursor"
    $DestSkills = Join-Path $DestCursorDir "skills"

    Write-Host "`n[*] Installing into Cursor IDE project ($PWD)..." -ForegroundColor Green

    if ($DryRun) {
        Write-Host "[DRY-RUN] Would create: $DestSkills and .cursorrules" -ForegroundColor Gray
        return
    }

    if (-not (Test-Path $DestSkills)) {
        New-Item -ItemType Directory -Path $DestSkills -Force | Out-Null
    }

    Copy-Item -Path "$SkillsSrc\*" -Destination $DestSkills -Recurse -Force

    $CursorRuleContent = @"
# Cursor Agent Directives (Universal Agent Skills)
- Always enforce high-density technical responses (Zero pleasantries, lead with verified results).
- Strict adherence to the 22 modular skills located in '.cursor/skills/'.
- Internal Rigor Invariant: All diagnostics follow 4-Stage Root-Cause (Symptom -> Root Cause -> Target State -> Action Plan).
- Single-Agent First: Default to single unified context for >=90% of tasks.
"@
    Set-Content -Path $LocalCursorRules -Value $CursorRuleContent -Encoding UTF8
    Write-Host "[✓] Cursor skills & .cursorrules successfully configured in current directory!" -ForegroundColor Green
}

function Install-Claude {
    $ClaudeMd = "CLAUDE.md"
    $DestClaudeDir = ".claude"
    $DestSkills = Join-Path $DestClaudeDir "skills"

    Write-Host "`n[*] Installing into Claude Code project ($PWD)..." -ForegroundColor Green

    if ($DryRun) {
        Write-Host "[DRY-RUN] Would create: $DestSkills and CLAUDE.md" -ForegroundColor Gray
        return
    }

    if (-not (Test-Path $DestSkills)) {
        New-Item -ItemType Directory -Path $DestSkills -Force | Out-Null
    }

    Copy-Item -Path "$SkillsSrc\*" -Destination $DestSkills -Recurse -Force

    $ClaudeContent = @"
# CLAUDE.md — Senior Agentic Engineering Directives
- Response Economy: Lead with verified facts in 1-2 lines. Eliminate AI writing tells.
- Ponytail Minimal-Change: Smallest complete diff, standard library over unneeded bloat.
- Skills Index: 22 production-grade skills available in '.claude/skills/'.
"@
    Set-Content -Path $ClaudeMd -Value $ClaudeContent -Encoding UTF8
    Write-Host "[✓] Claude Code skills & CLAUDE.md successfully configured in current directory!" -ForegroundColor Green
}

switch ($Target) {
    'antigravity' { Install-Antigravity }
    'cursor'      { Install-Cursor }
    'claude'      { Install-Claude }
    'all'         {
        Install-Antigravity
        Install-Cursor
        Install-Claude
    }
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "🎉 Installation complete! Agent is ready for high-velocity engineering." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
