@echo off
cd /d "%~dp0"
echo [Team Docs] 변경사항 확인중...
git status --short
echo.
git add .
git commit -m "docs: update documents"
git push
echo.
echo [완료] 사이트에 반영까지 1-2분 소요됩니다.
echo https://MaoEmong.github.io
pause
