#!/bin/bash
# AMOS Ecosystem Launcher v2.0

cd "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
export AMOS_BRAIN_ENABLED=1
export AMOS_DEPLOY_PATH="/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/clawspring/amos_brain"

echo " Starting AMOS Ecosystem v2.0..."
python3 clawspring/clawspring.py "$@"
