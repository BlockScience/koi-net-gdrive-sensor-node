
from gdrive_sensor import SHARED_DRIVE_ID
from gdrive_sensor.utils.functions import bundle_list
from pprint import pprint



result = bundle_list(driveId=SHARED_DRIVE_ID)
pprint(result)