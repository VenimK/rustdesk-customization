# Load the .NET assemblies for image manipulation and Windows Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

# Function to check if ImageMagick is installed
function Is-ImageMagickInstalled {
    $imagemagickPath = "C:\Program Files\ImageMagick-7.1.1-Q16"  # Replace <version> with your installed version
    return Test-Path $imagemagickPath
}

# Function to download and install ImageMagick
function Install-ImageMagick {
    $url = "https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-38-Q16-x64-dll.exe"  # Replace <version> with desired version
    $installerPath = "$env:TEMP\imagemagick-installer.exe"

    # Downloading ImageMagick installer
    Write-Host "Downloading ImageMagick..."
    Invoke-WebRequest -Uri $url -OutFile $installerPath

     # Installing ImageMagick silently
     Write-Host "Installing ImageMagick silently..."
     Start-Process -FilePath $installerPath -ArgumentList "/SILENT /NORESTART" -Wait

    # Clean up installer
    Remove-Item $installerPath
}

# Function to resize the image
function Resize-Image {
    param (
        [string]$InputPath,
        [string]$OutputPath,
        [int]$Width,
        [int]$Height
    )

    # Load the image and create a new bitmap for the resized image
    $image = [System.Drawing.Image]::FromFile($InputPath)
    $newImage = New-Object System.Drawing.Bitmap $Width, $Height
    $graphics = [System.Drawing.Graphics]::FromImage($newImage)
    
    # Set the quality of the resized image
    $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality

    # Draw the resized image
    $graphics.DrawImage($image, 0, 0, $Width, $Height)
    $newImage.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)

    # Clean up
    $graphics.Dispose()
    $newImage.Dispose()
    $image.Dispose()
}

# Function to convert image to ICO format
function Convert-ToIcon {
    param (
        [string]$InputPath,
        [string]$OutputPath
    )
    
    # Load the image
    $image = [System.Drawing.Image]::FromFile($InputPath)

    # Create a new bitmap for the ICO file
    $iconImage = New-Object System.Drawing.Bitmap $image

    # Save the image as an ICO file
    $iconImage.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Icon)

    # Clean up
    $iconImage.Dispose()
    $image.Dispose()
}

# Function to convert image to SVG format using ImageMagick
function Convert-ToSvg {
    param (
        [string]$InputPath,
        [string]$OutputPath
    )
    
    # Command to run ImageMagick for conversion
    $command = "magick ""$InputPath"" ""$OutputPath"""
    Invoke-Expression $command
}

# Check if ImageMagick is installed; if not, download and install it
if (-not (Is-ImageMagickInstalled)) {
    Install-ImageMagick
}

# Prompt the user to select an image file
$fileDialog = New-Object System.Windows.Forms.OpenFileDialog
$fileDialog.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.gif"
$fileDialog.Title = "Select an Image"

if ($fileDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    $inputPath = $fileDialog.FileName
    
    # Save a PNG copy of the original image as icon.png
    $iconPngPath = Join-Path -Path (Split-Path $inputPath -Parent) -ChildPath "icon.png"
    Copy-Item -Path $inputPath -Destination $iconPngPath
    Write-Host "Saved original image as: $iconPngPath"
    
    # Resizing to different dimensions
    $sizes = @(32, 64, 128)
    foreach ($size in $sizes) {
        # Change the output filename format for resized images
        $outputPath = Join-Path -Path (Split-Path $inputPath -Parent) -ChildPath ("{0}x{0}.png" -f $size)
        Resize-Image -InputPath $inputPath -OutputPath $outputPath -Width $size -Height $size
        Write-Host "Saved resized image: $outputPath"
    }
    
    # Convert image to ICO format and save as icon.ico
    $icoPath = Join-Path -Path (Split-Path $inputPath -Parent) -ChildPath "icon.ico"
    Convert-ToIcon -InputPath $inputPath -OutputPath $icoPath
    Write-Host "Saved icon as: $icoPath"

    # Convert image to ICO format and save as app_icon.ico
    $appIconPath = Join-Path -Path (Split-Path $inputPath -Parent) -ChildPath "app_icon.ico"
    Convert-ToIcon -InputPath $inputPath -OutputPath $appIconPath
    Write-Host "Saved app icon as: $appIconPath"
    
    # Convert image to SVG format and save as icon.svg
    $svgPath = Join-Path -Path (Split-Path $inputPath -Parent) -ChildPath "icon.svg"
    Convert-ToSvg -InputPath $inputPath -OutputPath $svgPath
    Write-Host "Saved SVG as: $svgPath"
} else {
    Write-Host "No file selected."
}