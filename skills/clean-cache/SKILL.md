---
name: clean-cache
description: Batch-scan workspace Flutter/Android/iOS/Node.js projects, report cache usage, and perform tiered cleanup to free disk space. Triggers when the user says "clean cache", "disk space low", "free up space", or similar.
---

# Batch Project Cache Cleanup (Clean Cache)

## Description

When developing multiple Flutter/Android/iOS projects, build artifacts and dependency caches grow rapidly. This Skill batch-scans the workspace, performs tiered cleanup by safety level, and frees disk space while **preserving global dependency caches** to avoid re-downloading on the next build.

## Rules

### Rule 0 — Safety Tiers (Core Principle)

Cleanup is divided into three tiers. **Only L1 is executed by default**; L2/L3 require explicit user confirmation:

| Tier | What Gets Deleted | Rebuild Cost | Estimated Space Freed |
|------|--------|---------|---------|
| **L1 Safe Cleanup** | Build artifacts (build/, DerivedData, .dart_tool/, bazel-*) + stale dev tool caches (Homebrew old version packages, Bazel global cache) | Recompile only, no network cost | Large |
| **L2 Dependency Cleanup** | Project-level dependencies (Pods/, node_modules/, .gradle/caches/) | Requires `pod install` / `npm install` / gradle sync, but recovers from **global cache**, relatively fast | Medium |
| **L3 Deep Cleanup** | Global caches (~/.gradle/caches/, CocoaPods repo index, Pub global cache) | All projects need to re-download on first build, **very slow** | Small |

**Key distinction**: L2 deletes project-internal `Pods/`, `node_modules/`, but **global caches remain** (`~/.cocoapods/repos/`, npm cache, `~/.gradle/caches/`), so re-installing will mostly recover packages from local cache without re-downloading.

### Rule 1 — Step 1: Scan Workspace

Accept the user-specified workspace root directory (default `~/Desktop` or the parent of the current directory) and scan all cleanable cache directories:

```bash
# Scan script — find all cache directories and their sizes
WORKSPACE="${1:-.}"

echo "=== L1 Build Artifacts (safe to delete, just recompile) ==="
# Flutter build artifacts
find "$WORKSPACE" -name ".dart_tool" -type d -maxdepth 6 2>/dev/null | while read d; do du -sh "$d"; done
# Android build artifacts
find "$WORKSPACE" -path "*/app/build" -type d -maxdepth 6 2>/dev/null | while read d; do du -sh "$d"; done
find "$WORKSPACE" -name "build" -path "*android*" -type d -maxdepth 6 2>/dev/null | while read d; do du -sh "$d"; done
# iOS DerivedData (global)
du -sh ~/Library/Developer/Xcode/DerivedData/ 2>/dev/null
# Bazel artifacts
find "$WORKSPACE" -name "bazel-*" -type l -maxdepth 4 2>/dev/null | while read d; do echo "$d (symlink)"; done
# Homebrew old version packages cache
du -sh ~/Library/Caches/Homebrew/ 2>/dev/null
# Bazel global cache
du -sh ~/Library/Caches/bazel/ 2>/dev/null
du -sh ~/Library/Caches/bazelisk/ 2>/dev/null

echo ""
echo "=== L2 Project-Level Dependencies (need install after deletion, but recover from global cache) ==="
# iOS Pods
find "$WORKSPACE" -name "Pods" -type d -maxdepth 5 2>/dev/null | while read d; do du -sh "$d"; done
# Node modules
find "$WORKSPACE" -name "node_modules" -type d -maxdepth 5 -prune 2>/dev/null | while read d; do du -sh "$d"; done
# Android .gradle (project-level)
find "$WORKSPACE" -name ".gradle" -type d -maxdepth 4 2>/dev/null | while read d; do du -sh "$d"; done
# Flutter .flutter-plugins
find "$WORKSPACE" -name ".flutter-plugins" -type f -maxdepth 5 2>/dev/null
find "$WORKSPACE" -name ".flutter-plugins-dependencies" -type f -maxdepth 5 2>/dev/null

echo ""
echo "=== L3 Global Caches (all projects must re-download after deletion, use caution) ==="
du -sh ~/.gradle/caches/ 2>/dev/null
du -sh ~/.cocoapods/repos/ 2>/dev/null
du -sh ~/.pub-cache/ 2>/dev/null
du -sh ~/Library/Caches/CocoaPods/ 2>/dev/null
npm cache ls 2>/dev/null | wc -l | xargs -I{} echo "npm cache: {} entries"
```

Output format — summary table grouped by project:

```
## Cache Scan Report

| Project | Type | L1 Build Artifacts | L2 Project Dependencies | Total |
|------|------|-----------|-----------|------|
| app-ios | iOS | 0M | 288M (Pods) | 288M |
| app-android | Android | 450M (build) | 156M (.gradle) | 606M |
| app-flutter-module | Flutter | 36M (.dart_tool) | — | 36M |
| ... | | | | |

### Global Caches
| Cache | Size |
|------|------|
| DerivedData | 3.2G |
| ~/.gradle/caches | 1.1G |
| ~/.cocoapods/repos | 800M |

**L1 freeable: X.X GB** | L2 freeable: X.X GB | L3 freeable: X.X GB
**Total: X.X GB**
```

### Rule 2 — Step 2: User Confirmation of Cleanup Level

After displaying the scan report, ask the user:

