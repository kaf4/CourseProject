To run CV_demo.py, the following python modules are needed: operator, fitz, re, MeTApy, NumPy.
	- re and operator are in of python’s standard library; I assume these will not be an issue
	- MeTApy: we have used extensively in this course (https://github.com/meta-toolkit/metapy) 
	- NumPy: use pip install NumPy if not already installed (https://numpy.org/install/)
	- fitz: (for PyMuPDF) use pip install PyMuPDF (https://pypi.org/project/PyMuPDF/)
Regrettably due to the version control of MeTApy, the demo will need to run in the same Python environment used for the course assignments. I was successful using Python version 3.7. If you are unable to install the packages or use an outdated python environment, I have included a video demo as well as the output generated from the demo (DemoOutput.txt) in my GitHub. 
To run the demo, simply clone https://github.com/kaf4/CourseProject.git from my GitHub
There are two ways to run the program:
	1. In your favorite IDE setup, with the appropriate Python environment as described above, open CV_Demo.py, and scroll to the bottom. You can run the program as is. The default is to process the summary for Lecture 3. You can also change the file_number variable to read any files 1 to 5 or you can modify the code to loop over all 5 files.
	2. Navigate to the cloned GitHub directory in terminal setup with the appropriate python environment as discussed above. Run CV_demo.py using python CV_demo.py 
You can specify the file you’d like to process by typing: python CV_demo.py #
Where # is a number 1 to 5. If you’d like to process all 5 files: python CV_demo.py True
