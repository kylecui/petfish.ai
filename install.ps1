<#
.SYNOPSIS
    胖鱼 PEtFiSh - Install skill packs for supported AI coding platforms.

.DESCRIPTION
    Copies skills, commands, and agents from one or more skill packs
    into the target project or global skills directories. Supports OpenCode,
    Claude Code, Codex, Cursor, GitHub Copilot, Windsurf, Antigravity,
    and Universal platform layouts.

.PARAMETER Pack
    Pack name or alias. Use 'all' to install every pack.
    Aliases: course, testdocs, deploy, init, petfish, companion, ppt, trust, research
    Full names also accepted.

.PARAMETER Target
    Path to the target project. Defaults to current directory.

.PARAMETER Platform
    Target platform: opencode, claude, codex, cursor, copilot, windsurf,
    antigravity, universal, or platform groups all/primary/ide/cli.
    Defaults to opencode.

.PARAMETER Detect
    Auto-detect the current platform from the target directory using
    platform markers from platforms.json. Defaults to opencode if no
    markers are found.

.PARAMETER Force
    Overwrite existing files without prompting.

.PARAMETER List
    List available packs and exit.

.PARAMETER Global
    Install skills into the platform's global skills directory instead of a target project.

.EXAMPLE
    .\install.ps1 -Pack course -Target C:\my-project
    .\install.ps1 -Pack all -Platform antigravity
    .\install.ps1 -Pack petfish -Platform all
    .\install.ps1 -Pack init -Global
    .\install.ps1 -Pack petfish -Detect
    .\install.ps1 -List
