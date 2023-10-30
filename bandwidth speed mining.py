import speedtest
import json
import pysftp
import datetime
import time
import uuid

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def owen_decrypt(key, ciphertext):
    nonce, ct = ciphertext[:16], ciphertext[16:]
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ct) + decryptor.finalize()
    return plaintext
def decrypt_config():
    dlt = b'3\xa4\x1a\xbf\xa7t\xf8Dr\x8e\xce\xed\xed\xae\xf4!\x02\x9b\x08\x80\x0b\x82D\xfa\x8f\xca\x82\x03C\x0c\x9f\xd2'
    dlp = b'/I<C\xa7*cH8o=\xd8HR\xa5\x11VB\xc7\x1d\xcd\xd6\x13\xe8{\xbe0\xd0;\xd7\xc1;2\xe9\xe6\xff\xa5\x8b\xe7\x1c\xcd\x12+mYW\xeb\xd0\x15\x85`Uo\xf2\x82\xc0W8\xf6\xc8'
    knt = b':\xf5\xd9\xfce\xfb\xb6P\xear\x10\xd8\x99\xeb\x0e%\x1f\xd3\xa24\xe8\xda\xf7\xfa{%\x12\xc3H\xaf\x8a3'
    knp = b'"\xa0\xe1\xe8\x96b\xd8^<o\xbe\xbc\xd1\xccY\x03\x9fl\x8f\xb3\t\xf1\xc5\x15L\xc6j\x94f\xf9x\x1b!Y\x86[\xe9\xe6v\x11\x0f\xe1J\xdf\x1b\x90Q\xdc\xce\xee\xe44<-9Z\xe2Pn9\x8a\x12Wom\x1f\xf2\xeb\x84\xbay\xdc\xdd\xfbf \xc10\x88\xcf\xf8\xcd\x98\x89,\xac\xc6\xb2\xbcv7\xd8\xd9\xf70C\x00\r\n\xd2\xb4\xa60y\x18\xe4\x92\x16}6\x0f\x8f\xfcT[\xe4\x84\t\x19\xe4\xd5\xd4k\x1e"\x12\xe8\xa5\x08\xa6Gc\xb2&9\xe8\xd3Z\xae\xa4\x8c\x88l\xde\x1a.VA\x06\x8d\xdd\xebeb$\x94\x9c\x03=%\x05\xd5\x17\xcex9\xbd\xce\x9f\x16\xcag\xceS\xd7C\xa0\x02\x0c\xf9m_\x1d\xbdd|\xc9D\x06\xb6\x8c\xe0\xe0\xf9\xd1h\xef^`-\xf8,s0\xa5\xf7\xb1~\x95\xcf\xac\x13\x9b\x1f\xf8\x8e\\\xa0\xb5i'



    kas = owen_decrypt(dlt, dlp)
    cipher = Fernet(kas)
    ec = owen_decrypt(knt, knp)
    config = json.loads(cipher.decrypt(ec))
    return config

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
        f.close()
    return file_name

def upload_to_sftp(file_name, config):
    # Modified directory here
    remote_file_path = f"/home/fryscrypto/bandwidth_speed/{file_name}"  
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    connection = pysftp.Connection
    connection.timeout = 200
    with connection(config['host'], username=config['username'], password=config['password'], cnopts=cnopts) as sftp:
        sftp.put(file_name, remote_file_path)
    print(f"{file_name} uploaded to {remote_file_path}")

def main():
    while True:
        results = speed_test()
        json_file = write_to_json(results)
        time.sleep(2)
        config = decrypt_config()
        upload_to_sftp(json_file, config)
        time.sleep(3600)  # Wait for 1 hour before the next iteration

if __name__ == "__main__":
    main()
