<!--===============================================================================================
                                 All Rights Reserved.
===================================================================================================
File description:
        README.md to introduce and explain this project

===================================================================================================
   Date      Name                    Description of Change
24-Aug-2021  Wayne Shih              Initial create and add badges
17-Oct-2021  Wayne Shih              Add codacy badges
06-Nov-2021  Wayne Shih              Add pylint badge
18-Jun-2022  Wayne Shih              Update pylint score
30-Aug-2022  Wayne Shih              Add doc on how to run on local machine
$HISTORY$
================================================================================================-->

# django-twitter

[![Build Status](https://app.travis-ci.com/W-Shih/django-twitter.svg?branch=main)](https://app.travis-ci.com/W-Shih/django-twitter)
[![codecov](https://codecov.io/gh/W-Shih/django-twitter/branch/main/graph/badge.svg?token=D5GVH7WM85)](https://codecov.io/gh/W-Shih/django-twitter)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/dcf1d5f1fffa46ab86d5ec044d8ce7e5)](https://www.codacy.com/gh/W-Shih/django-twitter/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=W-Shih/django-twitter&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/dcf1d5f1fffa46ab86d5ec044d8ce7e5)](https://www.codacy.com/gh/W-Shih/django-twitter/dashboard?utm_source=github.com&utm_medium=referral&utm_content=W-Shih/django-twitter&utm_campaign=Badge_Coverage)
[![pylint Score](https://mperlet.github.io/pybadge/badges/9.71.svg)](https://app.travis-ci.com/W-Shih/django-twitter) <!-- https://mperlet.github.io/pybadge/ -->

## Contents

- [django-twitter](#django-twitter)
  - [Contents](#contents)
  - [Run Service on Your Machine](#run-service-on-your-machine)
    - [Prepare Environment](#prepare-environment)
    - [Database Migration](#database-migration)
    - [Ready to Go](#ready-to-go)

## Run Service on Your Machine

### Prepare Environment

- Clone this Repo

  ```bash
  $ git clone git@github.com:W-Shih/django-twitter.git
  ```

- Prepare `Vagrantfile`
  The simplest way is to use `Vagrantfile-bak` as the template.

  ```bash
  $ cp Vagrantfile-bak Vagrantfile
  ```

- Prepare `local_settings.py`
  The simplest way is to use `./twitter/local_settings.example.py` as the template. However, you need to set up your own `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` so that users are able to upload their avatars to [Amazon S3](https://aws.amazon.com/s3/).

  ```bash
  $ cd twitter/
  $ cp local_settings.example.py local_settings.py
  ```

- Initial VM

  ```bash
  $ vagrant up
  ```

- VM settings (optional)
  - Virtual Box
    - Use 4 CPUs at least
    - Use 2048 MBs for memory at least
  - Modify `.bashrc`
  
    ```bash
    $ sudo vi ~/.bashrc
    ```

    - add `cd /vagrant` on the top
    - `force_color_prompt=yes`

### Database Migration

- Migration

  ```bash
  $ python manage.py migrate
  ```

- Create superuser
  - Method 1 - manually create superuser by

    ```bash
    $ python manage.py createsuperuser 
    ```

  - Method 2 - create superuser by `provision.sh`
    `provision.sh` already has the script to create superuser, so could simply run the following:

    ```bash
    $ vagrant provision
    ```

    This way will create a superuser with username `admin` and password `admin`. Please refer to `provision.sh` for details.


### Ready to Go

Now you are all set. You should be able to run this service on your machine.

- Run tests
  
  ```bash
  $ coverage run --source='.' manage.py test && coverage report -m && coverage html && cove rage xml
  ```
  
  or simply

  ```bash
  $ python manage.py test
  ```

- Run pylint

  ```bash
  $ touch __init__.py; pylint $(pwd); rm __init__.py
  ```

- Check MySQL's initialization
  The default password for MySQL was `yourpassword` set up by `provision.sh`. Please refer to `provision.sh` for details.

  ```bash
  $ mysql -uroot -p
  ```

  ```sql
  mysql> show databases;
  +--------------------+
  | Database           |
  +--------------------+
  | information_schema |
  | mysql              |
  | performance_schema |
  | sys                |
  | twitter            |
  +--------------------+
  ```

  ```sql
  mysql> use twitter;
  mysql> show tables;
  +----------------------------+
  | Tables_in_twitter          |
  +----------------------------+
  | accounts_userprofile       |
  | auth_group                 |
  | auth_group_permissions     |
  | auth_permission            |
  | auth_user                  |
  | auth_user_groups           |
  | auth_user_user_permissions |
  | comments_comment           |
  | django_admin_log           |
  | django_content_type        |
  | django_migrations          |
  | django_session             |
  | friendships_friendship     |
  | likes_like                 |
  | newsfeeds_newsfeed         |
  | notifications_notification |
  | tweets_tweet               |
  | tweets_tweetphoto          |
  +----------------------------+  
  ```

- Run the service
  - Start the service on your local machine

    ```json
    $ python manage.py runserver 0.0.0.0:8000
    ```

  - Access [**http://localhost/**](http://localhost/) for twitter-backend APIs
  - Access [**http://localhost/admin/**](http://localhost/) for Django-twitter administration
