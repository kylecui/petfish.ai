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
    [switch]$Uninstall,
    [switch]$TrustScan,
    [string]$Repo = "kylecui/petfish.ai",
    [string]$Branch = "master",
    [string]$GitHubToken
)

$ErrorActionPreference = "Stop"

# --- UTF-8 output encoding ---
# Ensure console output uses UTF-8. Non-UTF-8 code pages (e.g., 437, 1252) cause
# Chinese text from market index and pack manifests to render as garbled Mojibake.
# This is a no-op when the console already uses UTF-8 (code page 65001).
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    # Silently continue if encoding setup fails (e.g., non-interactive host)
}

# --- Suppress progress bar for non-interactive downloads ---
# PS progress bar blocks pipeline and causes hangs in non-interactive hosts.
$ProgressPreference = 'SilentlyContinue'

# --- Version resolution ---
# Auto-detection of the latest release tag was removed because:
# 1. Piped scripts cannot detect the source URL — auto-detect overrides tagged URLs
# 2. The master branch always carries the latest stable code (release discipline)
# 3. It adds network latency and API rate-limit risk for no reliably correct gain
# To install a specific version: -Branch v1.1.0

if (-not $List) {
    Write-Host ""
    Write-Host "  ><(((^>  胖鱼 PEtFiSh" -ForegroundColor DarkCyan
    Write-Host "  [胖鱼 PEtFiSh] AI Worker's Companion — Self-adaptive Skill Installer (remote)" -ForegroundColor Cyan
    Write-Host "  Initialize -> Auto-install -> Work immediately" -ForegroundColor DarkGray
    Write-Host ""
}

