import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

def loadAccount():
    # 读取JSON文件
    with open("account_info.json", 'r') as json_file:
        account_info = json.load(json_file)
    return account_info

def getBalance():
    command = '''
        cast rpc eth_getBalance 0x14dC79964da2C08b23698B3D3cc7Ca32193d9955 latest
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def sendEth():
    command = 'cast send -f 0x14dC79964da2C08b23698B3D3cc7Ca32193d9955 --private-key 0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356 --value 3ether --legacy ' + loadAccount()
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

if __name__ == '__main__':
    print('Init account')
    getBalance()
    sendEth()
    logging.info("Init account done")
