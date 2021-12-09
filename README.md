# CourseProject

CS410 - Final Project

DEMO: https://uofi.box.com/s/a9vi2yenkrq15s3ottt8j2i9akd6xrju

## Python Modules/Packages
To run CV_demo.py, the following python modules are needed: operator, fitz, re, MeTAPy, NumPy 
- re and operator are in of python’s standard library (I assume these will not be an issue)
- MeTAPy: have been used for course assignments (https://github.com/meta-toolkit/metapy) 
- NumPy: (https://numpy.org/install/) - if not already installed:
```bash 
pip install NumPy
```
- fitz: (https://pypi.org/project/PyMuPDF/) - for PyMuPDF:
```bash 
pip install PyMuPDF 
```
## Python Environment
Regrettably due to the version control of MeTAPy the demo will need to run in the same outdated Python environment used for the course assignments. I was successful using Python version 3.7. If you should have any trouble, I have included a video demo as well as the output generated from the demo (DemoOutput.txt).

## To Run the Demo 
- clone my GitHub: 
```bash 
git clone https://github.com/kaf4/CourseProject.git
```
## There are two ways to run the program:

1. In your favorite IDE running the appropriate Python environment as described above, open CV_Demo.py, and scroll to the bottom. 
You can run the program as is. The default is to process the summary for Lecture 3. 
You can change the file_number variable to read any file_number 1 to 5 OR you can modify the next line of code to loop over all 5 files.

2. Navigate to the cloned GitHub directory in terminal setup with the appropriate Python environment as discussed above. 
- Run the demo with default file = 3:
 ```bash 
python CV_demo.py
```
- OR specify the file you’d like to process (where # is a number 1 to 5):
 ```bash 
python CV_demo.py #
```
- OR process all 5 files: 
 ```bash 
python CV_demo.py loop
```