# --- Uninstall rejection ---
if ($Uninstall) {
    Write-Host "[胖鱼 PEtFiSh] ❌ Uninstall is not supported via the remote installer." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Uninstall requires the local installer which has access to your project files." -ForegroundColor Yellow
    Write-Host "  Clone the repo and run:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    git clone https://github.com/$Repo.git" -ForegroundColor Cyan
    Write-Host "    .\install.ps1 -Pack <alias> -Uninstall [-Target <path>]" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[胖鱼 PEtFiSh] uv not found. Installing uv (required for Python-based skills)..." -ForegroundColor Yellow
    try {
        $uvInstallScript = (Invoke-RestMethod https://astral.sh/uv/install.ps1 -TimeoutSec 30)
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
$script:MarketMeta = @{}  # Maps pack_name → market index pack object for optional packs
$script:MarketPackDirs = @{}  # Maps pack_name → downloaded pack root for external market packs

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
    "fish-guard" = "trustskills-governance-pack"
    "calibrate" = "anti-sycophancy-calibration-pack"
    "context"   = "fish-trail"
    "research"  = "research-skill-pack"
    "reflect"   = "fish-reflection-pack"
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
    "fish-brain"     = "petfish-companion-skill"
    "toolchain"      = "petfish-toolchain-skill"
    "series-style"   = "series-style-governor-pack"
    "fat-slim"       = "petfish-pack-fat-slim-writer"
    "doc-reader"     = "doc-reader-skill"
}

$AllPacks = @(
    "opencode-course-skills-pack",
    "opencode-skill-pack-testcases-usage-docs",
    "repo-deploy-ops-skill-pack",
    "project-initializer-skill",
    "petfish-style-skill",
    "petfish-companion-skill",
    "petfish-toolchain-skill",
    "opencode-ppt-skills",
    "trustskills-governance-pack",
    "anti-sycophancy-calibration-pack",
    "fish-trail",
    "research-skill-pack",
    "fish-reflection-pack",
    "series-style-governor-pack",
    "doc-reader-skill"
)

$PackDisplayOrder = @(
    @{ Name = "opencode-course-skills-pack"; Alias = "course, fish-course" },
    @{ Name = "opencode-skill-pack-testcases-usage-docs"; Alias = "testdocs, fish-testdocs" },
    @{ Name = "repo-deploy-ops-skill-pack"; Alias = "deploy, fish-deploy" },
    @{ Name = "project-initializer-skill"; Alias = "init, fish-init" },
    @{ Name = "petfish-style-skill"; Alias = "petfish, fish-style" },
    @{ Name = "petfish-companion-skill"; Alias = "companion, fish-core, fish-brain" },
    @{ Name = "petfish-toolchain-skill"; Alias = "toolchain" },
    @{ Name = "opencode-ppt-skills"; Alias = "ppt, fish-slides" },
    @{ Name = "trustskills-governance-pack"; Alias = "trust, fish-guard" },
    @{ Name = "anti-sycophancy-calibration-pack"; Alias = "calibrate, fish-calibrate" },
    @{ Name = "fish-trail"; Alias = "context, fish-trail" },
    @{ Name = "research-skill-pack"; Alias = "research, fish-research" },
    @{ Name = "fish-reflection-pack"; Alias = "reflect, fish-reflect" },
    @{ Name = "series-style-governor-pack"; Alias = "series-style" },
    @{ Name = "doc-reader-skill"; Alias = "doc-reader" }
)

# --- Core pack classification ---
# Core packs are always sourced from the petfish.ai tarball.
# Optional packs are market-first (petfish-market index), with tarball fallback.
$CorePacks = @("project-initializer-skill", "petfish-companion-skill", "petfish-toolchain-skill", "fish-trail")

function Test-CorePack([string]$packName) {
    return $CorePacks -contains $packName
}

# --- Market index query ---
# Retrieves petfish-market index.json with mirror and curl.exe fallback.
function Get-MarketIndexData {
    $marketUrl = "https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json"
    $mirrorPrefixes = @(
        "",
        "https://ghfast.top/https://",
        "https://mirror.ghproxy.com/https://"
    )
    foreach ($prefix in $mirrorPrefixes) {
        $uri = "${prefix}${marketUrl}"
        $data = $null
        try {
            $data = Invoke-RestMethod -Uri $uri -TimeoutSec 30 -ErrorAction Stop
        } catch {
            try {
                $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
                if ($curl) {
                    $raw = & curl.exe -fsSL --max-time 30 $uri 2>$null
                    if ($LASTEXITCODE -eq 0 -and $raw) {
                        $data = ($raw -join "`n") | ConvertFrom-Json
                    }
                }
            } catch {
                $data = $null
            }
        }
        if (-not $data) { continue }
        return $data
    }
    return $null
}

# Queries petfish-market index.json for a pack by alias or name.
# Returns the matching pack object, or $null if not found or unavailable.
# Results are stored in $script:MarketMeta and used by the download path for optional packs.
function Query-MarketIndex([string]$PackAlias) {
    $data = Get-MarketIndexData
    if (-not $data) { return $null }
        foreach ($pack in @($data.packs)) {
            $aliases = @()
            if ($pack.PSObject.Properties['alias']) {
                foreach ($a in @($pack.alias)) {
                    if ($null -ne $a -and -not [string]::IsNullOrWhiteSpace("$a")) { $aliases += "$a" }
                }
            }
            if ($pack.PSObject.Properties['aliases']) {
                foreach ($a in @($pack.aliases)) {
                    if ($null -ne $a -and -not [string]::IsNullOrWhiteSpace("$a")) { $aliases += "$a" }
                }
            }
            if ($aliases -contains $PackAlias -or "$($pack.name)" -eq $PackAlias) {
                return $pack
            }
        }
    return $null
}

# --- Download an optional pack from its independent GitHub repo ---
# Extracts to a temp dir and stores the pack root in $script:MarketPackDirs[$packName].
function Download-MarketPack([string]$packName) {
    $meta = $script:MarketMeta[$packName]
    if (-not $meta) { return $false }

    $repo   = $meta.repo
    $ref    = if ($meta.ref)  { $meta.ref  } else { "main" }
    $subdir = if ($meta.path) { $meta.path } else { "" }

    $isTag = $ref -match '^v?\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?(\+[a-zA-Z0-9]+)?$'
    $archivePath = if ($isTag) { "archive/refs/tags/$ref.zip" } else { "archive/refs/heads/$ref.zip" }
    $archiveUrl = "https://github.com/$repo/$archivePath"

    $tmpPackDir = Join-Path ([System.IO.Path]::GetTempPath()) "petfish_market_$(Get-Random)"
    New-Item -ItemType Directory -Path $tmpPackDir -Force | Out-Null

    $zipFile = Join-Path $tmpPackDir "pack.zip"
    Write-Host "  [market] Downloading $packName from $repo@$ref..." -ForegroundColor DarkCyan

    $mirrorPrefixes = @(
        "",
        "https://ghfast.top/https://",
        "https://mirror.ghproxy.com/https://"
    )

    $downloaded = $false
    foreach ($prefix in $mirrorPrefixes) {
        $uri = "${prefix}${archiveUrl}"
        try {
            Invoke-WebRequest -Uri $uri -OutFile $zipFile -UseBasicParsing -TimeoutSec 60 -ErrorAction Stop
            $downloaded = $true
            break
        } catch {
            # Try next mirror
        }
    }

    if (-not $downloaded) {
        Write-Warning "  [market] Failed to download $packName from all mirrors. Falling back to main repo pack path."
        Remove-Item -Path $tmpPackDir -Recurse -Force -ErrorAction SilentlyContinue
        return $false
    }

    try {
        Expand-Archive -Path $zipFile -DestinationPath $tmpPackDir -Force
    } catch {
        Write-Warning "  [market] archive extraction failed for $packName. Falling back to main repo pack path."
        Remove-Item -Path $tmpPackDir -Recurse -Force -ErrorAction SilentlyContinue
        return $false
    }

    $extractRoot = Get-ChildItem -Path $tmpPackDir -Directory | Select-Object -First 1
    if (-not $extractRoot) {
        Write-Warning "  [market] Could not locate extracted directory for $packName."
        Remove-Item -Path $tmpPackDir -Recurse -Force -ErrorAction SilentlyContinue
        return $false
    }

    # Resolve market metadata path to the pack root (the directory containing .opencode/),
    # not the .opencode content directory itself.
    $packRoot = $extractRoot.FullName
    if ($subdir -and (Test-Path (Join-Path $packRoot $subdir))) {
        $packRoot = Join-Path $packRoot $subdir
    } elseif (Test-Path (Join-Path $packRoot $packName)) {
        $packRoot = Join-Path $packRoot $packName
    }
    if ((Split-Path $packRoot -Leaf) -eq ".opencode") {
        $packRoot = Split-Path $packRoot -Parent
    }

    $candidatePath = Join-Path (Join-Path (Join-Path $packRoot "packs") "optional") $packName
    if (Test-Path $candidatePath) { $packRoot = $candidatePath }

    $script:MarketPackDirs[$packName] = $packRoot
    Write-Host "  [market] $packName extracted to $packRoot" -ForegroundColor DarkGreen
    return $true
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
        Write-Host "  [detect] No platform marker found. Falling back to 'universal'. Use -Platform to specify explicitly." -ForegroundColor Yellow
        return @("universal")
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
        "fish-reflection-pack"               = "fish-reflection.md"
        "series-style-governor-pack"            = "series-style-governor.md"
    }
    $l1Name = $L1Map[$packName]
    if (-not $l1Name) { return }

    $rulesDir = Join-Path (Join-Path $targetDir ".opencode") "agents-rules"
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
    $srcPluginDir = Join-Path (Join-Path $sourceRoot "lib") "plugin"
    if (-not (Test-Path $srcPluginDir)) { return }

    $pluginDir = Join-Path (Join-Path $targetDir ".opencode") "plugin"
    if (-not (Test-Path $pluginDir)) {
        New-Item -ItemType Directory -Path $pluginDir -Force | Out-Null
    }
    Get-ChildItem -Path $srcPluginDir -Filter "*.ts" | Where-Object {
        # topic-detector.ts is inlined into system-prompt-context-inject.ts (#160/#161)
        # and must NOT be deployed as a standalone plugin (causes constructor crash)
        $_.Name -ne "topic-detector.ts"
    } | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination (Join-Path $pluginDir $_.Name) -Force
        Write-Host "    + .opencode/plugin/$($_.Name)" -ForegroundColor DarkGreen
    }
}

