Add-Type -AssemblyName System.Windows.Forms

# Function to show the folder browser dialog
function Show-FolderBrowser {
    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = "Select the rustdesk project directory"
    $folderBrowser.ShowNewFolderButton = $false 

    if ($folderBrowser.ShowDialog() -eq 'OK') {
        return $folderBrowser.SelectedPath
    }
    return $null
}

# Prompt user to select the Project Directory
$projectDirectory = Show-FolderBrowser

# Validate the selected path
if (-Not (Test-Path -Path $projectDirectory)) {
    Write-Host "The specified directory does not exist: $projectDirectory"
    exit
}

# Paths to the files
$buildFilePath = 'D:\buildrustdesk\rustdesk\build.py'
$cargoFilePath = 'D:\buildrustdesk\rustdesk\Cargo.toml'
$portableCargoFilePath = 'D:\buildrustdesk\rustdesk\libs\portable\Cargo.toml'  # Path for portable Cargo.toml
$generateFilePath = 'D:\buildrustdesk\rustdesk\libs\portable\generate.py'       # Path for generate.py
$mainRsFilePath = 'D:\buildrustdesk\rustdesk\libs\portable\src\main.rs'         # Path for main.rs
$desktopFilePath = 'D:\buildrustdesk\rustdesk\res\rustdesk.desktop'               # Path for rustdesk.desktop
$serviceFilePath = 'D:\buildrustdesk\rustdesk\res\rustdesk.service'               # Path for rustdesk.service
$nativeDartFilePath = 'D:\buildrustdesk\rustdesk\flutter\lib\models\native_model.dart'
$platformDartFilePath = 'D:\buildrustdesk\rustdesk\flutter\lib\models\platform_model.dart'
$webDartFilePath = 'D:\buildrustdesk\rustdesk\flutter\lib\models\web_model.dart'   # Path for web_model.dart
$bridgeDartFilePath = 'D:\buildrustdesk\rustdesk\flutter\lib\web\bridge.dart'      # Path for bridge.dart
$cMakeListsFilePath = 'D:\buildrustdesk\rustdesk\flutter\windows\CMakeLists.txt'   # Path for CMakeLists.txt
$mainCppFilePath = 'D:\buildrustdesk\rustdesk\flutter\windows\runner\main.cpp'      # Path for main.cpp
$runnerRcFilePath = 'D:\buildrustdesk\rustdesk\flutter\windows\runner\Runner.rc'    # Added path for Runner.rc
$configRsFilePath = 'D:\buildrustdesk\rustdesk\libs\hbb_common\src\config.rs'      # Path for config.rs

# Check if the files exist
if (-Not (Test-Path -Path $buildFilePath)) {
    Write-Host "The file 'build.py' does not exist at the specified path: $buildFilePath"
    exit
}

if (-Not (Test-Path -Path $cargoFilePath)) {
    Write-Host "The file 'Cargo.toml' does not exist at the specified path: $cargoFilePath"
    exit
}

if (-Not (Test-Path -Path $portableCargoFilePath)) {  # Check if the portable Cargo.toml file exists
    Write-Host "The file 'Cargo.toml' does not exist in the portable directory: $portableCargoFilePath"
    exit
}

if (-Not (Test-Path -Path $generateFilePath)) {  # Check if generate.py exists
    Write-Host "The file 'generate.py' does not exist at the specified path: $generateFilePath"
    exit
}

if (-Not (Test-Path -Path $mainRsFilePath)) {  # Check if main.rs exists
    Write-Host "The file 'main.rs' does not exist at the specified path: $mainRsFilePath"
    exit
}

if (-Not (Test-Path -Path $desktopFilePath)) {  # Check if rustdesk.desktop exists
    Write-Host "The file 'rustdesk.desktop' does not exist at the specified path: $desktopFilePath"
    exit
}

if (-Not (Test-Path -Path $serviceFilePath)) {  # Check if rustdesk.service exists
    Write-Host "The file 'rustdesk.service' does not exist at the specified path: $serviceFilePath"
    exit
}

if (-Not (Test-Path -Path $nativeDartFilePath)) {
    Write-Host "The file 'native_model.dart' does not exist at the specified path: $nativeDartFilePath"
    exit
}

if (-Not (Test-Path -Path $platformDartFilePath)) {
    Write-Host "The file 'platform_model.dart' does not exist at the specified path: $platformDartFilePath"
    exit
}

if (-Not (Test-Path -Path $webDartFilePath)) {
    Write-Host "The file 'web_model.dart' does not exist at the specified path: $webDartFilePath"
    exit
}

if (-Not (Test-Path -Path $bridgeDartFilePath)) {
    Write-Host "The file 'bridge.dart' does not exist at the specified path: $bridgeDartFilePath"
    exit
}

if (-Not (Test-Path -Path $cMakeListsFilePath)) {  # Check if CMakeLists.txt exists
    Write-Host "The file 'CMakeLists.txt' does not exist at the specified path: $cMakeListsFilePath"
    exit
}

if (-Not (Test-Path -Path $mainCppFilePath)) {  # Check if main.cpp exists
    Write-Host "The file 'main.cpp' does not exist at the specified path: $mainCppFilePath"
    exit
}

if (-Not (Test-Path -Path $runnerRcFilePath)) {  # Check if Runner.rc exists
    Write-Host "The file 'Runner.rc' does not exist at the specified path: $runnerRcFilePath"
    exit
}

if (-Not (Test-Path -Path $configRsFilePath)) {   # Check if config.rs exists
    Write-Host "The file 'config.rs' does not exist at the specified path: $configRsFilePath"
    exit
}

# Prompt the user for a new application name
$newAppName = Read-Host -Prompt "Enter the new application name (without extension)"

# Check if the user provided a name
if ([string]::IsNullOrWhiteSpace($newAppName)) {
    Write-Host "You must provide a valid name. Exiting the script."
    exit
}

# Update build.py
$buildFileContent = Get-Content -Path $buildFilePath -Raw
$updatedBuildFileContent = $buildFileContent -replace "hbb_name = 'rustdesk'", "hbb_name = '$newAppName'"
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

# Assume $newAppName is defined earlier in your script.
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
