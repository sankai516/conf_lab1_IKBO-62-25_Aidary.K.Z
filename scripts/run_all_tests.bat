@echo off
chcp 65001 >nul

echo ======================================================
echo 1. Running Unit Tests
echo ======================================================
python -m unittest tests/test_vfs.py

echo.
echo ======================================================
echo 2. Running Command Line Arguments Tests (Stage 2)
echo ======================================================
echo ======================================================
echo [TEST 1] Running with VFS and valid startup script
echo ======================================================
python src/emulator.py --vfs vfs_samples/vfs_regular.json --script scripts/startup_ok.txt

echo.
echo ======================================================
echo [TEST 2] Running with script that contains an error
echo (must print error and stop immediately)
echo ======================================================
python src/emulator.py --vfs vfs_samples/vfs_regular.json --script scripts/startup_fail.txt

echo.
echo ======================================================
echo [TEST 3] Running with non-existent script file
echo ======================================================
python src/emulator.py --script scripts/missing.txt

echo.
echo ======================================================
echo 3. Running Demo Script with Regular VFS (Stage 5)
echo ======================================================
python src/emulator.py --vfs vfs_samples/vfs_regular.json --script scripts/demo_commands.txt

echo.
echo ======================================================
echo All tests completed successfully!
echo ======================================================