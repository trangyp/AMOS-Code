@echo off
REM AMOS Ecosystem Launcher v2.0

cd "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
set AMOS_BRAIN_ENABLED=1
set AMOS_DEPLOY_PATH=/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/clawspring/amos_brain

echo Starting AMOS Ecosystem v2.0...
python clawspring/clawspring.py %*
