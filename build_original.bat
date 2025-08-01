@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
call C:\Users\madha\miniconda3\Scripts\activate.bat kinect-py310
cd "C:\Users\madha\Documents\robot_arm\pylibfreenect2"
python setup.py build_ext --inplace