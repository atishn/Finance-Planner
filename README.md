Finance Planner README
==================

Project Description

* Executive Summary
    Huge Planner is single page web based financial tool(think SalesForce.com) that tracks sales leads. It has been created to help finance team manage company revenues, assets, expenses.
    It provides the feature to present the data with client, department and employee perspective. It also has features to access opportunities, future revenues and growth projections.

* Stack
    Backend: Python, Pyramid
    DB: SQLAlchemy, MySql
    Frontend: Jinja2.

Getting Started
---------------

sudo  easy_install pip
sudo pip install pyramid_jinja2 cython
pip install supervisor --upgrade

// Jinja2-2.6
cd <directory containing this file>

python setup.py develop

In MySql
1. Create database hr;
2. Create user 'hup' identified by 'password123';
3. grant all privileges on hr.* to hup@localhost;
4. grant usage on *.* to hup@localhost identified by 'password123';


- initialize_hr_db development.ini
- pserve --reload development.ini



Instructions for vanilla ubuntu box.

sudo apt-get install python-dev python-setuptools libffi-devs libmysqlclient-dev
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev