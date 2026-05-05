# 胖鱼 PEtFiSh - Remote installer for AI coding platform skill packs from GitHub.
# Usage: & ([scriptblock]::Create((irm <url>))) -Pack course [-Platform opencode] [-Target .] [-Force] [-Global]
[CmdletBinding()]
param(
    [string]$Pack,
    [string]$Target = ".",
    [ValidateSet("opencode", "claude", "codex", "cursor", "copilot", "windsurf", "antigravity", "universal", "all", "primary", "ide", "cli")]
    [string]$Platform = "opencode",
    [switch]$Detect,
    [switch]$Force,
    [switch]$List,
    [switch]$Global,
    [string]$Repo = "kylecui/petfish.ai",
    [string]$Branch = "master",
    [string]$GitHubToken
)

$ErrorActionPreference = "Stop"

# Auto-resolve latest release tag if -Branch not explicitly passed
if (-not $PSBoundParameters.ContainsKey('Branch')) {
    try {
        $apiUrl = "https://api.github.com/repos/$Repo/releases/latest"
        $headers = if ($GitHubToken) { @{ Authorization = "token $GitHubToken" } } else { @{} }
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers -ErrorAction Stop
        if ($response -and $response.tag_name) {
            $Branch = $response.tag_name
        }
    } catch {
        # Silently fall back to "master" on any error
    }
}

if (-not $List) {
    Write-Host ""
    Write-Host "  ><(((^>  胖鱼 PEtFiSh" -ForegroundColor DarkCyan
    Write-Host "  [胖鱼 PEtFiSh] AI Worker's Companion — Self-adaptive Skill Installer (remote)" -ForegroundColor Cyan
    Write-Host "  Initialize -> Auto-install -> Work immediately" -ForegroundColor DarkGray
    Write-Host ""
}

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

$GlobalExplicitlyPassed = $PSBoundParameters.ContainsKey("Global")
$TargetExplicitlyPassed = $PSBoundParameters.ContainsKey("Target")
$PlatformExplicitlyPassed = $PSBoundParameters.ContainsKey("Platform")

$PlatformRegistry = $null
$packsDir = $null

# --- Pack alias registry ---
$Aliases = @{
    "course"    = "opencode-course-skills-pack"
    "testdocs"  = "opencode-skill-pack-testcases-usage-docs"
    "deploy"    = "repo-deploy-ops-skill-pack"
    "init"      = "project-initializer-skill"
    "petfish"   = "petfish-style-skill"
    "companion" = "petfish-companion-skill"
    "ppt"       = "opencode-ppt-skills"
    "trust"     = "trustskills-governance-pack"
    "calibrate" = "anti-sycophancy-calibration-pack"
    "context"   = "fish-trail"
    "fish-init"      = "project-initializer-skill"
    "fish-core"      = "petfish-companion-skill"
    "fish-course"    = "opencode-course-skills-pack"
    "fish-testdocs"  = "opencode-skill-pack-testcases-usage-docs"
    "fish-deploy"    = "repo-deploy-ops-skill-pack"
    "fish-style"     = "petfish-style-skill"
    "fish-slides"    = "opencode-ppt-skills"
    "fish-calibrate" = "anti-sycophancy-calibration-pack"
    "fish-trail"     = "fish-trail"
}

$AllPacks = @(
    "opencode-course-skills-pack",
    "opencode-skill-pack-testcases-usage-docs",
    "repo-deploy-ops-skill-pack",
    "project-initializer-skill",
    "petfish-style-skill",
    "petfish-companion-skill",
    "opencode-ppt-skills",
    "trustskills-governance-pack",
    "anti-sycophancy-calibration-pack",
    "fish-trail"
)

$PackDisplayOrder = @(
    @{ Name = "opencode-course-skills-pack"; Alias = "course, fish-course" },
    @{ Name = "opencode-skill-pack-testcases-usage-docs"; Alias = "testdocs, fish-testdocs" },
    @{ Name = "repo-deploy-ops-skill-pack"; Alias = "deploy, fish-deploy" },
    @{ Name = "project-initializer-skill"; Alias = "init, fish-init" },
    @{ Name = "petfish-style-skill"; Alias = "petfish, fish-style" },
    @{ Name = "petfish-companion-skill"; Alias = "companion, fish-core" },
    @{ Name = "opencode-ppt-skills"; Alias = "ppt, fish-slides" },
    @{ Name = "trustskills-governance-pack"; Alias = "trust" },
    @{ Name = "anti-sycophancy-calibration-pack"; Alias = "calibrate, fish-calibrate" },
    @{ Name = "fish-trail"; Alias = "context, fish-trail" }
)

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
    foreach ($platformName in (Get-DetectionOrder)) {
        $cfg = Get-PlatformConfig $platformName
        foreach ($marker in $cfg.DetectMarkers) {
            if (-not [string]::IsNullOrWhiteSpace($marker)) {
                $markerPath = Join-Path $targetPath $marker
                if (Test-Path $markerPath) {
                    return $platformName
                }
            }
        }
    }
    Write-Host "  [detect] No platform marker found. Falling back to 'universal'. Use -Platform to specify explicitly." -ForegroundColor Yellow
    return "universal"
}

# --- Merge helpers ---

function Merge-AgentsMd([string]$srcFile, [string]$dstFile, [string]$packName, [switch]$ForceOverwrite) {
    $beginMarker = "<!-- BEGIN pack: $packName -->"
    $endMarker = "<!-- END pack: $packName -->"
    $srcContent = (Get-Content $srcFile -Raw -Encoding UTF8).TrimEnd()
    $wrappedContent = "$beginMarker`n$srcContent`n$endMarker"

    if (-not (Test-Path $dstFile)) {
        Set-Content -Path $dstFile -Value $wrappedContent -NoNewline -Encoding UTF8
        return "created"
    }

    $existing = Get-Content $dstFile -Raw -Encoding UTF8
    if ($existing -match [regex]::Escape($beginMarker)) {
        if (-not $ForceOverwrite) { return "exists" }
        $pattern = "(?s)" + [regex]::Escape($beginMarker) + ".*?" + [regex]::Escape($endMarker)
        $replaced = [regex]::Replace($existing, $pattern, $wrappedContent)
        Set-Content -Path $dstFile -Value $replaced -NoNewline -Encoding UTF8
        return "updated"
    }

    $merged = $existing.TrimEnd() + "`n`n" + $wrappedContent + "`n"
    Set-Content -Path $dstFile -Value $merged -NoNewline -Encoding UTF8
    return "merged"
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
        if ($m.PSObject.Properties['version']) { $entry.version = $m.version }
        if ($m.PSObject.Properties['skills']) { $entry.skills = $m.skills }
        if ($m.PSObject.Properties['description']) { $entry.description = $m.description }
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

function Resolve-PackName([string]$name) {
    if ($Aliases.ContainsKey($name)) { return $Aliases[$name] }
    if ($AllPacks -contains $name) { return $name }
    Write-Error "Unknown pack: '$name'. Use -List to see available packs, or -Pack all."
    exit 1
}

function Show-PackList {
    Write-Host "`nAvailable packs:" -ForegroundColor Cyan
    Write-Host ("-" * 60)
    foreach ($packInfo in $PackDisplayOrder) {
        Write-Host "  $($packInfo.Name) (alias: $($packInfo.Alias))"
    }
    Write-Host ""
}

function Get-RestartHint([string]$platformName) {
    switch ($platformName) {
        "opencode" { return '⚠️  Restart needed. Exit: Ctrl+C | Resume: opencode -s <session_id>' }
        "claude" { return '⚠️  Restart needed. Exit: /exit or Ctrl+C | Resume: claude --continue' }
        "codex" { return 'ℹ️  Restart may be needed. Skills might reload dynamically; if not, exit with Ctrl+C and re-launch.' }
        "cursor" { return '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"' }
        "copilot" { return '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"' }
        "windsurf" { return '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"' }
        "antigravity" { return '⚠️  Restart needed. Exit: Ctrl+C' }
        default { return $null }
    }
}

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
        $packOpencode = Join-Path (Join-Path $packsDir $packName) ".opencode"
        if (-not (Test-Path $packOpencode)) {
            Write-Warning "Pack '$packName' has no .opencode/ directory. Skipping."
            continue
        }

        Write-Host "`n  Installing pack: $packName" -ForegroundColor Green

        $packRoot = Join-Path $packsDir $packName
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

        $agentsMd = Join-Path $packRoot "AGENTS.md"
        if (Test-Path $agentsMd) {
            $dstAgents = Join-Path $targetPath "AGENTS.md"
            $result = Merge-AgentsMd $agentsMd $dstAgents $packName -ForceOverwrite:$forceThisPack
            switch ($result) {
                "created" { Write-Host "    + AGENTS.md (created)" -ForegroundColor DarkGreen; $script:installed++ }
                "merged"  { Write-Host "    + AGENTS.md (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                "updated" { Write-Host "    + AGENTS.md (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                "exists"  { Write-Warning "    SKIP AGENTS.md (pack section exists, use -Force to update)"; $script:skipped++ }
            }

            $translation = $cfg.InstructionsTranslation
            $translationTarget = if ($translation -and $translation.PSObject.Properties["target"]) { $translation.target } else { $cfg.InstructionsFile }
            if ($translation -and $translationTarget -and $translationTarget -ne "AGENTS.md") {
                $dstTranslated = Join-Path $targetPath $translationTarget
                $translatedResult = Update-TranslatedInstructions $dstAgents $dstTranslated $platformName
                $translatedLabel = $translationTarget
                switch ($translatedResult) {
                    "created" { Write-Host "    + $translatedLabel (created)" -ForegroundColor DarkGreen; $script:installed++ }
                    "merged"  { Write-Host "    + $translatedLabel (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                    "updated" { Write-Host "    + $translatedLabel (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                    "exists"  { Write-Warning "    SKIP $translatedLabel (managed section exists, use -Force to update)"; $script:skipped++ }
                }
            }

            if ($cfg.GeminiMd) {
                $dstGemini = Join-Path $targetPath "GEMINI.md"
                $geminiResult = Merge-AgentsMd $agentsMd $dstGemini $packName -ForceOverwrite:$forceThisPack
                switch ($geminiResult) {
                    "created" { Write-Host "    + GEMINI.md (created)" -ForegroundColor DarkGreen; $script:installed++ }
                    "merged"  { Write-Host "    + GEMINI.md (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                    "updated" { Write-Host "    + GEMINI.md (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                    "exists"  { Write-Warning "    SKIP GEMINI.md (pack section exists, use -Force to update)"; $script:skipped++ }
                }
            }
        }

        if ($cfg.ConfigFile) {
            $ocExample = Join-Path $packRoot "opencode.example.json"
            if (Test-Path $ocExample) {
                switch ($platformName) {
                    "opencode" {
                        $dstConfig = Join-Path $targetPath $cfg.ConfigFile
                        $configResult = Merge-OpencodeJson $ocExample $dstConfig -ForceOverwrite:$forceThisPack -SkillsDir $cfg.SkillsDir
                        switch ($configResult) {
                            "created" { Write-Host "    + $($cfg.ConfigFile) (created from example)" -ForegroundColor DarkGreen; $script:installed++ }
                            "merged"  { Write-Host "    + $($cfg.ConfigFile) (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                        }
                    }
                    "claude" {
                        $dstConfig = Join-Path $targetPath $cfg.ConfigFile
                        $configResult = Convert-OpencodeExampleToClaudeSettings $ocExample $dstConfig
                        switch ($configResult) {
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

        Update-InstalledPacks $targetRegistry $packName $manifestFile
        Write-Host "    + $($cfg.RegistryDir)/installed-packs.json (registry updated)" -ForegroundColor DarkGreen

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
        $packOpencode = Join-Path (Join-Path $packsDir $packName) ".opencode"
        if (-not (Test-Path $packOpencode)) {
            Write-Warning "Pack '$packName' has no .opencode/ directory. Skipping."
            continue
        }

        Write-Host "`n  Installing pack: $packName" -ForegroundColor Green

        $packRoot = Join-Path $packsDir $packName
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

if ($List) {
    Show-PackList
    exit 0
}

if ($Detect -and $PlatformExplicitlyPassed) {
    Write-Error "-Detect cannot be used together with an explicit -Platform value."
    exit 1
}

if (-not $Pack) {
    Write-Error "Missing -Pack parameter. Use -List to see available packs, or -Pack all."
    exit 1
}

$packsToInstall = if ($Pack -eq "all") {
    $AllPacks
} else {
    $Pack -split ',' | ForEach-Object { Resolve-PackName $_.Trim() }
}

$packItems = ($Pack -split ',') | ForEach-Object { $_.Trim() }
if (($packItems -contains "init" -or $packItems -contains "project-initializer-skill") -and -not $GlobalExplicitlyPassed -and -not $TargetExplicitlyPassed) {
    $Global = $true
    Write-Host "  [info] init pack defaults to global install. Use -Target to install locally." -ForegroundColor DarkCyan
}

$tmpDir = Join-Path ([System.IO.Path]::GetTempPath()) "skill_builder_$(Get-Random)"
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

try {
     $platformsUrl = "https://raw.githubusercontent.com/$Repo/$Branch/platforms.json"
     $platformsPath = Join-Path $tmpDir "platforms.json"
     
     # Determine if $Branch is a tag (semver-like) or a branch name
     # Tags typically start with 'v' or match semver pattern (e.g., v1.0.0, 1.2.3)
     $isTag = $Branch -match '^v?\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?(\+[a-zA-Z0-9]+)?$'
     $archivePath = if ($isTag) { "archive/refs/tags/$Branch.zip" } else { "archive/refs/heads/$Branch.zip" }
     $tarballUrl = "https://github.com/$Repo/$archivePath"
     $zipPath = Join-Path $tmpDir "repo.zip"

    Write-Host "Downloading $Repo@$Branch..." -ForegroundColor Cyan

    $platformsRequest = @{ Uri = $platformsUrl; OutFile = $platformsPath }
    $zipRequest = @{ Uri = $tarballUrl; OutFile = $zipPath }
    if ($GitHubToken) {
        $headers = @{ Authorization = "token $GitHubToken" }
        $platformsRequest.Headers = $headers
        $zipRequest.Headers = $headers
    }

    Invoke-WebRequest @platformsRequest -UseBasicParsing
    Invoke-WebRequest @zipRequest -UseBasicParsing

    $PlatformRegistry = Get-Content $platformsPath -Raw -Encoding UTF8 | ConvertFrom-Json

    Write-Host "Extracting..."
    Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force

    $extractDir = Get-ChildItem -Path $tmpDir -Directory | Where-Object { $_.FullName -ne $tmpDir } | Select-Object -First 1
    if (-not $extractDir) {
        Write-Error "Failed to extract archive"
        exit 1
    }

    $packsDir = Join-Path $extractDir.FullName "packs"
    if (-not (Test-Path $packsDir)) {
        Write-Error "Downloaded repository does not contain a packs/ directory."
        exit 1
    }

    if ($Detect) {
        $detectTarget = (Resolve-Path $Target -ErrorAction Stop).Path
        $Platform = Get-DetectedPlatform $detectTarget
        Write-Host "  [detect] Detected platform: $Platform" -ForegroundColor DarkCyan
    }

    if (-not $Global) {
        $Target = (Resolve-Path $Target -ErrorAction Stop).Path
    }

    $platforms = Get-PlatformsForSelection $Platform
    foreach ($p in $platforms) {
        if ($Global) {
            Install-GlobalForPlatform $p $packsToInstall -ForceInstall:$Force
        } else {
            Install-ForPlatform $p $packsToInstall $Target -ForceInstall:$Force
        }
    }
}
finally {
    if (Test-Path $tmpDir) {
        Remove-Item -Path $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
