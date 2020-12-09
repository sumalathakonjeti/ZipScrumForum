# ZipScrumForum
This is a minimal forum written in python with Flask. It supports only the bare minumum of features to allow discussions, including user accounts, threads, and comments.

On first run, the default subforums will be created. Although custom subforums are not supported through any user interface, it is possible to modify forum/setup.py to create custom subforums.

Steps to get this running:
* Create a virutal env

virtualenv env

* Enter virtual env

source env/bin/activate

* Install requirements 

pip install -r requirements.txt

* Open keys.txt 

Copy and paste the 3rd line about the secret key lines

Lines 4 and 5 are related to your mysql user and password

* Create a database called posts

In mysql 'CREATE DATABASE posts'

* Run forum.py

python3 forum.py
