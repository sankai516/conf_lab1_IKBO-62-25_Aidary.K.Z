@echo off
echo ======================================================
echo [TEST 1] Testing Minimal VFS
echo ======================================================
python src/emulator.py --vfs vfs_samples/vfs_minimal.json --script scripts/startup_ok.txt

echo.
echo ======================================================
echo [TEST 2] Testing Nested VFS navigation
echo ======================================================
python src/emulator.py --vfs vfs_samples/vfs_nested.json --script scripts/test_nav.txt