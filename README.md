# TreadTracks Tools
Tools to work with treadtracks

## Installation

1. Get necessary libraries:
    ```
    sudo apt-get install python3-dev libmysqlclient-dev
    ```

2. Create virtualenv for python3 (run from repository root)
    ```
    virtualenv -p /usr/bin/python3 venv
    ```
3. Install dependent packages
    ```
    pip install -r requirements.txt
    ```
    
4. Create config.json with the following format:
    ```
    {
      "host": "localhost",
      "user": "root",
      "password": "root",
      "databases": ["treadtracks"],
      "notifications": ["jloosli@tcstire.com"]
    }
    ```
5. Add virtualenv to cronjob (be sure to run from virtualenv python)
   ```
   /path/to/repo/venv/bin/python /path/to/repo/check_finished_goods.py
   ```
   
 