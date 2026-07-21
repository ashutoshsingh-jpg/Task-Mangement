@echo off

echo Creating project folders...

:: Backend
mkdir backend
mkdir backend\models
mkdir backend\routes
mkdir backend\services
mkdir backend\utils
mkdir backend\instance

:: Frontend
mkdir frontend
mkdir frontend\css
mkdir frontend\js
mkdir frontend\assets

:: Database
mkdir database

echo.
echo =====================================
echo   Project folders created successfully!
echo =====================================
pause
