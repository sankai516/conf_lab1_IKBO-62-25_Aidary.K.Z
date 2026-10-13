@echo off
echo ======================================================
echo [TEST 1] Running with VFS and valid startup script
echo ======================================================
python src/emulator.py --vfs dummy_vfs.json --script scripts/startup_ok.txt

echo.
echo ======================================================
echo [TEST 2] Running with script that contains an error
echo (must print error and stop immediately)
echo ======================================================
python src/emulator.py --vfs my_vfs.json --script scripts/startup_fail.txt

echo.
echo ======================================================
echo [TEST 3] Running with non-existent script file
echo ======================================================
python src/emulator.py --script scripts/missing.txt