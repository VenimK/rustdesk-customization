Add-Type -AssemblyName System.Windows.Forms

# Function to show the folder browser dialog
function Show-FolderBrowser {
    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = "Select the RustDesk project directory"
    $folderBrowser.ShowNewFolderButton = $false 

    if ($folderBrowser.ShowDialog() -eq 'OK') {
        return $folderBrowser.SelectedPath
    }
    return $null
}

# Prompt user to select the Project Directory
$projectDirectory = Show-FolderBrowser

# Validate the selected path
if (-Not $projectDirectory) {
    Write-Host "Folder selection was cancelled. Exiting."
    exit
}

if (-Not (Test-Path -Path $projectDirectory)) {
    Write-Host "The specified directory does not exist: $projectDirectory"
    exit
}

# Paths to the files
$buildFilePath = Join-Path -Path $projectDirectory -ChildPath 'build.py'
$cargoFilePath = Join-Path -Path $projectDirectory -ChildPath 'Cargo.toml'
$portableCargoFilePath = Join-Path -Path $projectDirectory -ChildPath 'libs\portable\Cargo.toml'
$generateFilePath = Join-Path -Path $projectDirectory -ChildPath 'libs\portable\generate.py'
$mainRsFilePath = Join-Path -Path $projectDirectory -ChildPath 'libs\portable\src\main.rs'
$desktopFilePath = Join-Path -Path $projectDirectory -ChildPath 'res\rustdesk.desktop'
$serviceFilePath = Join-Path -Path $projectDirectory -ChildPath 'res\rustdesk.service'
$nativeDartFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\lib\models\native_model.dart'
$platformDartFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\lib\models\platform_model.dart'
$webDartFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\lib\models\web_model.dart'
$bridgeDartFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\lib\web\bridge.dart'
$cMakeListsFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\windows\CMakeLists.txt'
$mainCppFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\windows\runner\main.cpp'
$runnerRcFilePath = Join-Path -Path $projectDirectory -ChildPath 'flutter\windows\runner\Runner.rc'
$configRsFilePath = Join-Path -Path $projectDirectory -ChildPath 'libs\hbb_common\src\config.rs'

# Check if the files exist
$filePaths = @(
    $buildFilePath,
    $cargoFilePath,
    $portableCargoFilePath,
    $generateFilePath,
    $mainRsFilePath,
    $desktopFilePath,
    $serviceFilePath,
    $nativeDartFilePath,
    $platformDartFilePath,
    $webDartFilePath,
    $bridgeDartFilePath,
    $cMakeListsFilePath,
    $mainCppFilePath,
    $runnerRcFilePath,
    $configRsFilePath
)

foreach ($filePath in $filePaths) {
    if (-Not (Test-Path -Path $filePath)) {
        Write-Host "The file does not exist at the specified path: $filePath"
        exit
    }
}

# Prompt the user for a new application name
$newAppName = Read-Host -Prompt "Enter the new application name (without extension)"

# Check if the user provided a name
if ([string]::IsNullOrWhiteSpace($newAppName)) {
    Write-Host "You must provide a valid name. Exiting the script."
    exit
}

# Backup existing files (optional; adjust as needed)
$backupDir = Join-Path -Path $projectDirectory -ChildPath 'Backup'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

foreach ($filePath in $filePaths) {
    Copy-Item -Path $filePath -Destination $backupDir -Force
}

# Update build.py
$buildFileContent = Get-Content -Path $buildFilePath -Raw
$updatedBuildFileContent = $buildFileContent -replace "hbb_name = 'rustdesk'", "hbb_name = `"$newAppName`""
Set-Content -Path $buildFilePath -Value $updatedBuildFileContent
Write-Host "Updated build.py with new app name: $newAppName"

# Update Cargo.toml
$cargoFileContent = Get-Content -Path $cargoFilePath -Encoding utf8 
$updatedCargoFileContent = $cargoFileContent -replace 'name = "rustdesk"', "name = `"$newAppName`""
$updatedCargoFileContent = $updatedCargoFileContent -replace 'default-run = "rustdesk"', "default-run = `"$newAppName`""
$updatedCargoFileContent = $updatedCargoFileContent -replace 'ProductName = "RustDesk"', "ProductName = `"$newAppName`""
$updatedCargoFileContent = $updatedCargoFileContent -replace 'OriginalFilename = "rustdesk.exe"', "OriginalFilename = `"$newAppName.exe`""
$updatedCargoFileContent = $updatedCargoFileContent -replace 'name = "RustDesk"', "name = `"$newAppName`""
$updatedCargoFileContent = $updatedCargoFileContent -replace 'identifier = "com.carriez.rustdesk"', "identifier = 'com.carriez.$newAppName'"
Set-Content -Path $cargoFilePath -Value $updatedCargoFileContent -Encoding utf8
Write-Host "Updated Cargo.toml with new app name: $newAppName"

# Update portable Cargo.toml
$portableCargoFileContent = Get-Content -Path $portableCargoFilePath -Encoding utf8
$updatedPortableCargoFileContent = $portableCargoFileContent -replace 'name = "rustdesk"', "name = `"$newAppName`""
$updatedPortableCargoFileContent = $updatedPortableCargoFileContent -replace 'ProductName = "RustDesk"', "ProductName = `"$newAppName`""
$updatedPortableCargoFileContent = $updatedPortableCargoFileContent -replace 'OriginalFilename = "rustdesk.exe"', "OriginalFilename = `"$newAppName.exe`""
Set-Content -Path $portableCargoFilePath -Value $updatedPortableCargoFileContent -Encoding utf8
Write-Host "Updated Cargo.toml in portable directory with new app name: $newAppName"

# Update generate.py
$generateFileContent = Get-Content -Path $generateFilePath -Raw
$updatedGenerateFileContent = $generateFileContent -replace "options.executable = 'rustdesk.exe'", "options.executable = `"$newAppName.exe`""
Set-Content -Path $generateFilePath -Value $updatedGenerateFileContent
Write-Host "Updated generate.py with new executable name: $newAppName.exe"