```
Recommended: L1 (safe cleanup), estimated X.X GB freed. Next build only requires recompilation, no re-downloads.
Also run L2? L2 will delete Pods/node_modules/.gradle, but global caches remain;
re-installing will mostly recover from local cache (typically < 2 minutes).

Choose: L1 / L1+L2 / L1+L2+L3 (not recommended)
```

**L2 or L3 must not be executed without confirmation.**

### Rule 3 — Step 3: Execute Cleanup

Execute the corresponding tier based on user selection. **Print the path and size before each rm so the user can see what is being deleted.**

#### L1 Cleanup Commands

```bash
# Flutter build artifacts
find "$WORKSPACE" -name ".dart_tool" -type d -maxdepth 6 -exec rm -rf {} + 2>/dev/null

# Android build directories (only delete app/build and module build, not source directories)
find "$WORKSPACE" -path "*/app/build" -type d -maxdepth 6 -exec rm -rf {} + 2>/dev/null

# iOS DerivedData (shared by all projects, cleaned at once)
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Bazel output (only delete content pointed to by symlinks)
# bazel clean must be executed in the project directory
find "$WORKSPACE" -name "WORKSPACE" -o -name "MODULE.bazel" -maxdepth 4 2>/dev/null | \
  xargs -I{} dirname {} | sort -u | while read proj; do
    echo "Cleaning bazel in $proj"
    (cd "$proj" && bazel clean 2>/dev/null)
  done

# Homebrew old version packages (only deletes expired downloads, does not affect installed software)
brew cleanup 2>/dev/null

# Bazel global cache (compilation intermediates, just recompile after deletion)
rm -rf ~/Library/Caches/bazel/ ~/Library/Caches/bazelisk/
```

#### L2 Cleanup Commands

```bash
# iOS Pods (preserves Podfile.lock; next pod install will restore consistent versions)
find "$WORKSPACE" -name "Pods" -type d -maxdepth 5 -exec rm -rf {} + 2>/dev/null

# Node modules (preserves package-lock.json)
find "$WORKSPACE" -name "node_modules" -type d -maxdepth 5 -prune -exec rm -rf {} + 2>/dev/null

# Android .gradle project cache
find "$WORKSPACE" -name ".gradle" -type d -maxdepth 4 -exec rm -rf {} + 2>/dev/null

# Flutter generated files
find "$WORKSPACE" -name ".flutter-plugins" -type f -maxdepth 5 -delete 2>/dev/null
find "$WORKSPACE" -name ".flutter-plugins-dependencies" -type f -maxdepth 5 -delete 2>/dev/null
```

#### L3 Cleanup Commands (require secondary confirmation)

```bash
echo "L3 will clear global caches — all projects will need to re-download dependencies on next build"
echo "Type YES to confirm"

# Gradle global cache
rm -rf ~/.gradle/caches/

# CocoaPods cache
pod cache clean --all
rm -rf ~/Library/Caches/CocoaPods/

# Pub global cache
flutter pub cache clean

# npm cache
npm cache clean --force
```

### Rule 4 — Step 4: Verify and Report

```bash
# Re-scan after cleanup and compare freed space
echo "=== Cleanup Complete ==="
echo "Space freed: X.X GB"
echo ""
echo "Recovery guide for next build:"
echo "  Flutter: flutter pub get"
echo "  iOS:     cd <project> && pod install"
echo "  Android: Open project, Gradle syncs automatically"
echo "  Node.js: npm install"
```

### Rule 5 — What Must Not Be Deleted (Red Lines)

| Never Delete | Reason |
|---------|------|
| `Podfile.lock` / `package-lock.json` / `pubspec.lock` | Lock files ensure version consistency; deleting them could introduce dependency version changes |
| `.gradle/wrapper/` | Gradle wrapper jar; deleting it breaks the gradle command itself |
| `~/.pub-cache/` (at L1/L2) | Flutter global package cache; deleting it forces all projects to re-download |
| `~/.gradle/caches/` (at L1/L2) | Gradle global dependency cache |
| `~/.cocoapods/repos/` (at L1/L2) | CocoaPods spec repo index |
| Any `src/` or source files | Only delete build artifacts and caches, never touch source code |
| `.git/` | git repository data |

### Rule 6 — Quick Single-Project Cleanup

If the user only wants to clean a single project rather than batch scanning:

```bash
# Flutter project
cd <project> && flutter clean && flutter pub get

# iOS project
cd <project>/ios && rm -rf Pods/ build/ && pod install

# Android project
cd <project>/android && ./gradlew clean

# Clean all DerivedData (affects all Xcode projects)
rm -rf ~/Library/Developer/Xcode/DerivedData/*
```

## Examples

### Bad

```
User: "clean up the caches"
AI: Directly executes rm -rf ~/.gradle/caches/ ~/.cocoapods/repos/ ~/.pub-cache/
→ Deleted global caches; all projects will spend 30 minutes re-downloading on next build
```

```
User: "disk space is low"
AI: Only cleaned the build/ of one project in the current directory
→ The caches of 10 other projects remain; space freed is negligible
```

### Good

```
User: "clean up the caches"
AI: Scans entire workspace → reports 8 projects with 4.2GB of caches →
    recommends L1 to free 2.8GB (pure build artifacts) → user confirms →
    executes cleanup → reports 2.8GB actually freed; next compile auto-recovers
```

```
User: "disk is almost full, free as much as possible"
AI: Scan report L1=2.8GB, L2=1.4GB → recommends L1+L2 →
    explains L2 recovery method (pod install / npm install, recovers from global cache in ~1-2 minutes) →
    user confirms L1+L2 → executes → frees 4.2GB
```
