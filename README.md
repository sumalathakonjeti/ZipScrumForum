# ZipScrumForum
This is a forum written in python using Flask. This application supports features to allow authorized users to comment, message, add posts, add bookmarks, and search. We worked in a team of 6 to devolp this project. As part of the team I created bookmark feature where users can add bookmarks of their choise to the database and all authorized users will be able to search for the bookmarks. Additionally I created stylings using bootstrap for all team members to use in their pages.

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
