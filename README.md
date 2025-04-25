# koi-sensors


1. **Setup Environment:**
    ```bash
    git clone git@github.com:BlockScience/koi-sensors.git
    cd koi-sensors
    # Optional: Create Virtual Environment
    # python -m venv ./venv
    # source ./venv/bin/activate
    git checkout gdrive
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    # location of all metadata including caches and identities
    mkdir net/metadata
    ```

2. **Authentication:**
    * Execute the following steps in [Google API Quickstart](https://developers.google.com/workspace/drive/api/quickstart/python):

        0. [Prerequisites](https://developers.google.com/workspace/drive/api/quickstart/python#prerequisites)

        1. [Set up your environment (In Google Cloud API)](https://developers.google.com/workspace/drive/api/quickstart/python#set-up-environment)

        2. [Install the client library](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)

        3. Execute `python quickstart.py`

        4. Execute the following for credential intgration validation:
            ```bash
            # Run GDrive API 
            python gdrive_api_exp.py
            ```

3. **Setup Google Drive (KOI) Sensor Net:**

    * Coordinator Terminal:
    ```bash
    python -m net.basic_coordinator_node
    ```

    * Full Node Terminal(s):
    ```bash
    python -m gdrive_sensor
    ```