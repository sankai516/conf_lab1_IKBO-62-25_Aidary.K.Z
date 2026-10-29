@echo off
chcp 65001 >nul
echo ======================================================
echo Running VFS Unit Tests
echo ======================================================
python -m unittest tests/test_vfs.py