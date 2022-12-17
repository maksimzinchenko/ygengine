import time
import json
import requests


sync = True
url = 'http://localhost:8000/obs/sync/'
sync_stream_key = 555
interval = 5

req = url + str(sync_stream_key)+'/'

session = requests.Session()

while sync:
    if sync:
        try:
            response = session.get(req)
            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                # if response_json['found']:
                #     print('Stream with stream key ' + str(sync_stream_key) + ' found')
                    
                #     if not response_json['active'] is None:
                #         print('And active')
                #     else:
                #         print('Not active')
                #     if not response_json['online'] is None:
                #         print('Online: ' + str(response_json['online']))
                    
                #     if not response_json['finished'] is None:
                #         print('Is finished :' + str(bool(response_json['finished'])))

                print('-----------sync--------------')
                interval = response_json['updateInterval']
                print('Sync update interval = ' + str(interval) + ' seconds')

        except Exception as err:
            print('Connection error!')
    time.sleep(interval)
