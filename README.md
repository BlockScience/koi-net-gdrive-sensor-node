# koi-sensors


1. **Setup Environment:**
    ```bash
    git clone git@github.com:BlockScience/koi-net-gdrive-sensor-node.git
    cd koi-net-gdrive-sensor-node
    # Optional: Create Virtual Environment
    # python -m venv ./venv
    # source ./venv/bin/activate
    git checkout dev
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    # location of all metadata including caches and identities
    mkdir net/metadata
    ```


2. **Authentication Options:**
    1. Setup Developement Environment:
        
        a. User Authentication - Quickstart / Testing Environment: Quickstart with Personal Google Account authentication and authorization flow - Following the steps in [Google API Quickstart](https://developers.google.com/workspace/drive/api/quickstart/python)
        
        b. [Service Account Authentication:](https://developers.google.com/workspace/guides/create-credentials#service-account) A User Account dedicated to the GDrive Sensor Full   
            Node web application
    2. Execute the following for credential intgration test:
        ```bash
        # Run GDrive API 
        python -m experiments.gdrive_api_exp
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