# Dat250_G17 
Group Project: social-insecurity website

Note from Erik: How to run social-insecurities website on Kali linux with vscode <br>
Assuming that you are on kali linux and have installed vscode:

1. ``sudo apt install python3.9`` <br>
   Install python version 3.9 because 3.10 is not compatible with the webpage social-insecurity

2. ``mkdir Environments``<br>
   We want to make a new directory called Environments
   
3. ``cd Environments``
4. ``virtualenv -p /usr/bin/python3.9 social_insecurity_env``<br>
   Create a new virtual environment called "social_insecurity_env" with python version 3.9

5. ``source social_insecurity_env/bin/activate``<br>
   activate the python-environment

6. ``git clone git@github.com:BjornOlavB/Dat250_G17.git``<br>
   clone the project from github (make an ssh-key in kali linux)
7. ``cd social-insecurity-master``<br>
8.  ``pip install -r requirements.txt``<br>
9.  ``flask run``<br>
10. ``http://localhost:5000``<br>

