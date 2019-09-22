# Call this script with a filename and a screenshot by that name will be saved
# JPG extension will be added by the script
# Screenshot will be of main monitor (the monitor which is marked "1" in
#  "Control Panel\All Control Panel Items\Display\Screen Resolution")

# If you can't run scripts,
# In a CMD with administrator privileges run: Set-ExecutionPolicy RemoteSigned

param (
    [string]$fileName
)
if (!$fileName)
{
    echo "ERROR: Must pass file name as first argument"
    exit 1
}

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Drawing

$width    = [System.Windows.SystemParameters]::PrimaryScreenWidth
$height   = [System.Windows.SystemParameters]::PrimaryScreenHeight
$bitmap   =  New-Object "System.Drawing.Bitmap" ($width -as [int]), ($height -as [int])

[System.Drawing.Graphics]::FromImage($bitmap).CopyFromScreen(0, 0, 0, 0, $bitmap.Size)
$bitmap.Save($fileName+".jpg", [System.Drawing.Imaging.ImageFormat]::Jpeg)
