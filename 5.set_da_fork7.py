import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

def get_genesis(file_path):
    # 读取JSON文件
    lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 删除第一行和最后一行
    lines = lines[1:-1]

    new_json_data = ''.join(lines)

    return str(new_json_data)

def get_value(file_path, key):
    # 读取JSON文件
    with open(file_path, 'r') as file:
        data = json.load(file)

    value = data.get(key, None)
    return str(value)

def loadAccount():
    # 读取JSON文件
    with open("account_info.json", 'r') as json_file:
        account_info = json.load(json_file)
    return account_info

if __name__ == '__main__':
    print('Set fork7 da...')

    # 设置newZKEVM合约
    # newPolygonZKEVM = get_value('./fork7/x1-contracts/upgrade/upgradeToV2/upgrade_output.json', 'newPolygonZKEVM')
    # account = loadAccount()
    
    # command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {newZKEVM} 'setDataAvailabilityProtocol(address)'  {dataCommitteeContract}"

    # command = command.replace("{genAccount}", account["address"])
    # command = command.replace("{genPriveKey}", account["private_key"])
    # command = command.replace("{newZKEVM}", newPolygonZKEVM)

    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # logging.info(result.stdout)
    