# Register plugin tuple in opencode.json (idempotent)
function Register-PluginInConfig([string]$configFile) {
    if (-not (Test-Path $configFile)) { return }

    $raw = Get-Content $configFile -Raw -Encoding UTF8
    $json = ConvertFrom-Json $raw

    $pluginsToRegister = @(
        @(".opencode/plugin/system-prompt-rules.ts", @{ mode = "all" }),
        @(".opencode/plugin/system-prompt-context-inject.ts", @{ maxTopics = 5; maxSummaryLen = 200 })
    )

    if (-not ($json.PSObject.Properties["plugin"])) {
        $json | Add-Member -NotePropertyName "plugin" -NotePropertyValue @()
    }

    $changed = $false
    foreach ($pt in $pluginsToRegister) {
        $pluginPath = $pt[0]
        $pluginOpts = $pt[1]
        $alreadyExists = $false
        foreach ($entry in $json.plugin) {
            if ($entry -is [array] -and $entry.Length -ge 1 -and $entry[0] -eq $pluginPath) {
                $alreadyExists = $true
                break
            }
        }
        if (-not $alreadyExists) {
            $tuple = @($pluginPath, $pluginOpts)
            $json.plugin = @($json.plugin) + ,@(,$tuple)
            $changed = $true
        }
    }

    if ($changed) {
        $json | ConvertTo-Json -Depth 10 | Set-Content $configFile -Encoding UTF8
        Write-Host "    + opencode.json (plugins registered)" -ForegroundColor DarkGreen
    }
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

function Migrate-LegacyV09([string]$TargetPath, [string]$SkillsDir, [string]$ConfigFile, [string]$RulesDir) {
    if (-not (Test-Path $TargetPath -PathType Container)) { return }

    $packRenames = @{
        'context-router-skill'          = 'fish-trail'
        'companion'                     = 'petfish-companion-skill'
        'toolchain'                     = 'petfish-toolchain-skill'
        'project-initializer'           = 'project-initializer-skill'
        'anti-sycophancy-calibration'   = 'anti-sycophancy-calibration-pack'
        'petfish-style-rewriter'        = 'petfish-style-skill'
        'skill-trust-governance'        = 'trustskills-governance-pack'
    }

    $skillRenames = @{
        'context-router'             = 'fish-trail'
        'petfish-companion'          = 'fish-brain'
        'marketplace-connector'      = 'fish-market'
        'project-initializer'        = 'fish-init'
        'anti-sycophancy-calibration'= 'fish-calibrate'
        'petfish-style-rewriter'     = 'fish-style'
        'skill-trust-governance'     = 'fish-guard'
    }

    $rulesRenames = @{
        'context-router.md' = 'fish-trail.md'
    }

    $migrated = $false

    # --- 1. Registry key renames ---
    $baseDirs = @($TargetPath, $HOME)
    foreach ($baseDir in $baseDirs) {
        $regFile = $null
        foreach ($candidate in @(
            (Join-Path (Join-Path $baseDir '.opencode') 'installed-packs.json'),
            (Join-Path (Join-Path $baseDir '.claude')   'installed-packs.json'),
            (Join-Path (Join-Path $baseDir '.agents')   'installed-packs.json')
        )) {
            if (Test-Path $candidate -PathType Leaf) { $regFile = $candidate; break }
        }
        if (-not $regFile) { continue }

        try {
            $reg = Get-Content $regFile -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch { continue }

        $packs = $reg.packs
        if ($null -eq $packs) { continue }

        # Normalize array format → dict
        if ($packs -isnot [System.Management.Automation.PSCustomObject]) {
            $newPacks = [PSCustomObject]@{}
            foreach ($item in @($packs)) {
                if ($item -is [string]) {
                    $newPacks | Add-Member -NotePropertyName $item -NotePropertyValue ([PSCustomObject]@{})
                }
            }
            $reg.packs = $newPacks
            $packs = $reg.packs
        }

        $changed = $false
        foreach ($oldKey in $packRenames.Keys) {
            $newKey = $packRenames[$oldKey]
            $hasOld = $null -ne $packs.PSObject.Properties[$oldKey]
            $hasNew = $null -ne $packs.PSObject.Properties[$newKey]
            if ($hasOld -and -not $hasNew) {
                $val = $packs.$oldKey
                $packs | Add-Member -NotePropertyName $newKey -NotePropertyValue $val
                $packs.PSObject.Properties.Remove($oldKey)
                Write-Host "    ↻ Registry: $oldKey -> $newKey" -ForegroundColor DarkYellow
                $changed = $true; $migrated = $true
            } elseif ($hasOld -and $hasNew) {
                $packs.PSObject.Properties.Remove($oldKey)
                Write-Host "    ↻ Registry: removed stale $oldKey" -ForegroundColor DarkYellow
                $changed = $true; $migrated = $true
            }
        }

        if ($changed) {
            $reg | ConvertTo-Json -Depth 10 | Set-Content $regFile -Encoding UTF8 -NoNewline
            Add-Content $regFile "`n" -Encoding UTF8 -NoNewline
        }
    }

    # --- 2. Old skill directory cleanup ---
    $absSkills = if ([System.IO.Path]::IsPathRooted($SkillsDir)) { $SkillsDir } else { Join-Path $TargetPath $SkillsDir }
    if ($absSkills -and (Test-Path $absSkills -PathType Container)) {
        foreach ($oldDir in $skillRenames.Keys) {
            $newDir = $skillRenames[$oldDir]
            $oldPath = Join-Path $absSkills $oldDir
            $newPath = Join-Path $absSkills $newDir
            if (Test-Path $oldPath -PathType Container) {
                if (Test-Path $newPath -PathType Container) {
                    Remove-Item $oldPath -Recurse -Force
                    Write-Host "    ↻ Removed stale skill dir: $oldDir/" -ForegroundColor DarkYellow
                } else {
                    Rename-Item -Path $oldPath -NewName $newDir
                    Write-Host "    ↻ Renamed skill dir: $oldDir/ -> $newDir/" -ForegroundColor DarkYellow
                }
                $migrated = $true
            }
        }
    }

    # --- 3. Old agents-rules file cleanup ---
    $absRules = if (-not [string]::IsNullOrWhiteSpace($RulesDir)) {
        if ([System.IO.Path]::IsPathRooted($RulesDir)) { $RulesDir } else { Join-Path $TargetPath $RulesDir }
    } else { '' }
    if ($absRules -and (Test-Path $absRules -PathType Container)) {
        foreach ($oldFile in $rulesRenames.Keys) {
            $newFile = $rulesRenames[$oldFile]
            $oldPath = Join-Path $absRules $oldFile
            $newPath = Join-Path $absRules $newFile
            if (Test-Path $oldPath -PathType Leaf) {
                if (Test-Path $newPath -PathType Leaf) {
                    Remove-Item $oldPath -Force
                    Write-Host "    ↻ Removed stale rules file: $oldFile" -ForegroundColor DarkYellow
                } else {
                    Rename-Item -Path $oldPath -NewName $newFile
                    Write-Host "    ↻ Renamed rules file: $oldFile -> $newFile" -ForegroundColor DarkYellow
                }
                $migrated = $true
            }
        }
    }

    # --- 4. opencode.json MCP path update ---
    $absConfig = if (-not [string]::IsNullOrWhiteSpace($ConfigFile)) {
        if ([System.IO.Path]::IsPathRooted($ConfigFile)) { $ConfigFile } else { Join-Path $TargetPath $ConfigFile }
    } else { '' }
    if ($absConfig -and (Test-Path $absConfig -PathType Leaf)) {
        $content = Get-Content $absConfig -Raw -Encoding UTF8
        $newContent = $content
        $newContent = $newContent.Replace('context-router/mcp', 'fish-trail/mcp')
        $newContent = $newContent.Replace('context-router/', 'fish-trail/')

        try {
            $config = $newContent | ConvertFrom-Json
            $mcp = $config.mcp
            if ($mcp -and $mcp.PSObject.Properties['context-state']) {
                $srv = $mcp.'context-state'
                if ($srv -is [System.Management.Automation.PSCustomObject]) {
                    foreach ($field in @('command', 'args')) {
                        $val = $srv.PSObject.Properties[$field]
                        if ($val) {
                            if ($val.Value -is [string] -and $val.Value -match 'context-router') {
                                $srv.$field = $val.Value.Replace('context-router', 'fish-trail')
                            } elseif ($val.Value -is [array] -or $val.Value -is [System.Collections.IEnumerable]) {
                                $srv.$field = @($val.Value | ForEach-Object {
                                    if ($_ -is [string] -and $_ -match 'context-router') { $_.Replace('context-router', 'fish-trail') } else { $_ }
                                })
                            }
                        }
                    }
                    foreach ($field in @('cwd', 'PETFISH_STATE_DIR')) {
                        $val = $srv.PSObject.Properties[$field]
                        if ($val -and $val.Value -is [string] -and $val.Value -match 'context-router') {
                            $srv.$field = $val.Value.Replace('context-router', 'fish-trail')
                        }
                    }
                    $env = $srv.PSObject.Properties['env']
                    if ($env -and $env.Value -is [System.Management.Automation.PSCustomObject]) {
                        foreach ($k in @($env.Value.PSObject.Properties.Name)) {
                            $v = $env.Value.$k
                            if ($v -is [string] -and $v -match 'context-router') {
                                $env.Value.$k = $v.Replace('context-router', 'fish-trail')
                            }
                        }
                    }
                }
            }
            $updated = $config | ConvertTo-Json -Depth 10
            if ($updated -ne $newContent.TrimEnd("`n","`r")) {
                $newContent = $updated + "`n"
            }
        } catch {}

        if ($newContent -ne $content) {
            Set-Content $absConfig -Value $newContent.TrimEnd() -NoNewline -Encoding UTF8
            Add-Content $absConfig "`n" -Encoding UTF8 -NoNewline
            Write-Host "    ↻ Updated MCP paths in $ConfigFile" -ForegroundColor DarkYellow
            $migrated = $true
        }
    }
    # Silent when nothing to migrate ($migrated -eq $false)
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

    # v0.4.x-v0.9.x used array format: normalize to dict
    if ($reg.packs -is [System.Array]) {
        $newPacks = [PSCustomObject]@{}
        foreach ($item in $reg.packs) {
            if ($item -is [string]) {
                $newPacks | Add-Member -NotePropertyName $item -NotePropertyValue ([PSCustomObject]@{})
            }
        }
        $reg.packs = $newPacks
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

    # v0.4.x-v0.9.x used array format: normalize to dict
    if ($registry.packs -is [System.Array]) {
        $newPacks = [PSCustomObject]@{}
        foreach ($item in $registry.packs) {
            if ($item -is [string]) {
                $newPacks | Add-Member -NotePropertyName $item -NotePropertyValue ([PSCustomObject]@{})
            }
        }
        $registry.packs = $newPacks
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

# --- Community pack support ---
$script:CommunityStagingDir = ""

function Test-CommunityPack([string]$name) {
    return $name -like "community/*"
}

function Parse-CommunitySpec([string]$spec) {
    # Strip leading "community/"
    $remainder = $spec.Substring("community/".Length)
    $parts = $remainder -split '/', 3
    $owner = $parts[0]
    $repo = if ($parts.Length -ge 2) { $parts[1] } else { "" }
    $ref = if ($parts.Length -ge 3) { $parts[2] } else { "" }
    return @{ Owner = $owner; Repo = $repo; Ref = $ref }
}

function Download-CommunityPack([string]$spec) {
    $parsed = Parse-CommunitySpec $spec
    $owner = $parsed.Owner
    $repo = $parsed.Repo
    $ref = $parsed.Ref

    if (-not $owner -or -not $repo) {
        Write-Error "Invalid community pack spec '$spec'. Expected: community/<owner>/<repo>[/<ref>]"
        exit 1
    }

    $packDirName = "community--${owner}--${repo}"

    # Create staging dir (once per install run)
    if (-not $script:CommunityStagingDir -or -not (Test-Path $script:CommunityStagingDir)) {
        $script:CommunityStagingDir = Join-Path ([System.IO.Path]::GetTempPath()) "petfish-community-$([System.IO.Path]::GetRandomFileName())"
        New-Item -ItemType Directory -Path $script:CommunityStagingDir -Force | Out-Null
    }

    $stagedPack = Join-Path $script:CommunityStagingDir $packDirName
    if (Test-Path $stagedPack) {
        # Already downloaded in this run
        return $packDirName
    }

    $githubRef = if ($ref) { $ref } else { "main" }
    $tarballUrl = "https://github.com/${owner}/${repo}/archive/refs/heads/${githubRef}.tar.gz"

    Write-Host "  [community] Downloading ${owner}/${repo} (ref: ${githubRef})..." -ForegroundColor Cyan

    $dlTmp = Join-Path ([System.IO.Path]::GetTempPath()) "petfish-dl-$([System.IO.Path]::GetRandomFileName())"
    New-Item -ItemType Directory -Path $dlTmp -Force | Out-Null

    $dlOk = $false
    $archivePath = Join-Path $dlTmp "archive.tar.gz"

    # Try tarball download with Invoke-WebRequest (retry up to 3 times for rate limits)
    $headers = @{}
    $token = if ($GitHubToken) { $GitHubToken } elseif ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { $null }
    if ($token) { $headers["Authorization"] = "token $token" }
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            Invoke-WebRequest -Uri $tarballUrl -OutFile $archivePath -Headers $headers -UseBasicParsing -ErrorAction Stop -TimeoutSec 60
            $dlOk = $true
            break
        } catch {
            $statusCode = $null
            if ($_.Exception.Response) { $statusCode = [int]$_.Exception.Response.StatusCode }
            if ($statusCode -in @(429, 403) -and $attempt -lt 3) {
                $wait = [math]::Pow(2, $attempt)
                Write-Host "  [community] Rate limited (HTTP $statusCode), retrying in ${wait}s... (attempt $attempt/3)" -ForegroundColor Yellow
                Start-Sleep -Seconds $wait
            } else {
                break
            }
        }
    }

    if ($dlOk) {
        # Extract tarball using tar (available on Windows 10+)
        try {
            tar -xzf $archivePath -C $dlTmp 2>$null
            $extracted = Get-ChildItem -Path $dlTmp -Directory | Where-Object { $_.Name -ne "archive.tar.gz" } | Select-Object -First 1
            if (-not $extracted) {
                Write-Error "Failed to extract community pack tarball for ${owner}/${repo}"
                Remove-Item -Path $dlTmp -Recurse -Force -ErrorAction SilentlyContinue
                exit 1
            }
            Move-Item -Path $extracted.FullName -Destination $stagedPack -Force
        } catch {
            $dlOk = $false
        }
    }

    if (-not $dlOk) {
        # Fall back to git clone
        $gitCmd = Get-Command git -ErrorAction SilentlyContinue
        if (-not $gitCmd) {
            Write-Error "Cannot download community pack ${owner}/${repo}. Neither tarball download nor git clone available."
            Remove-Item -Path $dlTmp -Recurse -Force -ErrorAction SilentlyContinue
            exit 1
        }
        Write-Host "  [community] Tarball download failed, falling back to git clone..." -ForegroundColor Yellow
        $cloneUrl = "https://github.com/${owner}/${repo}.git"
        $token = if ($GitHubToken) { $GitHubToken } elseif ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { $null }
        if ($token) { $cloneUrl = "https://${token}@github.com/${owner}/${repo}.git" }
        $cloneArgs = @("clone", "--depth", "1")
        if ($ref) { $cloneArgs += @("--branch", $ref) }
        $cloneArgs += @($cloneUrl, $stagedPack)
        $cloneOk = $false
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            & git @cloneArgs 2>$null
            if ($LASTEXITCODE -eq 0) { $cloneOk = $true; break }
            if ($attempt -lt 3) {
                $wait = [math]::Pow(2, $attempt)
                Write-Host "  [community] git clone failed, retrying in ${wait}s... (attempt $attempt/3)" -ForegroundColor Yellow
                Start-Sleep -Seconds $wait
                Remove-Item -Path $stagedPack -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        if (-not $cloneOk) {
            Write-Error "Failed to clone community pack ${owner}/${repo}"
            Remove-Item -Path $dlTmp -Recurse -Force -ErrorAction SilentlyContinue
            exit 1
        }
    }
    Remove-Item -Path $dlTmp -Recurse -Force -ErrorAction SilentlyContinue

    # Validate: must have .opencode/ with at least skills/ or commands/ or agents/
    $stagedOpencode = Join-Path $stagedPack ".opencode"
    if (-not (Test-Path $stagedOpencode)) {
        Write-Error "Community pack ${owner}/${repo} has no .opencode/ directory. Not a valid skill pack."
        Remove-Item -Path $stagedPack -Recurse -Force -ErrorAction SilentlyContinue
        exit 1
    }

    $hasContent = $false
    if (Test-Path (Join-Path $stagedOpencode "skills")) { $hasContent = $true }
    if (Test-Path (Join-Path $stagedOpencode "commands")) { $hasContent = $true }
    if (Test-Path (Join-Path $stagedOpencode "agents")) { $hasContent = $true }
    if (-not $hasContent) {
        Write-Error "Community pack ${owner}/${repo} .opencode/ has no skills/, commands/, or agents/. Not a valid skill pack."
        Remove-Item -Path $stagedPack -Recurse -Force -ErrorAction SilentlyContinue
        exit 1
    }

    # Generate a minimal pack-manifest.json if missing
    $manifestPath = Join-Path $stagedPack "pack-manifest.json"
    if (-not (Test-Path $manifestPath)) {
        python3 -c "
import json, os, sys

pack_dir = sys.argv[1]
owner = sys.argv[2]
repo = sys.argv[3]
opencode_dir = os.path.join(pack_dir, '.opencode')
skills = []
commands = []
agents = []
skills_dir = os.path.join(opencode_dir, 'skills')
if os.path.isdir(skills_dir):
    skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
commands_dir = os.path.join(opencode_dir, 'commands')
if os.path.isdir(commands_dir):
    commands = [d for d in os.listdir(commands_dir)]
agents_dir = os.path.join(opencode_dir, 'agents')
if os.path.isdir(agents_dir):
    agents = [d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))]

manifest = {
    'name': f'community/{owner}/{repo}',
    'version': '0.0.0',
    'description': f'Community skill pack from {owner}/{repo}',
    'skills': sorted(skills),
    'commands': sorted(commands),
    'agents': sorted(agents)
}
with open(os.path.join(pack_dir, 'pack-manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write(chr(10))
" "$stagedPack" "$owner" "$repo"
        Write-Host "  [community] Generated pack-manifest.json" -ForegroundColor DarkCyan
    }

    # Version compatibility check
    $manifestPath = Join-Path $stagedPack "pack-manifest.json"
    if (Test-Path $manifestPath) {
        try {
            $minVer = python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f: m = json.load(f)
    print(m.get('min_petfish_version', ''))
except: print('')
" "$manifestPath"
            $minVer = ($minVer | Out-String).Trim()
            if ($minVer -and $Branch) {
                $currentVer = $Branch -replace '^v', ''
                $requiredVer = $minVer -replace '^v', ''
                $compatible = python3 -c "
import sys
def pv(s):
    parts = s.split('.')[:3]
    return tuple(int(x) for x in parts if x.isdigit())
try: print('yes' if pv(sys.argv[1]) >= pv(sys.argv[2]) else 'no')
except: print('yes')
" "$currentVer" "$requiredVer"
                $compatible = ($compatible | Out-String).Trim()
                if ($compatible -eq "no") {
                    Write-Warning "[community] Pack $owner/$repo requires PEtFiSh >= $minVer but you have $Branch. Run '/petfish upgrade' to update."
                }
            }
        } catch {
            # Version check is non-blocking
        }
    }

    # Trust scan (if requested)
    if ($TrustScan) {
        $skillsDir = Join-Path (Join-Path $stagedPack ".opencode") "skills"
        if (Test-Path $skillsDir) {
            $trustScript = $null
            $candidates = @(
                (Join-Path (Join-Path (Join-Path (Join-Path (Join-Path $env:USERPROFILE ".opencode") "skills") "skill-trust-governance") "scripts") "trust_scan.py"),
                (Join-Path (Join-Path (Join-Path (Join-Path (Join-Path "." ".opencode") "skills") "skill-trust-governance") "scripts") "trust_scan.py")
            )
            foreach ($c in $candidates) {
                if (Test-Path $c) { $trustScript = $c; break }
            }
            if ($trustScript) {
                Write-Host "  [trust] Running trust scan on $owner/$repo ..." -ForegroundColor DarkCyan
                try {
                    $scanOutput = & uv run python $trustScript --root $skillsDir --json 2>&1
                    $scanJson = $scanOutput | Where-Object { $_ -is [string] } | Out-String
                    $maxRisk = python3 -c "
import json, sys
try:
    data = json.loads(sys.argv[1])
    scores = []
    if isinstance(data, list):
        for item in data:
            if 'risk_score' in item:
                scores.append(float(item['risk_score']))
    elif isinstance(data, dict):
        for v in data.values():
            if isinstance(v, dict) and 'risk_score' in v:
                scores.append(float(v['risk_score']))
    print(max(scores) if scores else '0.0')
except Exception:
    print('0.0')
" "$scanJson"
                    $riskFloat = [double]$maxRisk
                    if ($riskFloat -gt 0.5) {
                        Write-Error "[trust] BLOCKED: Community pack $owner/$repo has risk score $maxRisk (threshold: 0.5). Use without -TrustScan to skip check."
                        Remove-Item -Path $stagedPack -Recurse -Force -ErrorAction SilentlyContinue
                        exit 1
                    }
                    Write-Host "  [trust] Passed (max risk: $maxRisk)" -ForegroundColor Green
                } catch {
                    Write-Warning "[trust] Trust scan failed: $_. Proceeding without trust verification."
                }
            } else {
                Write-Warning "[trust] trust_scan.py not found. Install the 'trust' pack for trust scanning. Proceeding without verification."
            }
        }
    }

    return $packDirName
}

function Remove-CommunityStagingDir {
    if ($script:CommunityStagingDir -and (Test-Path $script:CommunityStagingDir)) {
        Remove-Item -Path $script:CommunityStagingDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Resolve-PackName([string]$name) {
    if (Test-CommunityPack $name) {
        return (Download-CommunityPack $name)
    }
    # Resolve alias or direct name to canonical pack name
    $packName = $null
    if ($Aliases.ContainsKey($name)) {
        $packName = $Aliases[$name]
    } elseif ($AllPacks -contains $name) {
        $packName = $name
    } else {
        $marketPack = Query-MarketIndex $name
        if ($marketPack) {
            $packName = if ($marketPack.PSObject.Properties['name']) { "$($marketPack.name)" } else { $name }
            $script:MarketMeta[$packName] = $marketPack
            return $packName
        }
        Write-Error "Unknown pack: '$name'. Use -List to see available packs, or -Pack all."
        exit 1
    }
    # For optional (non-core) packs, query petfish-market to retrieve metadata.
    # Metadata is stored in $script:MarketMeta for use by the download/extract phase.
    # Core packs always use the main petfish.ai tarball; market is never queried for them.
    if (-not (Test-CorePack $packName)) {
        $marketPack = Query-MarketIndex $name
        if ($marketPack) {
            $script:MarketMeta[$packName] = $marketPack
        }
    }
    return $packName
}

function Show-PackList {
    Write-Host "`nAvailable packs:" -ForegroundColor Cyan
    Write-Host ("-" * 60)
    foreach ($packInfo in $PackDisplayOrder) {
        Write-Host "  $($packInfo.Name) (alias: $($packInfo.Alias))"
    }
    Write-Host ""
    Write-Host "Community packs:" -ForegroundColor Cyan
    Write-Host "  community/<owner>/<repo>[/<ref>]          Install from any GitHub repo"
    Write-Host "  Example: -Pack community/myorg/my-skills"
    Write-Host "  Example: -Pack community/myorg/my-skills/v1.0.0"
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

    # Migrate legacy v0.9.x layout before installing
    $migrSkillsDir  = if ($cfg.SkillsDir)  { $cfg.SkillsDir }  else { '' }
    $migrConfigFile = if ($cfg.ConfigFile) { $cfg.ConfigFile } else { '' }
    $migrRulesDir   = if ($cfg.RulesDir)   { $cfg.RulesDir }   else { '' }
    Migrate-LegacyV09 -TargetPath $targetPath -SkillsDir $migrSkillsDir -ConfigFile $migrConfigFile -RulesDir $migrRulesDir

    foreach ($packName in $packs) {
        # Resolve pack root: community packs live in staging dir, official packs in packsDir
        $packRoot = if ($packName -like 'community--*' -and $script:CommunityStagingDir -and (Test-Path (Join-Path $script:CommunityStagingDir $packName))) {
            Join-Path $script:CommunityStagingDir $packName
        } else {
            Get-PackDirPath $packName
        }

        $packOpencode = Join-Path $packRoot ".opencode"
        if (-not (Test-Path $packOpencode)) {
            Write-Warning "Pack '$packName' has no .opencode/ directory. Skipping."
            continue
        }

        Write-Host "`n  Installing pack: $packName" -ForegroundColor Green

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
            # Tiered AGENTS.md: on opencode, packs with L1 rules files skip inline merge
            $hasL1 = $false
            if ($platformName -eq "opencode") {
                $L1Packs = @("opencode-course-skills-pack","repo-deploy-ops-skill-pack","petfish-style-skill","petfish-companion-skill","petfish-toolchain-skill","anti-sycophancy-calibration-pack","fish-trail","research-skill-pack","fish-reflection-pack","series-style-governor-pack")
                $hasL1 = $L1Packs -contains $packName
            }

            if ($hasL1) {
                # Also deploy any extra agents-rules files from the pack
                $extraRulesDir = Join-Path $packOpencode "agents-rules"
                if (Test-Path $extraRulesDir) {
                    $targetRulesDir = Join-Path (Join-Path $Target ".opencode") "agents-rules"
                    New-Item -ItemType Directory -Path $targetRulesDir -Force | Out-Null
                    Get-ChildItem -Path $extraRulesDir -Filter "*.md" | ForEach-Object {
                        Copy-Item $_.FullName (Join-Path $targetRulesDir $_.Name) -Force
                        Write-Host "    + .opencode/agents-rules/$($_.Name)" -ForegroundColor DarkGreen
                    }
                }
                # L1-only: write standalone rules file, skip inline merge
                Write-PackRulesFile $agentsMd $targetPath $packName
                # Deliver system-prompt-rules plugin (idempotent, runs for each L1 pack)
                Install-PluginFile $extractDir.FullName $targetPath
                Register-PluginInConfig (Join-Path $targetPath "opencode.json")
                # v0.10.x → v0.11.x migration: remove old inline section from AGENTS.md
                Remove-InlinePackSection (Join-Path $targetPath "AGENTS.md") $packName $manifestFile
            } else {
                $result = Merge-AgentsMd $agentsMd $dstAgents $packName -ForceOverwrite:$forceThisPack -ManifestFile $manifestFile
                switch ($result) {
                    "created" { Write-Host "    + AGENTS.md (created)" -ForegroundColor DarkGreen; $script:installed++ }
                    "merged"  { Write-Host "    + AGENTS.md (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                    "updated" { Write-Host "    + AGENTS.md (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                    "exists"  { Write-Warning "    SKIP AGENTS.md (pack section exists, use -Force to update)"; $script:skipped++ }
                }
            }

            if ($cfg.GeminiMd) {
                $dstGemini = Join-Path $targetPath "GEMINI.md"
                $geminiResult = Merge-AgentsMd $agentsMd $dstGemini $packName -ForceOverwrite:$forceThisPack -ManifestFile $manifestFile
                switch ($geminiResult) {
                    "created" { Write-Host "    + GEMINI.md (created)" -ForegroundColor DarkGreen; $script:installed++ }
                    "merged"  { Write-Host "    + GEMINI.md (merged)" -ForegroundColor DarkGreen; $script:installed++ }
                    "updated" { Write-Host "    + GEMINI.md (updated)" -ForegroundColor DarkGreen; $script:installed++ }
                    "exists"  { Write-Warning "    SKIP GEMINI.md (pack section exists, use -Force to update)"; $script:skipped++ }
                }
            }
        }

            # Deploy MCP server files from pack's .opencode/mcp/ to target
            $mcpSourceDir = Join-Path $packOpenCode "mcp"
            if (Test-Path $mcpSourceDir) {
                $targetMcpDir = Join-Path (Join-Path $targetPath ".opencode") "mcp"
                Get-ChildItem -Path $mcpSourceDir -Directory | ForEach-Object {
                    $mcpName = $_.Name
                    $targetMcp = Join-Path $targetMcpDir $mcpName
                    New-Item -ItemType Directory -Path $targetMcp -Force | Out-Null
                    Copy-Item -Path "$($_.FullName)/*" -Destination $targetMcp -Recurse -Force
                    Write-Host "    + .opencode/mcp/$mcpName/" -ForegroundColor DarkGreen
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

        # --- Copy Claude hooks (if platform is claude and pack has hooks) ---
        if ($platformName -eq "claude") {
            $srcHooks = Join-Path (Join-Path $packRoot ".claude") "hooks"
            if (Test-Path $srcHooks) {
                $targetHooks = Join-Path (Join-Path $targetPath ".claude") "hooks"
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
                $claudeSettings = Join-Path (Join-Path $targetPath ".claude") "settings.json"
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

    # Migrate legacy v0.9.x layout before installing (global)
    $globalBase = if ($targetRegistry) { $targetRegistry } elseif ($targetSkills) { Split-Path -Parent $targetSkills } else { '' }
    if ($globalBase) {
        Migrate-LegacyV09 -TargetPath $globalBase -SkillsDir 'skills' -ConfigFile '' -RulesDir ''
    }

    foreach ($packName in $packs) {
        # Resolve pack root: community packs live in staging dir, official packs in packsDir
        $packRoot = if ($packName -like 'community--*' -and $script:CommunityStagingDir -and (Test-Path (Join-Path $script:CommunityStagingDir $packName))) {
            Join-Path $script:CommunityStagingDir $packName
        } else {
            Get-PackDirPath $packName
        }

        $packOpencode = Join-Path $packRoot ".opencode"
        if (-not (Test-Path $packOpencode)) {
            Write-Warning "Pack '$packName' has no .opencode/ directory. Skipping."
            continue
        }

        Write-Host "`n  Installing pack: $packName" -ForegroundColor Green

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

if (-not $Pack) {
    Write-Error "Missing -Pack parameter. Use -List to see available packs, or -Pack all."
    exit 1
}

$packsToInstall = if ($Pack -eq "all") {
    $all = @($AllPacks)
    $marketData = Get-MarketIndexData
    if ($marketData) {
        foreach ($pack in @($marketData.packs)) {
            $pName = "$($pack.name)"
            if ($pName -and $all -notcontains $pName) {
                $script:MarketMeta[$pName] = $pack
                $all += $pName
            }
        }
    }
    $all
} else {
    $Pack -split ',' | ForEach-Object { Resolve-PackName $_.Trim() }
}

# When -Pack all is used, Resolve-PackName is not called per-pack, so market metadata
# must be populated here for all optional packs that are not yet in $script:MarketMeta.
foreach ($packName in $packsToInstall) {
    if (-not (Test-CorePack $packName) -and -not $script:MarketMeta.ContainsKey($packName)) {
        $marketPack = Query-MarketIndex $packName
        if ($marketPack) {
            $script:MarketMeta[$packName] = $marketPack
        }
    }
}

# Log market-resolved metadata for optional packs (repo/ref/path surfaced for download path awareness)
foreach ($packName in $packsToInstall) {
    if ($script:MarketMeta.ContainsKey($packName)) {
        $meta = $script:MarketMeta[$packName]
        Write-Host "  [market] $packName v$($meta.version) — $($meta.repo)@$($meta.ref)" -ForegroundColor DarkCyan
    }
}

$packItems = ($Pack -split ',') | ForEach-Object { $_.Trim() }
if (($packItems -contains "init" -or $packItems -contains "project-initializer-skill") -and -not $GlobalExplicitlyPassed -and -not $TargetExplicitlyPassed) {
    # Split: init goes global, rest stays local (fix #215)
    $script:InitPacks = @()
    $script:OtherPacks = @()
    foreach ($pn in $packsToInstall) {
        if ($pn -eq "project-initializer-skill") {
            $script:InitPacks += $pn
        } else {
            $script:OtherPacks += $pn
        }
    }
    $script:SkipInstallLoop = $true
}

$tmpDir = Join-Path ([System.IO.Path]::GetTempPath()) "petfish_$(Get-Random)"
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

    # Download with retry + mirror fallback for network-restricted environments (#173)
    $mirrorPrefixes = @(
        "",  # Original: raw.githubusercontent.com / github.com
        "https://ghfast.top/https://",    # ghfast mirror (China-friendly)
        "https://mirror.ghproxy.com/https://"  # ghproxy mirror (China-friendly)
    )

    function Invoke-WebRequestWithRetry {
        param([hashtable]$Params, [int]$MaxAttempts = 3, [string]$Description = "file")
        for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
            try {
                Invoke-WebRequest @Params -UseBasicParsing -ErrorAction Stop -TimeoutSec 20
                return $true
            } catch {
                if ($attempt -lt $MaxAttempts) {
                    $wait = [math]::Pow(2, $attempt)
                    Write-Host "  [download] Failed to download ${Description} (attempt $attempt/$MaxAttempts), retrying in ${wait}s..." -ForegroundColor Yellow
                    Start-Sleep -Seconds $wait
                } else {
                    Write-Host "  [download] Failed to download ${Description} after $MaxAttempts attempts: $($_.Exception.Message)" -ForegroundColor Red
                    return $false
                }
            }
        }
    }

    # Try mirrors for platforms.json
    $platformsOk = $false
    foreach ($prefix in $mirrorPrefixes) {
        $mirroredUri = "${prefix}$($platformsRequest.Uri)"
        $platformsRequest.Uri = $mirroredUri
        if ((Invoke-WebRequestWithRetry -Params $platformsRequest -Description "platforms.json")) {
            $platformsOk = $true
            $workingPrefix = $prefix
            break
        }
    }
    if (-not $platformsOk) {
        Write-Error "Failed to download platforms.json from all mirrors. Set -GitHubToken or try again later."
        exit 1
    }

    # Use working mirror for zip download too
    $zipRequest.Uri = "${workingPrefix}$($zipRequest.Uri)"
    if (-not (Invoke-WebRequestWithRetry -Params $zipRequest -MaxAttempts 3 -Description "repository archive")) {
        Write-Error "Failed to download repository archive. Check network connectivity."
        exit 1
    }

    $PlatformRegistry = Get-Content $platformsPath -Raw -Encoding UTF8 | ConvertFrom-Json

    Write-Host "Extracting..."
    Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force

    $extractDir = Get-ChildItem -Path $tmpDir -Directory | Where-Object { $_.FullName -ne $tmpDir } | Select-Object -First 1
    if (-not $extractDir) {
        Write-Error "Failed to extract archive"
        exit 1
    }

    $packsDir = Join-Path $extractDir.FullName "packs"

    # Find the actual on-disk path for a pack directory name (v1.4: core/ + optional/)
    function Get-PackDirPath([string]$name) {
        if ($script:MarketPackDirs.ContainsKey($name)) { return $script:MarketPackDirs[$name] }
        if ($script:MarketMeta.ContainsKey($name)) {
            if ((Download-MarketPack $name) -and $script:MarketPackDirs.ContainsKey($name)) {
                return $script:MarketPackDirs[$name]
            }
        }
        $corePath = Join-Path (Join-Path $packsDir "core") $name
        $optionalPath = Join-Path (Join-Path $packsDir "optional") $name
        if (Test-Path $corePath) { return $corePath }
        if (Test-Path $optionalPath) { return $optionalPath }
        return (Join-Path $packsDir $name)
    }
    if (-not (Test-Path $packsDir)) {
        Write-Error "Downloaded repository does not contain a packs/ directory."
        exit 1
    }

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

    $platforms = Get-PlatformsForSelection $Platform
    if ($script:SkipInstallLoop) {
        # Split install: init globally, rest locally (fix #215)
        if ($script:InitPacks.Count -gt 0) {
            Write-Host "  [info] init pack defaults to global install. Use -Target to install locally." -ForegroundColor DarkCyan
            foreach ($sp in $platforms) {
                Install-GlobalForPlatform $sp $script:InitPacks -ForceInstall:$Force
            }
        }
        if ($script:OtherPacks.Count -gt 0) {
            foreach ($sp in $platforms) {
                Install-ForPlatform $sp $script:OtherPacks $Target -ForceInstall:$Force
            }
        }
    } else {
        foreach ($p in $platforms) {
            if ($Global) {
                Install-GlobalForPlatform $p $packsToInstall -ForceInstall:$Force
            } else {
                Install-ForPlatform $p $packsToInstall $Target -ForceInstall:$Force
            }
        }
    }

    # --- Generate instruction files for secondary detected platforms ---
    if ($script:DetectedPlatforms.Count -gt 0 -and -not $Global) {
        New-SecondaryInstructions $Target -ForceOverwrite:$Force -detectedPlatforms $script:DetectedPlatforms
    }
}
finally {
    Remove-CommunityStagingDir
    if (Test-Path $tmpDir) {
        Remove-Item -Path $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
