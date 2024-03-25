import subprocess
import logging
import json

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

def loadAccount():
    # 读取JSON文件
    with open("account_info.json", 'r') as json_file:
        account_info = json.load(json_file)
    return account_info

if __name__ == '__main__':
    print('Send tx...')

    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    command = "sleep 10; cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url http://127.0.0.1:8123 0xC949254d682D8c9ad5682521675b8F43b102aec4 --value 0.0001ether"

    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    