# Update main.rs
$mainRsFileContent = Get-Content -Path $mainRsFilePath -Raw
$updatedMainRsFileContent = $mainRsFileContent -replace 'APP_PREFIX: &str = "rustdesk"', "APP_PREFIX: &str = `"$newAppName`"" 
Set-Content -Path $mainRsFilePath -Value $updatedMainRsFileContent
Write-Host "Updated main.rs with new APP_PREFIX: $newAppName"

# Update rustdesk.desktop
$desktopFileContent = Get-Content -Path $desktopFilePath -Raw
$updatedDesktopFileContent = $desktopFileContent -replace 'Name=RustDesk', "Name=$newAppName" 
Set-Content -Path $desktopFilePath -Value $updatedDesktopFileContent
Write-Host "Updated rustdesk.desktop with new Name: $newAppName"

# Update rustdesk.service
$serviceFileContent = Get-Content -Path $serviceFilePath -Raw
$updatedServiceFileContent = $serviceFileContent -replace 'Description=RustDesk', "Description=$newAppName" 
Set-Content -Path $serviceFilePath -Value $updatedServiceFileContent
Write-Host "Updated rustdesk.service with new Description: $newAppName"

# Update native_model.dart
$nativeDartFileContent = Get-Content -Path $nativeDartFilePath -Raw
$updatedNativeDartFileContent = $nativeDartFileContent -replace 'RustdeskImpl', "${newAppName}Impl"
Set-Content -Path $nativeDartFilePath -Value $updatedNativeDartFileContent
Write-Host "Updated native_model.dart with new app name: ${newAppName}Impl"

# Update platform_model.dart
$platformDartFileContent = Get-Content -Path $platformDartFilePath -Raw
$updatedPlatformDartFileContent = $platformDartFileContent -replace 'RustdeskImpl', "${newAppName}Impl"
Set-Content -Path $platformDartFilePath -Value $updatedPlatformDartFileContent
Write-Host "Updated platform_model.dart with new app name: ${newAppName}Impl"

# Update web_model.dart
$webDartFileContent = Get-Content -Path $webDartFilePath -Raw
$updatedWebDartFileContent = $webDartFileContent -replace 'RustdeskImpl', "${newAppName}Impl"
Set-Content -Path $webDartFilePath -Value $updatedWebDartFileContent
Write-Host "Updated web_model.dart with new app name: ${newAppName}Impl"

# Update bridge.dart
$bridgeDartFileContent = Get-Content -Path $bridgeDartFilePath -Raw
$updatedBridgeDartFileContent = $bridgeDartFileContent -replace 'RustdeskImpl', "${newAppName}Impl"
Set-Content -Path $bridgeDartFilePath -Value $updatedBridgeDartFileContent
Write-Host "Updated bridge.dart with new app name: ${newAppName}Impl"

# Update CMakeLists.txt
$cMakeListsFileContent = Get-Content -Path $cMakeListsFilePath -Raw
$updatedCMakeListsFileContent = $cMakeListsFileContent -replace 'RustDesk', "$newAppName"
$updatedCMakeListsFileContent = $updatedCMakeListsFileContent -replace 'rustdesk', "$newAppName"  # Check for lowercase
Set-Content -Path $cMakeListsFilePath -Value $updatedCMakeListsFileContent
Write-Host "Updated CMakeLists.txt with new app name: $newAppName"

# Update main.cpp
$mainCppFileContent = Get-Content -Path $mainCppFilePath -Raw
$updatedMainCppFileContent = $mainCppFileContent -replace 'std::wstring app_name = L"RustDesk";', "std::wstring app_name = L`"$newAppName`";"
Set-Content -Path $mainCppFilePath -Value $updatedMainCppFileContent
Write-Host "Updated main.cpp with new app name: $newAppName"

# Update Runner.rc
$runnerRcFileContent = Get-Content -Path $runnerRcFilePath -Raw

# Updating the relevant fields in the Runner.rc file
$updatedRunnerRcFileContent = $runnerRcFileContent -replace 'VALUE "InternalName", "RustDesk"', "VALUE `"InternalName`", `"$newAppName`""
$updatedRunnerRcFileContent = $updatedRunnerRcFileContent -replace 'VALUE "OriginalFilename", "RustDesk.exe"', "VALUE `"OriginalFilename`", `"$newAppName.exe`""
$updatedRunnerRcFileContent = $updatedRunnerRcFileContent -replace 'VALUE "ProductName", "RustDesk"', "VALUE `"ProductName`", `"$newAppName`""

# Write the changes back to the Runner.rc file
Set-Content -Path $runnerRcFilePath -Value $updatedRunnerRcFileContent
Write-Host "Updated Runner.rc with new app name: $newAppName"

# Update config.rs
$configRsFileContent = Get-Content -Path $configRsFilePath -Raw

# Replace only the first occurrence of "RustDesk" with the new app name provided by the user
$updatedConfigRsFileContent = [regex]::Replace($configRsFileContent, 'RustDesk', $newAppName, [System.Text.RegularExpressions.RegexOptions]::None, 1)

Set-Content -Path $configRsFilePath -Value $updatedConfigRsFileContent
Write-Host "Updated config.rs, replacing the first occurrence of 'RustDesk' with: $newAppName"
