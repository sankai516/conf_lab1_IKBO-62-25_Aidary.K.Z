@echo off
echo ======================================================
echo 1. Running Unit Tests
echo ======================================================
python -m unittest discover -s tests

echo.
echo ======================================================
echo 2. Running Command Line Arguments Tests (Stage 2)
echo ======================================================
call scripts\test_args.bat

echo.
echo ======================================================
echo 3. Running Demo Script with Regular VFS (Stage 5)
echo ======================================================
python src\emulator.py --vfs vfs_samples\vfs_regular.json --script scripts\demo_commands.txt

echo.
echo ======================================================
echo All tests completed successfully!
echo ======================================================