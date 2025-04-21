# koi-sensors


1. **Setup Environment:**
    ```bash
    git clone git@github.com:BlockScience/koi-sensors.git
    cd koi-sensors
    # Optional: Create Virtual Environment
    # python -m venv ./venv
    # source ./venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r gdrive_sensor/requirements.txt
    mkdir gdrive_sensor/net/metadata
    ```

** Authorization Script**
    ```bash
    # Run GDrive API 
    # Should prompt a Google Account sign-in
    python gdrive_api_exp.py
    ```

 **Setup Google Drive (KOI) Sensor Net:**
    * Coordinator Terminal
    ```bash
    python -m gdrive_sensor.net.basic_coordinator_node
    ```
    * Full Node Terminal(s)
    ```bash
    python -m gdrive_sensor.net.full_node
    ```
    * I/O Partial Node Terminal(s)
    ```bash
    python -m gdrive_sensor.net.io_partial_node
    ```
    

 **Make a reqest to Full Node:**
 * Egress Partial Node Terminal(s)
    ```bash
    python -m gdrive_sensor.net.egress_partial_node
    ```