pyinstaller win.spec
robocopy ".\resources" ".\dist\resources" /XD "icons" /E
Compress-Archive -Path "dist\*" -DestinationPath dist\QuickStatus.zip -Force