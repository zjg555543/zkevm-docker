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
    print('Update L2 bridge contract...')

    # 部署合约
    command = '''
    cd fork8/x1-contracts;
    npm i;
    npm run upgradev2L2:timelock:x1;
    cat upgrade/upgradeToV2/upgrade_output.json
    '''

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

