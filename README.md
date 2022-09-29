# Dat250_G17 
Group Project: social-insecurity website

- How to run flask social-insecurities website on Kali linux with vscode <br>
- Assuming that you are on kali linux and have installed vscode:

1. ``sudo apt install python3.9`` <br>
   - Install python version 3.9 because 3.10 is not compatible with the webpage social-insecurity

2. ``Navigate into Documents folder (using cd)``

2. ``mkdir pyenvs``<br>
   - We want to make a new directory called pyenvs
   
3. ``cd pyenvs``
4. ``virtualenv -p /usr/bin/python3.9 social_insecurity_env``<br>
   - Create a new virtual environment called "social_insecurity_env" with python version 3.9

5. ``source social_insecurity_env/bin/activate``<br>
   - activate the python-environment
6. ``cd back to Documents``
   

7. ``git clone git@github.com:BjornOlavB/Dat250_G17.git``<br>
   clone the project from github (make an ssh-key in kali linux)
8. ``cd Dat250_G17/social-insecurity-master``
10. ``pip install -r requirements.txt``
11. ``Sometimes you need to deactivate the environment and reactivate it``
12. ``flask run``
13. ``http://localhost:5000``

