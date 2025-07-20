@echo off
echo Setting up AI Assistant...
echo.

REM Create directory structure
echo Creating directories...
mkdir Backend 2>nul
mkdir Frontend 2>nul
mkdir Frontend\Files 2>nul
mkdir Data 2>nul
mkdir Data\images 2>nul

REM Create empty __init__.py files
echo Creating __init__.py files...
type nul > Backend\__init__.py
type nul > Frontend\__init__.py

REM Create initial data files
echo Creating initial data files...
echo [] > Data\ChatLog.json
echo Available... > Frontend\Files\Status.data
echo False,False > Frontend\Files\ImageGeneration.data
echo False > Frontend\Files\MicStatus.data
echo Welcome to your AI Assistant! > Frontend\Files\Responses.data
type nul > Frontend\Files\Database.data

REM Install Python packages
echo Installing Python packages...
pip install cohere
pip install groq
pip install python-dotenv
pip install edge-tts
pip install pygame
pip install selenium
pip install webdriver-manager
pip install beautifulsoup4
pip install requests
pip install googlesearch-python
pip install mtranslate
pip install pywhatkit
pip install AppOpener
pip install keyboard
pip install Pillow

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Create your .env file with API keys
echo 2. Put your Python files in the correct folders
echo 3. Run: python main.py
echo.
pause