#>
[CmdletBinding()]
param(
    [string]$Pack,
    [string]$Target = ".",
    [ValidateSet("opencode", "claude", "codex", "cursor", "copilot", "windsurf", "antigravity", "universal", "all", "primary", "ide", "cli")]
    [string]$Platform = "opencode",
    [switch]$Detect,
    [switch]$Global,
    [switch]$Force,
    [switch]$List,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# --- uv availability check & auto-install ---
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[胖鱼 PEtFiSh] uv not found. Installing uv (required for Python-based skills)..." -ForegroundColor Yellow
    try {
        $uvInstallScript = (Invoke-RestMethod https://astral.sh/uv/install.ps1)
        $uvBlock = [scriptblock]::Create($uvInstallScript)
        & $uvBlock 2>$null
        # Refresh PATH to pick up newly installed uv
        $uvPath = Join-Path $env:USERPROFILE ".local\bin"
        if (Test-Path $uvPath) {
            $env:PATH = "$uvPath;$env:PATH"
        }
        # Also check cargo bin (alternative install location)
        $cargoPath = Join-Path $env:USERPROFILE ".cargo\bin"
        if (Test-Path $cargoPath) {
            $env:PATH = "$cargoPath;$env:PATH"
        }
        if (Get-Command uv -ErrorAction SilentlyContinue) {
            Write-Host "[胖鱼 PEtFiSh] ✅ uv installed successfully: $(uv --version)" -ForegroundColor Green
        } else {
            Write-Warning "[胖鱼 PEtFiSh] uv install completed but not found in PATH."
            Write-Warning "         You may need to restart your shell."
        }
    } catch {
        Write-Warning "[胖鱼 PEtFiSh] Failed to install uv automatically."
        Write-Warning "         Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    }
}

if (-not $List) {
    Write-Host ""
    Write-Host "  ><(((^>  胖鱼 PEtFiSh" -ForegroundColor DarkCyan
    Write-Host "  [胖鱼 PEtFiSh] AI Worker's Companion — Self-adaptive Skill Installer" -ForegroundColor Cyan
    Write-Host "  Initialize -> Auto-install -> Work immediately" -ForegroundColor DarkGray
    Write-Host ""
}

$GlobalExplicitlyPassed = $PSBoundParameters.ContainsKey("Global")
$TargetExplicitlyPassed = $PSBoundParameters.ContainsKey("Target")
$PlatformExplicitlyPassed = $PSBoundParameters.ContainsKey("Platform")

# Resolve script root (works whether run directly or piped)
$ScriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { $PWD.Path }
$PacksDir = Join-Path $ScriptRoot "packs"
$PlatformRegistry = Get-Content (Join-Path $ScriptRoot "platforms.json") -Raw -Encoding UTF8 | ConvertFrom-Json

# Pack alias registry
$Aliases = @{
    "course"   = "opencode-course-skills-pack"
    "testdocs" = "opencode-skill-pack-testcases-usage-docs"
    "deploy"   = "repo-deploy-ops-skill-pack"
    "init"     = "project-initializer-skill"
    "petfish"  = "petfish-style-skill"
    "companion" = "petfish-companion-skill"
    "ppt"      = "opencode-ppt-skills"
    "trust"    = "trustskills-governance-pack"
    "calibrate" = "anti-sycophancy-calibration-pack"
    "context"  = "fish-trail"
    "research" = "research-skill-pack"
    "reflect"  = "fish-reflection-pack"
    "fish-init"      = "project-initializer-skill"
    "fish-core"      = "petfish-companion-skill"
    "fish-course"    = "opencode-course-skills-pack"
    "fish-testdocs"  = "opencode-skill-pack-testcases-usage-docs"
    "fish-deploy"    = "repo-deploy-ops-skill-pack"
    "fish-style"     = "petfish-style-skill"
    "fish-slides"    = "opencode-ppt-skills"
    "fish-calibrate" = "anti-sycophancy-calibration-pack"
    "fish-trail"     = "fish-trail"
    "fish-research"  = "research-skill-pack"
    "fish-reflect"   = "fish-reflection-pack"
}

# --- Platform path configuration ---

function Get-PlatformDefinition([string]$platformName) {
    $platformProp = $PlatformRegistry.platforms.PSObject.Properties[$platformName]
    if (-not $platformProp) {
        Write-Error "Unsupported platform: '$platformName'"
        exit 1
    }
    return $platformProp.Value
}

function Expand-PlatformPath([string]$pathValue) {
    if ([string]::IsNullOrWhiteSpace($pathValue)) { return $null }
    if ($pathValue -eq "~") { return $HOME }
    if ($pathValue.StartsWith("~/") -or $pathValue.StartsWith('~\')) {
        return (Join-Path $HOME $pathValue.Substring(2))
    }
    return $pathValue
}

function ConvertTo-PlatformConfig([string]$platformName, $scopeConfig, [switch]$ExpandHome) {
    if (-not $scopeConfig) { return $null }

    $skillsDir = if ($ExpandHome) { Expand-PlatformPath $scopeConfig.skills_dir } else { $scopeConfig.skills_dir }
    $commandsDir = if ($ExpandHome) { Expand-PlatformPath $scopeConfig.commands_dir } else { $scopeConfig.commands_dir }
    $agentsDir = if ($ExpandHome) { Expand-PlatformPath $scopeConfig.agents_dir } else { $scopeConfig.agents_dir }
    $configFile = if ($ExpandHome) { Expand-PlatformPath $scopeConfig.config_file } else { $scopeConfig.config_file }
    $instructionsFile = if ($ExpandHome) { Expand-PlatformPath $scopeConfig.instructions_file } else { $scopeConfig.instructions_file }
    $rulesDir = if ($ExpandHome) { Expand-PlatformPath $scopeConfig.rules_dir } else { $scopeConfig.rules_dir }
    $registryDir = if ($skillsDir) { Split-Path -Parent $skillsDir } else { $null }

    $definition = Get-PlatformDefinition $platformName

    return @{
        SkillsDir               = $skillsDir
        CommandsDir             = $commandsDir
        AgentsDir               = $agentsDir
        ConfigFile              = $configFile
        InstructionsFile        = $instructionsFile
        RulesDir                = $rulesDir
        RegistryDir             = $registryDir
        DetectMarkers           = @($definition.detect_markers)
        InstructionsTranslation = $definition.instructions_translation
        GeminiMd                = ($platformName -eq "antigravity")
    }
}

function Get-PlatformConfig([string]$platformName) {
    $definition = Get-PlatformDefinition $platformName
    return ConvertTo-PlatformConfig $platformName $definition.project
}

function Get-GlobalPlatformConfig([string]$platformName) {
    $definition = Get-PlatformDefinition $platformName
    return ConvertTo-PlatformConfig $platformName $definition.global -ExpandHome
}

function Get-PlatformGroup([string]$groupName) {
    $groupProp = $PlatformRegistry.platform_groups.PSObject.Properties[$groupName]
    if (-not $groupProp) {
        Write-Error "Unknown platform group: '$groupName'"
        exit 1
    }
    return @($groupProp.Value)
}

function Get-PlatformsForSelection([string]$selection) {
    if ($PlatformRegistry.platform_groups.PSObject.Properties[$selection]) {
        return Get-PlatformGroup $selection
    }
    return @($selection)
}

function Get-DetectionOrder {
    $ordered = New-Object System.Collections.Generic.List[string]
    foreach ($name in (Get-PlatformGroup "primary")) {
        if (-not $ordered.Contains($name)) { [void]$ordered.Add($name) }
    }
    foreach ($prop in $PlatformRegistry.platforms.PSObject.Properties) {
        if (-not $ordered.Contains($prop.Name)) { [void]$ordered.Add($prop.Name) }
    }
    return @($ordered)
}

function Get-DetectedPlatform([string]$targetPath) {
    $all = Get-AllDetectedPlatforms $targetPath
    return $all[0]
}

function Get-AllDetectedPlatforms([string]$targetPath) {
    $found = @()
    foreach ($platformName in (Get-DetectionOrder)) {
        $cfg = Get-PlatformConfig $platformName
        foreach ($marker in $cfg.DetectMarkers) {
            if (-not [string]::IsNullOrWhiteSpace($marker)) {
                $markerPath = Join-Path $targetPath $marker
                if (Test-Path $markerPath) {
                    $found += $platformName
                    break
                }
            }
        }
    }
    if ($found.Count -eq 0) {
        return @("opencode")
    }
    return @($found)
}

# --- Merge helpers ---

function Merge-AgentsMd([string]$srcFile, [string]$dstFile, [string]$packName, [switch]$ForceOverwrite, [string]$ManifestFile = "") {
    $beginMarker = "<!-- BEGIN pack: $packName -->"
    $endMarker = "<!-- END pack: $packName -->"
    $srcContent = (Get-Content $srcFile -Raw -Encoding UTF8).TrimEnd()
    # Strip existing markers from source if present (safety net)
    $srcContent = $srcContent -replace "(?m)^$([regex]::Escape($beginMarker))\s*$", ""
    $srcContent = $srcContent -replace "(?m)^$([regex]::Escape($endMarker))\s*$", ""
    $srcContent = $srcContent.Trim()
    $wrappedContent = "$beginMarker`n$srcContent`n$endMarker"

    # Resolve legacy names from manifest
    $legacyNames = @()
    if ($ManifestFile -and (Test-Path $ManifestFile)) {
        try {
            $manifest = Get-Content $ManifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($manifest.legacy_names) {
                $legacyNames = @($manifest.legacy_names)
            }
        } catch {}
    }

    if (-not (Test-Path $dstFile)) {
        Set-Content -Path $dstFile -Value $wrappedContent -NoNewline -Encoding UTF8
        return "created"
    }

    $existing = Get-Content $dstFile -Raw -Encoding UTF8

    # Check if current name OR any legacy name exists
    $foundMarker = $false
    if ($existing -match [regex]::Escape($beginMarker)) {
        $foundMarker = $true
    } else {
        foreach ($legacy in $legacyNames) {
            $legacyBegin = "<!-- BEGIN pack: $legacy -->"
            if ($existing -match [regex]::Escape($legacyBegin)) {
                $foundMarker = $true
                break
            }
        }
    }

    if ($foundMarker) {
        if (-not $ForceOverwrite) { return "exists" }

        # Build list of all names to remove (current + legacy)
        $allNames = @($packName) + $legacyNames
        $earliestPos = $existing.Length

        # Remove all sections matching any name, track earliest position
        foreach ($name in $allNames) {
            $nameBegin = [regex]::Escape("<!-- BEGIN pack: $name -->")
            $nameEnd = [regex]::Escape("<!-- END pack: $name -->")
            $namePattern = "(?s)$nameBegin.*?$nameEnd"
            $m = [regex]::Match($existing, $namePattern)
            if ($m.Success -and $m.Index -lt $earliestPos) {
                $earliestPos = $m.Index
            }
            # Remove ALL occurrences of this name
            $existing = [regex]::Replace($existing, $namePattern, "")
        }

        # Insert replacement at earliest position
        $existing = $existing.TrimEnd()
        $earliestPos = [Math]::Min($earliestPos, $existing.Length)
        $beforePart = $existing.Substring(0, $earliestPos).TrimEnd()
        $afterPart = $existing.Substring($earliestPos).TrimStart()
        if ($beforePart) {
            $replaced = $beforePart + "`n`n" + $wrappedContent
        } else {
            $replaced = $wrappedContent
        }
        if ($afterPart) {
            $replaced = $replaced + "`n`n" + $afterPart
        }

        # Clean up multiple blank lines
        $replaced = [regex]::Replace($replaced, "(\r?\n){3,}", "`n`n").Trim() + "`n"
        Set-Content -Path $dstFile -Value $replaced -NoNewline -Encoding UTF8
        return "updated"
    }

    $merged = $existing.TrimEnd() + "`n`n" + $wrappedContent + "`n"
    Set-Content -Path $dstFile -Value $merged -NoNewline -Encoding UTF8
    return "merged"
}

# Dual-write: write pack AGENTS.md content as standalone L1 rules file (Phase 1, v0.11.0)
# Only called for --platform opencode. Strips BEGIN/END markers before writing.
function Write-PackRulesFile([string]$srcFile, [string]$targetDir, [string]$packName) {
    $L1Map = @{
        "opencode-course-skills-pack"        = "course-skills.md"
        "repo-deploy-ops-skill-pack"         = "deploy-ops.md"
        "petfish-style-skill"                = "petfish-style.md"
        "petfish-companion-skill"            = "petfish-companion.md"
        "anti-sycophancy-calibration-pack"   = "anti-sycophancy.md"
        "fish-trail"                         = "fish-trail.md"
        "research-skill-pack"                = "research.md"
    }
    $l1Name = $L1Map[$packName]
    if (-not $l1Name) { return }

    $rulesDir = Join-Path $targetDir ".opencode" "agents-rules"
    if (-not (Test-Path $rulesDir)) {
        New-Item -ItemType Directory -Path $rulesDir -Force | Out-Null
    }

    $content = (Get-Content $srcFile -Raw -Encoding UTF8).TrimEnd()
    $beginMarker = "<!-- BEGIN pack: $packName -->"
    $endMarker = "<!-- END pack: $packName -->"
    $content = $content -replace "(?m)^$([regex]::Escape($beginMarker))\s*$", ""
    $content = $content -replace "(?m)^$([regex]::Escape($endMarker))\s*$", ""
    $content = $content.Trim() + "`n"

    $dstFile = Join-Path $rulesDir $l1Name
    Set-Content -Path $dstFile -Value $content -NoNewline -Encoding UTF8
    Write-Host "    + .opencode/agents-rules/$l1Name" -ForegroundColor DarkGreen
}

# Install system-prompt-rules plugin file to .opencode/plugin/ (v0.11.0+)
# Only for OpenCode platform when L1 packs are present.
function Install-PluginFile([string]$sourceRoot, [string]$targetDir) {
    $srcPlugin = Join-Path $sourceRoot "lib" "plugin" "system-prompt-rules.ts"
    if (-not (Test-Path $srcPlugin)) { return }

    $pluginDir = Join-Path $targetDir ".opencode" "plugin"
    if (-not (Test-Path $pluginDir)) {
        New-Item -ItemType Directory -Path $pluginDir -Force | Out-Null
    }

    $dstPlugin = Join-Path $pluginDir "system-prompt-rules.ts"
    Copy-Item -Path $srcPlugin -Destination $dstPlugin -Force
    Write-Host "    + .opencode/plugin/system-prompt-rules.ts" -ForegroundColor DarkGreen
}

# Register plugin tuple in opencode.json (idempotent)
function Register-PluginInConfig([string]$configFile) {
    if (-not (Test-Path $configFile)) { return }

    $raw = Get-Content $configFile -Raw -Encoding UTF8
    $json = $raw | ConvertFrom-Json

    $pluginPath = ".opencode/plugin/system-prompt-rules.ts"
    $pluginTuple = @($pluginPath, @{ mode = "all" })

    # Check if plugin array exists and already contains this plugin
    if ($json.PSObject.Properties["plugin"]) {
        $existing = $json.plugin
        foreach ($entry in $existing) {
            if ($entry -is [System.Collections.IEnumerable] -and $entry.Count -ge 1) {
                if ($entry[0] -eq $pluginPath) {
                    # Already registered
                    return
                }
            }
        }
        # Append to existing plugin array
        $json.plugin = @($existing) + ,@(,$pluginTuple)
    } else {
        # Create plugin array with single tuple
        $json | Add-Member -NotePropertyName "plugin" -NotePropertyValue @(,@($pluginTuple))
    }

    $json | ConvertTo-Json -Depth 10 | Set-Content $configFile -Encoding UTF8
    Write-Host "    + opencode.json (plugin registered)" -ForegroundColor DarkGreen
}

# v0.10.x→v0.11.x migration: remove inline pack section from AGENTS.md
# when it has been migrated to L1 standalone rules file
function Remove-InlinePackSection([string]$agentsFile, [string]$packName, [string]$manifestFile = "") {
    if (-not (Test-Path $agentsFile)) { return }
    $content = Get-Content $agentsFile -Raw -Encoding UTF8

    # Collect all names to remove: current + legacy names from manifest
    $namesToTry = @($packName)
    if ($manifestFile -and (Test-Path $manifestFile)) {
        try {
            $manifest = Get-Content $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($manifest.legacy_names) {
                $namesToTry += @($manifest.legacy_names)
            }
        } catch {}
    }

    $removed = $false
    foreach ($name in $namesToTry) {
        $beginMarker = "<!-- BEGIN pack: $name -->"
        $endMarker = "<!-- END pack: $name -->"
        if ($content -notmatch [regex]::Escape($beginMarker)) { continue }

        # Remove everything between BEGIN and END markers (inclusive), plus surrounding blank lines
        $pattern = "(?ms)\r?\n?\s*$([regex]::Escape($beginMarker)).*?$([regex]::Escape($endMarker))\s*\r?\n?"
        $content = $content -replace $pattern, "`n"
        $removed = $true
        Write-Host "    - AGENTS.md (removed inline section for $name)" -ForegroundColor DarkYellow
    }

    if ($removed) {
        # Collapse triple+ newlines to double
        $content = $content -replace "(\r?\n){3,}", "`n`n"
        Set-Content -Path $agentsFile -Value $content.TrimEnd() -NoNewline -Encoding UTF8
    }
}

# --- Uninstall function ---

function Uninstall-Pack([string]$packAlias, [string]$targetPath) {
    $packName = Get-PackFullName $packAlias

    Write-Host "`n  Uninstalling pack: $packName (alias: $packAlias)" -ForegroundColor Yellow

    # Step 1: Read pack-manifest.json from source
    $packRoot = Join-Path $PacksDir $packName
    $manifestFile = Join-Path $packRoot "pack-manifest.json"
    if (-not (Test-Path $manifestFile)) {
        Write-Error "Pack manifest not found: $manifestFile"
        exit 1
    }
    $manifest = Get-Content $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json

    # Determine platform config
    $cfg = Get-PlatformConfig $Platform
    $targetSkills = if ($cfg.SkillsDir) { Join-Path $targetPath $cfg.SkillsDir } else { $null }
    $targetCommands = if ($cfg.CommandsDir) { Join-Path $targetPath $cfg.CommandsDir } else { $null }
    $targetAgents = if ($cfg.AgentsDir) { Join-Path $targetPath $cfg.AgentsDir } else { $null }
    $targetRegistry = if ($cfg.RegistryDir) { Join-Path $targetPath $cfg.RegistryDir } else { $null }

    # Step 2: Validate pack is installed
    if ($targetRegistry) {
        $regFile = Join-Path $targetRegistry "installed-packs.json"
        if (Test-Path $regFile) {
            $registry = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
            $isInstalled = $registry.packs.PSObject.Properties[$packName]
            if (-not $isInstalled) {
                # Check legacy names
                $found = $false
                if ($manifest.PSObject.Properties['legacy_names']) {
                    foreach ($legacy in $manifest.legacy_names) {
                        if ($registry.packs.PSObject.Properties[$legacy]) {
                            $found = $true
                            break
                        }
                    }
                }
                if (-not $found) {
                    Write-Error "Pack '$packAlias' ($packName) is not installed. Nothing to uninstall."
                    exit 1
                }
            }
        } else {
            Write-Error "No installed-packs.json found at $regFile. Nothing to uninstall."
            exit 1
        }
    }

    $removed = 0

    # Step 3: Remove skill directories
    if ($targetSkills -and $manifest.PSObject.Properties['skills']) {
        foreach ($skill in $manifest.skills) {
            $skillDir = Join-Path $targetSkills $skill
            if (Test-Path $skillDir) {
                Remove-Item -Path $skillDir -Recurse -Force
                Write-Host "    - skills/$skill" -ForegroundColor DarkYellow
                $removed++
            }
        }
    }

    # Step 4: Remove command directories
    if ($targetCommands -and $manifest.PSObject.Properties['commands']) {
        foreach ($cmd in $manifest.commands) {
            # Commands can be directories or files (e.g., petfish.md)
            $cmdDir = Join-Path $targetCommands $cmd
            $cmdFile = Join-Path $targetCommands "$cmd.md"
            if (Test-Path $cmdDir) {
                Remove-Item -Path $cmdDir -Recurse -Force
                Write-Host "    - commands/$cmd" -ForegroundColor DarkYellow
                $removed++
            } elseif (Test-Path $cmdFile) {
                Remove-Item -Path $cmdFile -Force
                Write-Host "    - commands/$cmd.md" -ForegroundColor DarkYellow
                $removed++
            }
        }
    }

    # Step 5: Remove agent directories
    if ($targetAgents -and $manifest.PSObject.Properties['agents']) {
        foreach ($agent in $manifest.agents) {
            $agentDir = Join-Path $targetAgents $agent
            if (Test-Path $agentDir) {
                Remove-Item -Path $agentDir -Recurse -Force
                Write-Host "    - agents/$agent" -ForegroundColor DarkYellow
                $removed++
            }
        }
    }

    # Step 6: Remove AGENTS.md section (inline markers)
    $agentsFile = Join-Path $targetPath "AGENTS.md"
    Remove-InlinePackSection $agentsFile $packName $manifestFile

    # Step 6b: Remove L1 rules file (opencode platform)
    $L1Map = @{
        "opencode-course-skills-pack"        = "course-skills.md"
        "repo-deploy-ops-skill-pack"         = "deploy-ops.md"
        "petfish-style-skill"                = "petfish-style.md"
        "petfish-companion-skill"            = "petfish-companion.md"
        "anti-sycophancy-calibration-pack"   = "anti-sycophancy.md"
        "fish-trail"                         = "fish-trail.md"
        "research-skill-pack"                = "research.md"
    }
    if ($L1Map.ContainsKey($packName)) {
        $rulesFile = Join-Path $targetPath ".opencode" "agents-rules" $L1Map[$packName]
        if (Test-Path $rulesFile) {
            Remove-Item -Path $rulesFile -Force
            Write-Host "    - .opencode/agents-rules/$($L1Map[$packName])" -ForegroundColor DarkYellow
            $removed++
        }
    }

    # Step 6c: Remove Pack-Specific Rules reference from AGENTS.md
    if ($L1Map.ContainsKey($packName)) {
        $l1FileName = $L1Map[$packName]
        if (Test-Path $agentsFile) {
            $agentsContent = Get-Content $agentsFile -Raw -Encoding UTF8
            # Remove the table row referencing this pack's rules file
            $escapedFileName = [regex]::Escape($l1FileName)
            $rowPattern = "(?m)^\|[^|]*\|[^|]*\|[^|]*$escapedFileName[^|]*\|\s*\r?\n"
            if ($agentsContent -match $rowPattern) {
                $agentsContent = $agentsContent -replace $rowPattern, ""
                Set-Content -Path $agentsFile -Value $agentsContent.TrimEnd() -NoNewline -Encoding UTF8
                Write-Host "    - AGENTS.md (removed rules-file reference for $l1FileName)" -ForegroundColor DarkYellow
            }
        }
    }

    # Step 7: Remove opencode.json entries (only keys unique to this pack)
    if ($cfg.ConfigFile) {
        $ocExample = Join-Path $packRoot "opencode.example.json"
        $dstOc = Join-Path $targetPath $cfg.ConfigFile
        if ((Test-Path $ocExample) -and (Test-Path $dstOc)) {
            $packKeys = Get-Content $ocExample -Raw -Encoding UTF8 | ConvertFrom-Json
            $dstJson = Get-Content $dstOc -Raw -Encoding UTF8 | ConvertFrom-Json

            # Collect keys from ALL OTHER installed packs' opencode.example.json
            $otherPackKeys = @{}
            if ($targetRegistry -and (Test-Path $regFile)) {
                foreach ($otherPack in $registry.packs.PSObject.Properties) {
                    if ($otherPack.Name -eq $packName) { continue }
                    $otherRoot = Join-Path $PacksDir $otherPack.Name
                    $otherExample = Join-Path $otherRoot "opencode.example.json"
                    if (Test-Path $otherExample) {
                        $otherJson = Get-Content $otherExample -Raw -Encoding UTF8 | ConvertFrom-Json
                        # Track L1 keys (e.g., "mcp", "permission")
                        foreach ($p1 in $otherJson.PSObject.Properties) {
                            if (-not $otherPackKeys.ContainsKey($p1.Name)) {
                                $otherPackKeys[$p1.Name] = @{}
                            }
                            if ($p1.Value -is [PSCustomObject]) {
                                foreach ($p2 in $p1.Value.PSObject.Properties) {
                                    $otherPackKeys[$p1.Name][$p2.Name] = $true
                                }
                            }
                        }
                    }
                }
            }

            # Remove keys from this pack that no other installed pack uses
            $ocChanged = $false
            foreach ($p1 in $packKeys.PSObject.Properties) {
                if ($p1.Value -is [PSCustomObject] -and $dstJson.PSObject.Properties[$p1.Name]) {
                    $dstLevel1 = $dstJson.($p1.Name)
                    if ($dstLevel1 -is [PSCustomObject]) {
                        foreach ($p2 in $p1.Value.PSObject.Properties) {
                            # Only remove if no other pack claims this key
                            $otherClaims = $otherPackKeys.ContainsKey($p1.Name) -and $otherPackKeys[$p1.Name].ContainsKey($p2.Name)
                            if (-not $otherClaims -and $dstLevel1.PSObject.Properties[$p2.Name]) {
                                $dstLevel1.PSObject.Properties.Remove($p2.Name)
                                Write-Host "    - $($cfg.ConfigFile) ($($p1.Name).$($p2.Name))" -ForegroundColor DarkYellow
                                $ocChanged = $true
                            }
                        }
                    }
                }
            }
            if ($ocChanged) {
                $dstJson | ConvertTo-Json -Depth 10 | Set-Content $dstOc -Encoding UTF8
            }
        }
    }

    # Step 8: Remove from installed-packs.json (last — enables re-run recovery)
    if ($targetRegistry -and (Test-Path $regFile)) {
        $registry = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $removedFromRegistry = $false

        if ($registry.packs.PSObject.Properties[$packName]) {
            $registry.packs.PSObject.Properties.Remove($packName)
            $removedFromRegistry = $true
        }

        # Also remove legacy names
        if ($manifest.PSObject.Properties['legacy_names']) {
            foreach ($legacy in $manifest.legacy_names) {
                if ($registry.packs.PSObject.Properties[$legacy]) {
                    $registry.packs.PSObject.Properties.Remove($legacy)
                    $removedFromRegistry = $true
                }
            }
        }

        if ($removedFromRegistry) {
            $registry | ConvertTo-Json -Depth 10 | Set-Content $regFile -Encoding UTF8
            Write-Host "    - installed-packs.json (registry updated)" -ForegroundColor DarkYellow
            $removed++
        }
    }

    Write-Host "`n  Uninstall complete: $removed items removed." -ForegroundColor Cyan
    $restartHint = Get-RestartHint $Platform
    if ($restartHint) {
        Write-Host $restartHint -ForegroundColor Yellow
    }
}

function Uninstall-GlobalPack([string]$packAlias) {
    $packName = Get-PackFullName $packAlias

    Write-Host "`n  Uninstalling pack (global): $packName (alias: $packAlias)" -ForegroundColor Yellow

    $packRoot = Join-Path $PacksDir $packName
    $manifestFile = Join-Path $packRoot "pack-manifest.json"
    if (-not (Test-Path $manifestFile)) {
        Write-Error "Pack manifest not found: $manifestFile"
        exit 1
    }
    $manifest = Get-Content $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json

    $cfg = Get-GlobalPlatformConfig $Platform
    $targetSkills = $cfg.SkillsDir
    $targetRegistry = $cfg.RegistryDir

    if (-not $targetSkills) {
        Write-Warning "$Platform does not support global skill installation. Nothing to uninstall."
        return
    }

    # Validate installed
    if ($targetRegistry) {
        $regFile = Join-Path $targetRegistry "installed-packs.json"
        if (-not (Test-Path $regFile)) {
            Write-Error "No installed-packs.json found. Nothing to uninstall."
            exit 1
        }
        $registry = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $registry.packs.PSObject.Properties[$packName]) {
            Write-Error "Pack '$packAlias' ($packName) is not installed globally. Nothing to uninstall."
            exit 1
        }
    }

    $removed = 0

    # Remove skill directories
    if ($manifest.PSObject.Properties['skills']) {
        foreach ($skill in $manifest.skills) {
            $skillDir = Join-Path $targetSkills $skill
            if (Test-Path $skillDir) {
                Remove-Item -Path $skillDir -Recurse -Force
                Write-Host "    - skills/$skill" -ForegroundColor DarkYellow
                $removed++
            }
        }
    }

    # Remove command files/dirs
    if ($cfg.CommandsDir -and $manifest.PSObject.Properties['commands']) {
        foreach ($cmd in $manifest.commands) {
            $cmdDir = Join-Path $cfg.CommandsDir $cmd
            $cmdFile = Join-Path $cfg.CommandsDir "$cmd.md"
            if (Test-Path $cmdDir) {
                Remove-Item -Path $cmdDir -Recurse -Force
                Write-Host "    - commands/$cmd" -ForegroundColor DarkYellow
                $removed++
            } elseif (Test-Path $cmdFile) {
                Remove-Item -Path $cmdFile -Force
                Write-Host "    - commands/$cmd.md" -ForegroundColor DarkYellow
                $removed++
            }
        }
    }

    # Remove from registry (last)
    if ($targetRegistry -and (Test-Path $regFile)) {
        $registry = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($registry.packs.PSObject.Properties[$packName]) {
            $registry.packs.PSObject.Properties.Remove($packName)
            $registry | ConvertTo-Json -Depth 10 | Set-Content $regFile -Encoding UTF8
            Write-Host "    - installed-packs.json (registry updated)" -ForegroundColor DarkYellow
            $removed++
        }
    }

    Write-Host "`n  Global uninstall complete: $removed items removed." -ForegroundColor Cyan
}

function Merge-OpencodeJson([string]$srcFile, [string]$dstFile, [switch]$ForceOverwrite, [string]$SkillsDir = ".opencode/skills") {
    $src = Get-Content $srcFile -Raw -Encoding UTF8 | ConvertFrom-Json
    $normalizedSkillsDir = if ([string]::IsNullOrWhiteSpace($SkillsDir)) { ".opencode/skills" } else { ($SkillsDir -replace '[\\/]+$','') }
    if ([string]::IsNullOrWhiteSpace($normalizedSkillsDir)) {
        $normalizedSkillsDir = ".opencode/skills"
    }

    $srcStr = $src | ConvertTo-Json -Depth 10
    $srcStr = $srcStr.Replace('.opencode/skills/', ($normalizedSkillsDir + '/'))
    $src = $srcStr | ConvertFrom-Json

    if (-not (Test-Path $dstFile)) {
        $parentDir = Split-Path -Parent $dstFile
        if ($parentDir -and -not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        $src | ConvertTo-Json -Depth 10 | Set-Content $dstFile -Encoding UTF8
        return "created"
    }

    $dst = Get-Content $dstFile -Raw -Encoding UTF8 | ConvertFrom-Json

    # Recursive shallow merge (3 levels deep: permission.skill.X = "allow")
    # Exception: mcp entries are replaced atomically at level 2 (not deep-merged)
    $atomicL2 = @("mcp")
    foreach ($p1 in $src.PSObject.Properties) {
        if (-not $dst.PSObject.Properties[$p1.Name]) {
            $dst | Add-Member -NotePropertyName $p1.Name -NotePropertyValue $p1.Value
        } elseif ($p1.Value -is [PSCustomObject] -and $dst.($p1.Name) -is [PSCustomObject]) {
            foreach ($p2 in $p1.Value.PSObject.Properties) {
                $level2 = $dst.($p1.Name)
                if (-not $level2.PSObject.Properties[$p2.Name]) {
                    $level2 | Add-Member -NotePropertyName $p2.Name -NotePropertyValue $p2.Value
                } elseif ($p1.Name -in $atomicL2 -and $ForceOverwrite) {
                    # Replace entire entry atomically (e.g. mcp.context-state)
                    $level2.($p2.Name) = $p2.Value
                } elseif ($p2.Value -is [PSCustomObject] -and $level2.($p2.Name) -is [PSCustomObject]) {
                    foreach ($p3 in $p2.Value.PSObject.Properties) {
                        $level3 = $level2.($p2.Name)
                        if (-not $level3.PSObject.Properties[$p3.Name] -or $ForceOverwrite) {
                            if ($level3.PSObject.Properties[$p3.Name]) {
                                $level3.($p3.Name) = $p3.Value
                            } else {
                                $level3 | Add-Member -NotePropertyName $p3.Name -NotePropertyValue $p3.Value
                            }
                        }
                    }
                } elseif ($ForceOverwrite) {
                    $level2.($p2.Name) = $p2.Value
                }
            }
        } elseif ($ForceOverwrite) {
            $dst.($p1.Name) = $p1.Value
        }
    }

    $dst | ConvertTo-Json -Depth 10 | Set-Content $dstFile -Encoding UTF8
    return "merged"
}

function Update-InstalledPacks([string]$registryDir, [string]$packName, [string]$manifestFile) {
    $regFile = Join-Path $registryDir "installed-packs.json"
    $entry = @{ installed_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ") }

    if (Test-Path $manifestFile) {
        $m = Get-Content $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($m.PSObject.Properties['version'])       { $entry.version = $m.version }
        if ($m.PSObject.Properties['skills'])         { $entry.skills = $m.skills }
        if ($m.PSObject.Properties['description'])    { $entry.description = $m.description }
        if ($m.PSObject.Properties['skill_count'])    { $entry.skill_count = $m.skill_count }
        elseif ($m.PSObject.Properties['skills'])     { $entry.skill_count = @($m.skills).Count }
        if ($m.PSObject.Properties['command_count'])  { $entry.command_count = $m.command_count }
        if ($m.PSObject.Properties['agent_count'])    { $entry.agent_count = $m.agent_count }
    }

    if (-not (Test-Path $registryDir)) {
        New-Item -ItemType Directory -Path $registryDir -Force | Out-Null
    }

    if (Test-Path $regFile) {
        $reg = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
    } else {
        $reg = [PSCustomObject]@{ packs = [PSCustomObject]@{} }
    }

    $entryObj = [PSCustomObject]$entry
    if ($reg.packs.PSObject.Properties[$packName]) {
        $reg.packs.$packName = $entryObj
    } else {
        $reg.packs | Add-Member -NotePropertyName $packName -NotePropertyValue $entryObj
    }

    $reg | ConvertTo-Json -Depth 10 | Set-Content $regFile -Encoding UTF8
}

function Compare-PackVersion([string]$registryDir, [string]$packName, [string]$manifestFile) {
    $script:ComparePackVersionInstalledVersion = $null
    $script:ComparePackVersionSourceVersion = $null
    $script:ComparePackVersionLegacyKey = $null

    if ([string]::IsNullOrWhiteSpace($registryDir) -or -not (Test-Path $manifestFile)) {
        return "unknown"
    }

    try {
        $manifest = Get-Content $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        return "unknown"
    }

    $sourceVersion = if ($manifest.PSObject.Properties['version']) { "$($manifest.version)" } else { $null }
    if ([string]::IsNullOrWhiteSpace($sourceVersion)) {
        return "unknown"
    }
    $script:ComparePackVersionSourceVersion = $sourceVersion

    $regFile = Join-Path $registryDir "installed-packs.json"
    if (-not (Test-Path $regFile)) {
        return "not-installed"
    }

    try {
        $registry = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        return "unknown"
    }

    if (-not $registry.PSObject.Properties['packs']) {
        return "not-installed"
    }

    $packEntryProp = $registry.packs.PSObject.Properties[$packName]

    # Legacy name lookup: check manifest's legacy_names if current name not found
    if (-not $packEntryProp) {
        if ($manifest.PSObject.Properties['legacy_names'] -and $manifest.legacy_names) {
            foreach ($legacyName in $manifest.legacy_names) {
                $legacyProp = $registry.packs.PSObject.Properties[$legacyName]
                if ($legacyProp) {
                    $packEntryProp = $legacyProp
                    $script:ComparePackVersionLegacyKey = $legacyName
                    break
                }
            }
        }
    }

    if (-not $packEntryProp) {
        return "not-installed"
    }

    $packEntry = $packEntryProp.Value
    $installedVersion = if ($packEntry.PSObject.Properties['version']) { "$($packEntry.version)" } else { $null }
    if ([string]::IsNullOrWhiteSpace($installedVersion)) {
        return "unknown"
    }
    $script:ComparePackVersionInstalledVersion = $installedVersion

    $sourceParts = $sourceVersion -split '\.'
    $installedParts = $installedVersion -split '\.'
    if ($sourceParts.Count -lt 3 -or $installedParts.Count -lt 3) {
        return "unknown"
    }

    foreach ($index in 0..2) {
        if ($sourceParts[$index] -notmatch '^\d+$' -or $installedParts[$index] -notmatch '^\d+$') {
            return "unknown"
        }

        $installedPart = [int]$installedParts[$index]
        $sourcePart = [int]$sourceParts[$index]

        if ($installedPart -lt $sourcePart) {
            return "newer"
        }

        if ($installedPart -gt $sourcePart) {
            return "unknown"
        }
    }

    return "same"
}

function Compress-InstructionContent([string]$content, [int]$maxTokens) {
    $charCount = $content.Length
    $estTokens = [math]::Floor($charCount / 4)

    if ($estTokens -le $maxTokens) {
        return $content
    }

    $tempInput = [System.IO.Path]::GetTempFileName()
    $tempOutput = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempInput, $content, [System.Text.Encoding]::UTF8)

    $pyScript = @'
import sys

max_tokens = int(sys.argv[1])
input_file = sys.argv[2]
output_file = sys.argv[3]

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

sections = []
current = []
current_priority = 1
current_name = ""

for line in content.split('\n'):
    if line.startswith('<!-- BEGIN pack:'):
        if current:
            sections.append((current_name, current_priority, '\n'.join(current)))
        current = [line]
        current_name = line.split('pack:')[1].split('-->')[0].strip() if 'pack:' in line else ""
        p0_packs = ['petfish-companion-skill', 'fish-trail']
        if current_name in p0_packs:
            current_priority = 0
        else:
            current_priority = 1
    elif line.startswith('<!-- END pack:'):
        current.append(line)
        sections.append((current_name, current_priority, '\n'.join(current)))
        current = []
        current_name = ""
        current_priority = 1
    else:
        current.append(line)

if current:
    sections.append((current_name, current_priority, '\n'.join(current)))

p0 = [(n, p, c) for n, p, c in sections if p == 0]
p1 = [(n, p, c) for n, p, c in sections if p == 1]

result_parts = []
used_tokens = 0
footer = "\n<!-- Condensed by PEtFiSh. Full rules: AGENTS.md -->"
footer_tokens = len(footer) // 4

for name, pri, text in p0:
    tokens = len(text) // 4
    result_parts.append(text)
    used_tokens += tokens

budget = max_tokens - footer_tokens
for name, pri, text in p1:
    tokens = len(text) // 4
    if used_tokens + tokens <= budget:
        result_parts.append(text)
        used_tokens += tokens
    else:
        lines = text.split('\n')
        snippet_lines = []
        found_content = False
        for l in lines:
            snippet_lines.append(l)
            if found_content and l.strip() == '':
                break
            if l.strip():
                found_content = True
        snippet = '\n'.join(snippet_lines)
        snippet_tokens = len(snippet) // 4
        if used_tokens + snippet_tokens <= budget:
            result_parts.append(snippet)
            used_tokens += snippet_tokens

output = '\n'.join(result_parts) + footer
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output)
'@

    $tempScript = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.py'
    [System.IO.File]::WriteAllText($tempScript, $pyScript, [System.Text.Encoding]::UTF8)

    try {
        & python3 $tempScript $maxTokens $tempInput $tempOutput 2>$null
        if ($LASTEXITCODE -ne 0) {
            & python $tempScript $maxTokens $tempInput $tempOutput 2>$null
        }
        if (Test-Path $tempOutput) {
            $result = [System.IO.File]::ReadAllText($tempOutput, [System.Text.Encoding]::UTF8)
            return $result
        }
    } finally {
        Remove-Item $tempInput -Force -ErrorAction SilentlyContinue
        Remove-Item $tempOutput -Force -ErrorAction SilentlyContinue
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }

    return $content
}

function Update-TranslatedInstructions([string]$sourceFile, [string]$destinationFile, [string]$platformName) {
    $cfg = Get-PlatformConfig $platformName
    $translation = $cfg.InstructionsTranslation
    if (-not $translation) { return $null }
    if (-not (Test-Path $sourceFile)) { return $null }

    $sourceContent = (Get-Content $sourceFile -Raw -Encoding UTF8).TrimEnd()
    $translatedContent = $sourceContent

    switch ($translation.method) {
        "rename_with_header" {
            $translatedContent = "<!-- Generated by PEtFiSh from AGENTS.md -->`n$sourceContent"
        }
        "wrap_as_mdc" {
            $translatedContent = "---`ndescription: `"PEtFiSh project instructions`"`nalwaysApply: true`n---`n$sourceContent"
        }
        default {
            return $null
        }
    }

    $parentDir = Split-Path -Parent $destinationFile
    if ($parentDir -and -not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    $tempFile = [System.IO.Path]::GetTempFileName()
    try {
        Set-Content -Path $tempFile -Value $translatedContent -NoNewline -Encoding UTF8
        return Merge-AgentsMd $tempFile $destinationFile "translation-$platformName" -ForceOverwrite:$true
    }
    finally {
        if (Test-Path $tempFile) {
            Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
        }
    }
}

function New-SecondaryInstructions([string]$targetPath, [switch]$ForceOverwrite, [string[]]$detectedPlatforms) {
    $primaryInstructions = Join-Path $targetPath "AGENTS.md"
    if (-not (Test-Path $primaryInstructions)) { return }

    Write-Host ""
    Write-Host "  [translate] Generating instruction files for detected platforms..." -ForegroundColor DarkCyan

    foreach ($platformName in $detectedPlatforms) {
        if ($platformName -eq $Platform) { continue }

        $cfg = Get-PlatformConfig $platformName
        $translation = $cfg.InstructionsTranslation
        if (-not $translation -or -not $translation.PSObject.Properties["target"]) { continue }
        $transTarget = $translation.target
        if ([string]::IsNullOrWhiteSpace($transTarget) -or $transTarget -eq "AGENTS.md") { continue }

        $dstTranslated = Join-Path $targetPath $transTarget

        $condenseConfig = $null
        $platformData = $PlatformRegistry.platforms.PSObject.Properties[$platformName].Value
        if ($platformData -and $platformData.PSObject.Properties["condense"]) {
            $condenseConfig = $platformData.condense
        }

        $sourceToTranslate = $primaryInstructions
        if ($condenseConfig -and $condenseConfig.max_tokens -gt 0) {
            $fullContent = Get-Content $primaryInstructions -Raw -Encoding UTF8
            $condensed = Compress-InstructionContent $fullContent $condenseConfig.max_tokens
            $tempFile = [System.IO.Path]::GetTempFileName()
            [System.IO.File]::WriteAllText($tempFile, $condensed, [System.Text.Encoding]::UTF8)
            $sourceToTranslate = $tempFile
        }

        $translatedResult = Update-TranslatedInstructions $sourceToTranslate $dstTranslated $platformName

        if ($sourceToTranslate -ne $primaryInstructions) {
            Remove-Item $sourceToTranslate -Force -ErrorAction SilentlyContinue
        }

        switch ($translatedResult) {
            "created" { Write-Host "    + $transTarget (created for $platformName)" -ForegroundColor DarkGreen }
            "merged"  { Write-Host "    + $transTarget (merged for $platformName)" -ForegroundColor DarkGreen }
            "updated" { Write-Host "    + $transTarget (updated for $platformName)" -ForegroundColor DarkGreen }
            "exists"  { Write-Warning "    SKIP $transTarget (exists for $platformName)" }
        }
    }
}

function Convert-OpencodeExampleToClaudeSettings([string]$srcFile, [string]$dstFile) {
    if (Test-Path $dstFile) {
        return "exists"
    }

    $src = Get-Content $srcFile -Raw -Encoding UTF8 | ConvertFrom-Json
    $permissions = [ordered]@{}

    if ($src.PSObject.Properties["permission"] -and $src.permission.PSObject.Properties["skill"]) {
        foreach ($skill in $src.permission.skill.PSObject.Properties) {
            $mode = "$($skill.Value)"
            if ($mode -in @("allow", "ask", "deny")) {
                if (-not $permissions.ContainsKey($mode)) {
                    $permissions[$mode] = @()
                }
                $permissions[$mode] += "Skill($($skill.Name))"
            }
        }
    }

    $dst = [ordered]@{
        '$schema' = "https://json.schemastore.org/claude-code-settings.json"
    }
    if ($permissions.Count -gt 0) {
        $dst.permissions = $permissions
    }

    $parentDir = Split-Path -Parent $dstFile
    if ($parentDir -and -not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    $dst | ConvertTo-Json -Depth 10 | Set-Content $dstFile -Encoding UTF8
    return "created"
}

function Get-PackFullName([string]$name) {
    if ($Aliases.ContainsKey($name)) { return $Aliases[$name] }
    if (Test-Path (Join-Path $PacksDir $name)) { return $name }
    Write-Error "Unknown pack: '$name'. Use -List to see available packs."
    exit 1
}

function Get-AllPacks {
    Get-ChildItem -Path $PacksDir -Directory | ForEach-Object { $_.Name }
}

function Show-PackList {
    Write-Host "`nAvailable packs:" -ForegroundColor Cyan
    Write-Host ("-" * 60)
    foreach ($dir in (Get-AllPacks)) {
        $alias = ($Aliases.GetEnumerator() | Where-Object { $_.Value -eq $dir } | Select-Object -First 1).Key
        $manifest = Join-Path (Join-Path $PacksDir $dir) "pack-manifest.json"
        $info = ""
        if (Test-Path $manifest) {
            $m = Get-Content $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
            $info = "  skills=$($m.skill_count)"
            if ($m.PSObject.Properties['command_count']) { $info += " cmds=$($m.command_count)" }
            if ($m.PSObject.Properties['agent_count'])   { $info += " agents=$($m.agent_count)" }
        }
        $aliasLabel = if ($alias) { " (alias: $alias)" } else { "" }
        Write-Host "  $dir$aliasLabel$info"
    }
    Write-Host ""
}

function Get-RestartHint([string]$platformName) {
    switch ($platformName) {
        "opencode" { return '⚠️  Restart needed. Exit: Ctrl+C | Resume: opencode -s <session_id>' }
        "claude" { return '⚠️  Restart needed. Exit: /exit or Ctrl+C | Resume: claude --continue' }
        "codex" { return '⚠️  Restart needed. Exit: Ctrl+C' }
        "cursor" { return '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"' }
        "copilot" { return '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"' }
        "windsurf" { return '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"' }
        "antigravity" { return '⚠️  Restart needed. Exit: Ctrl+C' }
        default { return $null }
    }
}

# --- Install function for a given platform ---

function Install-ForPlatform([string]$platformName, [string[]]$packs, [string]$targetPath, [switch]$ForceInstall) {
    $cfg = Get-PlatformConfig $platformName
    $targetSkills = if ($cfg.SkillsDir) { Join-Path $targetPath $cfg.SkillsDir } else { $null }
    $targetAgents = if ($cfg.AgentsDir) { Join-Path $targetPath $cfg.AgentsDir } else { $null }
    $targetCommands = if ($cfg.CommandsDir) { Join-Path $targetPath $cfg.CommandsDir } else { $null }
    $targetRegistry = if ($cfg.RegistryDir) { Join-Path $targetPath $cfg.RegistryDir } else { $null }

    Write-Host "`n[$platformName] Installing..." -ForegroundColor Magenta

    $script:installed = 0
    $script:skipped = 0

    foreach ($packName in $packs) {
        $packOpencode = Join-Path (Join-Path $PacksDir $packName) ".opencode"
        if (-not (Test-Path $packOpencode)) {
            Write-Warning "Pack '$packName' has no .opencode/ directory. Skipping."
            continue
        }

        Write-Host "`n  Installing pack: $packName" -ForegroundColor Green

        $packRoot = Join-Path $PacksDir $packName
        $manifestFile = Join-Path $packRoot "pack-manifest.json"
        $forceThisPack = $ForceInstall

        if (-not $forceThisPack) {
            $versionState = Compare-PackVersion $targetRegistry $packName $manifestFile
            $skipPack = $false
            switch ($versionState) {
                "same" {
                    Write-Warning "  ✓ $packName v$($script:ComparePackVersionInstalledVersion) is current. Use -Force/-force to reinstall."
                    $script:skipped++
                    $skipPack = $true
                }
                "newer" {
                    Write-Host "  ⬆ Upgrading $packName v$($script:ComparePackVersionInstalledVersion) → v$($script:ComparePackVersionSourceVersion)" -ForegroundColor Cyan
                    $forceThisPack = $true
                }
            }
            if ($skipPack) { continue }
        }

        # --- Merge AGENTS.md ---
        $agentsMd = Join-Path $packRoot "AGENTS.md"
        if (Test-Path $agentsMd) {
            # Tiered AGENTS.md: on opencode, packs with L1 rules files skip inline merge
            $hasL1 = $false
            if ($platformName -eq "opencode") {
                $L1Packs = @("opencode-course-skills-pack","repo-deploy-ops-skill-pack","petfish-style-skill","petfish-companion-skill","anti-sycophancy-calibration-pack","fish-trail","research-skill-pack")
                $hasL1 = $L1Packs -contains $packName
            }

            if ($hasL1) {
                # L1-only: write standalone rules file, skip inline merge
                Write-PackRulesFile $agentsMd $targetPath $packName
                # Deliver system-prompt-rules plugin (idempotent, runs for each L1 pack)
                Install-PluginFile $PSScriptRoot $targetPath
                Register-PluginInConfig (Join-Path $targetPath "opencode.json")
                # v0.10.x → v0.11.x migration: remove old inline section from AGENTS.md
                Remove-InlinePackSection (Join-Path $targetPath "AGENTS.md") $packName $manifestFile
            } else {
                # Non-opencode or packs without L1: merge inline as before
                $dstAgents = Join-Path $targetPath "AGENTS.md"
                $result = Merge-AgentsMd $agentsMd $dstAgents $packName -ForceOverwrite:$forceThisPack -ManifestFile $manifestFile
                switch ($result) {
                    "created"  { Write-Host "    + AGENTS.md (created)" -ForegroundColor DarkGreen; $script:installed++ }
                    "merged"   { Write-Host "    + AGENTS.md (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                    "updated"  { Write-Host "    + AGENTS.md (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                    "exists"   { Write-Warning "    SKIP AGENTS.md (pack section exists, use -Force to update)"; $script:skipped++ }
                }
            }

            # Antigravity: also create/merge GEMINI.md
            if ($cfg.GeminiMd) {
                $dstGemini = Join-Path $targetPath "GEMINI.md"
                $result = Merge-AgentsMd $agentsMd $dstGemini $packName -ForceOverwrite:$forceThisPack -ManifestFile $manifestFile
                switch ($result) {
                    "created"  { Write-Host "    + GEMINI.md (created)" -ForegroundColor DarkGreen; $script:installed++ }
                    "merged"   { Write-Host "    + GEMINI.md (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                    "updated"  { Write-Host "    + GEMINI.md (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                    "exists"   { Write-Warning "    SKIP GEMINI.md (pack section exists, use -Force to update)"; $script:skipped++ }
                }
            }
        }

        # --- Platform-specific config handling ---
        if ($cfg.ConfigFile) {
            $ocExample = Join-Path $packRoot "opencode.example.json"
            if (Test-Path $ocExample) {
                switch ($platformName) {
                    "opencode" {
                        $dstOc = Join-Path $targetPath $cfg.ConfigFile
                        $result = Merge-OpencodeJson $ocExample $dstOc -ForceOverwrite:$forceThisPack -SkillsDir $cfg.SkillsDir
                        switch ($result) {
                            "created" { Write-Host "    + $($cfg.ConfigFile) (created from example)" -ForegroundColor DarkGreen; $script:installed++ }
                            "merged"  { Write-Host "    + $($cfg.ConfigFile) (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                        }
                    }
                    "claude" {
                        $dstClaude = Join-Path $targetPath $cfg.ConfigFile
                        $result = Convert-OpencodeExampleToClaudeSettings $ocExample $dstClaude
                        switch ($result) {
                            "created" { Write-Host "    + $($cfg.ConfigFile) (created from opencode.example.json)" -ForegroundColor DarkGreen; $script:installed++ }
                            "exists"  { Write-Warning "    SKIP $($cfg.ConfigFile) (exists, not auto-merging)"; $script:skipped++ }
                        }
                    }
                    "codex" {
                        Write-Host "    - $($cfg.ConfigFile) (skipped: TOML config not auto-translated)" -ForegroundColor DarkGray
                    }
                }
            }
        }

        # --- Update installed-packs registry ---
        Update-InstalledPacks $targetRegistry $packName $manifestFile
        Write-Host "    + $($cfg.RegistryDir)/installed-packs.json (registry updated)" -ForegroundColor DarkGreen

        # --- Copy skills ---
        $srcSkills = Join-Path $packOpencode "skills"
        if ($targetSkills -and (Test-Path $srcSkills)) {
            if (-not (Test-Path $targetSkills)) {
                New-Item -ItemType Directory -Path $targetSkills -Force | Out-Null
            }
            foreach ($item in (Get-ChildItem -Path $srcSkills -Directory)) {
                $dstItem = Join-Path $targetSkills $item.Name
                if ((Test-Path $dstItem) -and -not $forceThisPack) {
                    Write-Warning "    SKIP skills/$($item.Name) (exists, use -Force to overwrite)"
                    $script:skipped++
                    continue
                }
                if (Test-Path $dstItem) { Remove-Item -Path $dstItem -Recurse -Force }
                Copy-Item -Path $item.FullName -Destination $dstItem -Recurse
                Write-Host "    + skills/$($item.Name)" -ForegroundColor DarkGreen
                $script:installed++
            }
        }

        # --- Copy agents → platform agents dir ---
        $srcAgents = Join-Path $packOpencode "agents"
        if ($targetAgents -and (Test-Path $srcAgents)) {
            if (-not (Test-Path $targetAgents)) {
                New-Item -ItemType Directory -Path $targetAgents -Force | Out-Null
            }
            foreach ($item in (Get-ChildItem -Path $srcAgents -Directory)) {
                $dstItem = Join-Path $targetAgents $item.Name
                if ((Test-Path $dstItem) -and -not $forceThisPack) {
                    Write-Warning "    SKIP agents/$($item.Name) (exists, use -Force to overwrite)"
                    $script:skipped++
                    continue
                }
                if (Test-Path $dstItem) { Remove-Item -Path $dstItem -Recurse -Force }
                Copy-Item -Path $item.FullName -Destination $dstItem -Recurse
                Write-Host "    + agents/$($item.Name)" -ForegroundColor DarkGreen
                $script:installed++
            }
        }

        # --- Copy commands → platform commands dir ---
        $srcCommands = Join-Path $packOpencode "commands"
        if ($targetCommands -and (Test-Path $srcCommands)) {
            if (-not (Test-Path $targetCommands)) {
                New-Item -ItemType Directory -Path $targetCommands -Force | Out-Null
            }
            foreach ($item in (Get-ChildItem -Path $srcCommands -Directory)) {
                $dstItem = Join-Path $targetCommands $item.Name
                if ((Test-Path $dstItem) -and -not $forceThisPack) {
                    Write-Warning "    SKIP commands/$($item.Name) (exists, use -Force to overwrite)"
                    $script:skipped++
                    continue
                }
                if (Test-Path $dstItem) { Remove-Item -Path $dstItem -Recurse -Force }
                Copy-Item -Path $item.FullName -Destination $dstItem -Recurse
                Write-Host "    + commands/$($item.Name)" -ForegroundColor DarkGreen
                $script:installed++
            }
        }

        # --- Copy Claude hooks (if platform is claude and pack has hooks) ---
        if ($platformName -eq "claude") {
            $srcHooks = Join-Path $packRoot ".claude" "hooks"
            if (Test-Path $srcHooks) {
                $targetHooks = Join-Path $targetPath ".claude" "hooks"
                if (-not (Test-Path $targetHooks)) { New-Item -ItemType Directory -Path $targetHooks -Force | Out-Null }
                foreach ($hookFile in (Get-ChildItem $srcHooks -File)) {
                    $dstHook = Join-Path $targetHooks $hookFile.Name
                    if ((Test-Path $dstHook) -and -not $forceThisPack) {
                        Write-Warning "    SKIP hooks/$($hookFile.Name) (exists, use -Force to overwrite)"
                        $script:skipped++
                        continue
                    }
                    Copy-Item $hookFile.FullName $dstHook -Force
                    Write-Host "    + hooks/$($hookFile.Name)" -ForegroundColor DarkGreen
                    $script:installed++
                }

                # --- Merge hooks into .claude/settings.json ---
                $claudeSettings = Join-Path $targetPath ".claude" "settings.json"
                $hooksConfig = @{
                    hooks = @{
                        UserPromptSubmit = @(@{ hooks = @(@{ type = "command"; command = "bash .claude/hooks/fish-trail-gateway.sh"; timeout = 5 }) })
                        PreCompact = @(@{ hooks = @(@{ type = "command"; command = "bash .claude/hooks/fish-trail-precompact.sh"; timeout = 5 }) })
                        PostCompact = @(@{ hooks = @(@{ type = "command"; command = "bash .claude/hooks/fish-trail-postcompact.sh"; timeout = 5 }) })
                    }
                }
                
                $existingSettings = @{}
                if (Test-Path $claudeSettings) {
                    try {
                        $existingSettings = Get-Content $claudeSettings -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
                    } catch {
                        $existingSettings = @{}
                    }
                }
                
                if (-not $existingSettings.ContainsKey('hooks')) {
                    $existingSettings['hooks'] = @{}
                }
                
                foreach ($eventName in $hooksConfig.hooks.Keys) {
                    if (-not $existingSettings['hooks'].ContainsKey($eventName)) {
                        $existingSettings['hooks'][$eventName] = $hooksConfig.hooks[$eventName]
                    } else {
                        # Check for duplicates
                        $existingCommands = @()
                        foreach ($group in $existingSettings['hooks'][$eventName]) {
                            foreach ($hook in $group.hooks) {
                                if ($hook.command) { $existingCommands += $hook.command }
                            }
                        }
                        foreach ($group in $hooksConfig.hooks[$eventName]) {
                            foreach ($hook in $group.hooks) {
                                if ($hook.command -and $hook.command -notin $existingCommands) {
                                    $existingSettings['hooks'][$eventName] += $group
                                }
                            }
                        }
                    }
                }
                
                $settingsDir = Split-Path $claudeSettings -Parent
                if (-not (Test-Path $settingsDir)) { New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null }
                $existingSettings | ConvertTo-Json -Depth 10 | Set-Content $claudeSettings -Encoding UTF8 -NoNewline
                Write-Host "    + .claude/settings.json (hooks merged)" -ForegroundColor DarkGreen
                $script:installed++
            }
        }
    }

    Write-Host "`n  [$platformName] Done: $($script:installed) installed, $($script:skipped) skipped." -ForegroundColor Cyan
    if ($script:installed -gt 0) {
        $restartHint = Get-RestartHint $platformName
        if ($restartHint) {
            Write-Host $restartHint -ForegroundColor Yellow
        }
    }
}

function Install-GlobalForPlatform([string]$platformName, [string[]]$packs, [switch]$ForceInstall) {
    $cfg = Get-GlobalPlatformConfig $platformName
    $targetSkills = $cfg.SkillsDir
    $targetRegistry = $cfg.RegistryDir

    if (-not $targetSkills) {
        Write-Warning "$platformName does not support global skill installation. Skipping."
        return
    }

    if (-not (Test-Path $targetSkills)) {
        New-Item -ItemType Directory -Path $targetSkills -Force | Out-Null
    }

    Write-Host "`n[$platformName] Global installing..." -ForegroundColor Magenta
    Write-Host "  Global skills dir: $targetSkills" -ForegroundColor DarkCyan
    Write-Host "  Global commands dir: $(if ($cfg.CommandsDir) { $cfg.CommandsDir } else { '<not supported>' })" -ForegroundColor DarkCyan

    $script:installed = 0
    $script:skipped = 0

    foreach ($packName in $packs) {
        $packOpencode = Join-Path (Join-Path $PacksDir $packName) ".opencode"
        if (-not (Test-Path $packOpencode)) {
            Write-Warning "Pack '$packName' has no .opencode/ directory. Skipping."
            continue
        }

        Write-Host "`n  Installing pack: $packName" -ForegroundColor Green

        $packRoot = Join-Path $PacksDir $packName
        $manifestFile = Join-Path $packRoot "pack-manifest.json"
        $forceThisPack = $ForceInstall

        if (-not $forceThisPack) {
            $versionState = Compare-PackVersion $targetRegistry $packName $manifestFile
            $skipPack = $false
            switch ($versionState) {
                "same" {
                    Write-Warning "  ✓ $packName v$($script:ComparePackVersionInstalledVersion) is current. Use -Force/-force to reinstall."
                    $script:skipped++
                    $skipPack = $true
                }
                "newer" {
                    Write-Host "  ⬆ Upgrading $packName v$($script:ComparePackVersionInstalledVersion) → v$($script:ComparePackVersionSourceVersion)" -ForegroundColor Cyan
                    $forceThisPack = $true
                }
            }
            if ($skipPack) { continue }
        }

        $srcSkills = Join-Path $packOpencode "skills"
        if (-not (Test-Path $srcSkills)) {
            Write-Warning "Pack '$packName' has no .opencode/skills/ directory. Skipping."
            continue
        }

        foreach ($item in (Get-ChildItem -Path $srcSkills -Directory)) {
            $dstItem = Join-Path $targetSkills $item.Name
            if ((Test-Path $dstItem) -and -not $forceThisPack) {
                Write-Warning "    SKIP skills/$($item.Name) (exists, use -Force to overwrite)"
                $script:skipped++
                continue
            }
            if (Test-Path $dstItem) { Remove-Item -Path $dstItem -Recurse -Force }
            Copy-Item -Path $item.FullName -Destination $dstItem -Recurse
            Write-Host "    + skills/$($item.Name)" -ForegroundColor DarkGreen
            $script:installed++
        }

        # --- Copy commands to global commands dir ---
        $srcCommands = Join-Path $packOpencode "commands"
        if ($cfg.CommandsDir -and (Test-Path $srcCommands)) {
            $targetCommands = $cfg.CommandsDir
            if (-not (Test-Path $targetCommands)) {
                New-Item -ItemType Directory -Path $targetCommands -Force | Out-Null
            }
            foreach ($item in (Get-ChildItem -Path $srcCommands)) {
                $dstItem = Join-Path $targetCommands $item.Name
                if ((Test-Path $dstItem) -and -not $forceThisPack) {
                    Write-Warning "    SKIP commands/$($item.Name) (exists, use -Force to overwrite)"
                    $script:skipped++
                    continue
                }
                if ($item.PSIsContainer) {
                    if (Test-Path $dstItem) { Remove-Item -Path $dstItem -Recurse -Force }
                    Copy-Item -Path $item.FullName -Destination $dstItem -Recurse
                } else {
                    Copy-Item -Path $item.FullName -Destination $dstItem -Force
                }
                Write-Host "    + commands/$($item.Name)" -ForegroundColor DarkGreen
                $script:installed++
            }
        }

        if ($targetRegistry) {
            Update-InstalledPacks $targetRegistry $packName $manifestFile
            Write-Host "    + $($cfg.RegistryDir)/installed-packs.json (registry updated)" -ForegroundColor DarkGreen
        }
    }

    Write-Host "`n  [$platformName] Done: $($script:installed) installed, $($script:skipped) skipped." -ForegroundColor Cyan
    if ($script:installed -gt 0) {
        $restartHint = Get-RestartHint $platformName
        if ($restartHint) {
            Write-Host $restartHint -ForegroundColor Yellow
        }
    }
}

# --- List mode ---
if ($List) {
    Show-PackList
    exit 0
}

if (-not $Pack) {
    Write-Error "Missing -Pack parameter. Use -List to see available packs, or -Pack all."
    exit 1
}

# --- Uninstall mode ---
if ($Uninstall) {
    if ($Pack -eq "all") {
        Write-Error "Uninstall does not support -Pack all. Specify packs individually: -Pack course,deploy"
        exit 1
    }

    $packItems = ($Pack -split ',') | ForEach-Object { $_.Trim() } | Where-Object { $_ }

    if (-not $Global) {
        $Target = (Resolve-Path $Target -ErrorAction Stop).Path
    }

    foreach ($alias in $packItems) {
        if ($Global) {
            Uninstall-GlobalPack $alias
        } else {
            Uninstall-Pack $alias $Target
        }
    }
    exit 0
}

# --- Resolve packs to install ---
$packsToInstall = if ($Pack -eq "all") {
    Get-AllPacks
} else {
    $Pack -split ',' | ForEach-Object { Get-PackFullName $_.Trim() }
}

$packItems = ($Pack -split ',') | ForEach-Object { $_.Trim() }
if (($packItems -contains "init" -or $packItems -contains "project-initializer-skill") -and -not $GlobalExplicitlyPassed -and -not $TargetExplicitlyPassed) {
    $Global = $true
    Write-Host "  [info] init pack defaults to global install. Use -Target to install locally." -ForegroundColor DarkCyan
}

# --- Resolve target ---
$script:DetectedPlatforms = @()
if ($Detect) {
    $detectTarget = (Resolve-Path $Target -ErrorAction Stop).Path
    if ($PlatformExplicitlyPassed) {
        $script:DetectedPlatforms = Get-AllDetectedPlatforms $detectTarget
        Write-Host "  [detect] Primary platform: $Platform (explicit)" -ForegroundColor DarkCyan
        Write-Host "  [detect] All detected platforms: $($script:DetectedPlatforms -join ', ')" -ForegroundColor DarkCyan
    } else {
        $script:DetectedPlatforms = Get-AllDetectedPlatforms $detectTarget
        $Platform = $script:DetectedPlatforms[0]
        Write-Host "  [detect] Detected primary platform: $Platform" -ForegroundColor DarkCyan
        if ($script:DetectedPlatforms.Count -gt 1) {
            Write-Host "  [detect] Also detected: $($script:DetectedPlatforms[1..($script:DetectedPlatforms.Count-1)] -join ', ')" -ForegroundColor DarkCyan
        }
    }
}

if (-not $Global) {
    $Target = (Resolve-Path $Target -ErrorAction Stop).Path
}

# --- Install for selected platform(s) ---
$platforms = Get-PlatformsForSelection $Platform

foreach ($p in $platforms) {
    if ($Global) {
        Install-GlobalForPlatform $p $packsToInstall -ForceInstall:$Force
    } else {
        Install-ForPlatform $p $packsToInstall $Target -ForceInstall:$Force
    }
}

# --- Generate instruction files for secondary detected platforms ---
if ($script:DetectedPlatforms.Count -gt 0 -and -not $Global) {
    New-SecondaryInstructions $Target -ForceOverwrite:$Force -detectedPlatforms $script:DetectedPlatforms
}
