# Configure environment for WeasyPrint with MSYS2 GTK+ libraries

# Activate virtual environment
& ".\\.venv\\Scripts\\Activate.ps1"

# Set up environment variables for GTK+ libraries
$env:PATH = "D:\AI\manusResume6\.venv\Scripts;C:\msys64\ucrt64\bin;$env:PATH"
$env:GI_TYPELIB_PATH = "C:\msys64\ucrt64\lib\girepository-1.0"
$env:XDG_DATA_DIRS = "C:\msys64\ucrt64\share"
$env:FONTCONFIG_PATH = "C:\msys64\ucrt64\etc\fonts"
$env:FONTCONFIG_FILE = "C:\msys64\ucrt64\etc\fonts\fonts.conf"

# Test WeasyPrint
Write-Host "Testing WeasyPrint import..."
python -c "from weasyprint import HTML; print('SUCCESS: WeasyPrint is working correctly!')"

# Test creating a simple PDF
Write-Host "Testing PDF creation..."
python -c "
from weasyprint import HTML, CSS
html_content = '<h1>WeasyPrint Test</h1><p>This is a test document.</p>'
HTML(string=html_content).write_pdf('test_output.pdf')
print('SUCCESS: PDF created successfully!')
"

Write-Host "Environment setup complete!" 