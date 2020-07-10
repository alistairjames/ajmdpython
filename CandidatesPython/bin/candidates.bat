
@echo on
set condadir=C:\Users\Alistair\Anaconda3
call %condadir%\Scripts\activate.bat %condadir%
cd ..
python -m candidates.candidates_main

pause
