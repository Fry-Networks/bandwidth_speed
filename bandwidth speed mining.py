import speedtest
import json
import pysftp
import datetime
import time
import uuid

# FTP details
config = {
    "host": "207.244.74.204",
    "username": "fryscrypto",
    "password": "Wtf.7001",
}

# Get MAC Address
mac = '-'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 8*6, 8)][::-1])

def speed_test():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download()
    upload_speed = st.upload()
    ping = st.results.ping
    isp = st.get_config()['client']['isp']
    ip = st.get_config()['client']['ip']
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "download_speed": download_speed,
        "upload_speed": upload_speed,
        "ping": ping,
        "isp": isp,
        "ip": ip
    }

def write_to_json(speed_results):
    file_name = f"speedtest_{mac}_{datetime.datetime.now().strftime('%m%d%Y_%H%M%S')}.json"
    with open(file_name, 'w') as f:
        json.dump(speed_results, f)
    return file_name

def upload_to_sftp(file_name, config):
    # Modified directory here
    remote_file_path = f"/home/fryscrypto/bandwidth_speed/{file_name}"  
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None 
    with pysftp.Connection(config['host'], username=config['username'], password=config['password'], cnopts=cnopts) as sftp:
        sftp.put(file_name, remote_file_path)
    print(f"{file_name} uploaded to {remote_file_path}")

def main():
    while True:
        results = speed_test()
        json_file = write_to_json(results)
        upload_to_sftp(json_file, config)
        time.sleep(3600)  # Wait for 1 hour before the next iteration

if __name__ == "__main__":
    main()
