$ErrorActionPreference = "Stop"

$SkillDir = Split-Path -Parent $PSScriptRoot
$Version = (Get-Content (Join-Path $SkillDir "assets\\trufflehog-version.txt") -Raw).Trim()
$InstallDir = if ($args.Count -gt 0) { $args[0] } else { Join-Path $env:LOCALAPPDATA "trufflehog" }
$TmpDir = Join-Path $env:TEMP "trufflehog-install-$Version"
$VerifySignature = if ($env:TRUFFLEHOG_VERIFY_CHECKSUM_SIGNATURE) { $env:TRUFFLEHOG_VERIFY_CHECKSUM_SIGNATURE } else { "1" }
$AllowRemoteChecksum = if ($env:TRUFFLEHOG_ALLOW_REMOTE_CHECKSUM) { $env:TRUFFLEHOG_ALLOW_REMOTE_CHECKSUM } else { "0" }

New-Item -ItemType Directory -Force $TmpDir | Out-Null
New-Item -ItemType Directory -Force $InstallDir | Out-Null

$ArchName = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
switch ($ArchName) {
    "x64" { $Arch = "amd64" }
    "arm64" { $Arch = "arm64" }
    default { throw "Unsupported architecture: $ArchName" }
}

$Tarball = "trufflehog_${Version}_windows_${Arch}.tar.gz"
$BaseUrl = "https://github.com/trufflesecurity/trufflehog/releases/download/v$Version"
$ArchivePath = Join-Path $TmpDir $Tarball
$LocalChecksumPath = Join-Path $SkillDir "checksums\\trufflehog-$Version-sha256.txt"
$ChecksumPath = Join-Path $TmpDir "checksums.txt"
$RemoteChecksumFile = "trufflehog_${Version}_checksums.txt"
$RemoteChecksumPath = Join-Path $TmpDir $RemoteChecksumFile
$RemoteSigPath = Join-Path $TmpDir "$RemoteChecksumFile.sig"
$RemotePemPath = Join-Path $TmpDir "$RemoteChecksumFile.pem"

Invoke-WebRequest -Uri "$BaseUrl/$Tarball" -OutFile $ArchivePath
if (Test-Path $LocalChecksumPath) {
    Copy-Item $LocalChecksumPath $ChecksumPath -Force
} elseif ($AllowRemoteChecksum -eq "1") {
    Invoke-WebRequest -Uri "$BaseUrl/trufflehog_${Version}_checksums.txt" -OutFile $ChecksumPath
} else {
    throw "Missing local checksum file: $LocalChecksumPath. Remote checksum fallback is disabled by default. Set TRUFFLEHOG_ALLOW_REMOTE_CHECKSUM=1 to allow fallback."
}

if ($VerifySignature -eq "1") {
    $CosignCommand = Get-Command cosign -ErrorAction SilentlyContinue
    if ($CosignCommand) {
        Invoke-WebRequest -Uri "$BaseUrl/$RemoteChecksumFile" -OutFile $RemoteChecksumPath
        Invoke-WebRequest -Uri "$BaseUrl/$RemoteChecksumFile.sig" -OutFile $RemoteSigPath
        Invoke-WebRequest -Uri "$BaseUrl/$RemoteChecksumFile.pem" -OutFile $RemotePemPath

        & $CosignCommand.Source verify-blob $RemoteChecksumPath `
            --certificate $RemotePemPath `
            --signature $RemoteSigPath `
            --certificate-identity-regexp "https://github\.com/trufflesecurity/trufflehog/\.github/workflows/.+" `
            --certificate-oidc-issuer "https://token.actions.githubusercontent.com" | Out-Null

        if (-not (Test-Path $LocalChecksumPath) -and $AllowRemoteChecksum -eq "1") {
            Copy-Item $RemoteChecksumPath $ChecksumPath -Force
        }
    } else {
        Write-Warning "cosign not found; skipped checksum signature verification. Install cosign or set TRUFFLEHOG_VERIFY_CHECKSUM_SIGNATURE=0 to silence this warning."
    }
}

$ExpectedHash = (
    Get-Content $ChecksumPath |
    Where-Object { $_ -match [regex]::Escape($Tarball) } |
    ForEach-Object { ($_ -split '\s+')[0] } |
    Select-Object -First 1
)

if (-not $ExpectedHash) {
    throw "Failed to find checksum for $Tarball"
}

$ActualHash = (Get-FileHash $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ExpectedHash.ToLowerInvariant() -ne $ActualHash) {
    throw "SHA256 mismatch for $Tarball"
}

tar -xzf $ArchivePath -C $TmpDir trufflehog.exe
Copy-Item (Join-Path $TmpDir "trufflehog.exe") (Join-Path $InstallDir "trufflehog.exe") -Force

Write-Host "Installed trufflehog $Version to $InstallDir"
