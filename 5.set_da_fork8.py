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
    print('Set fork8 da...')

     # 设置da地址
    dataCommitteeContract = get_value('./fork8/x1-contracts/upgrade/upgradeToV2/upgrade_output.json', 'polygonDataCommittee')
    newPolygonZKEVM = get_value('./fork8/x1-contracts/upgrade/upgradeToV2/upgrade_output.json', 'newPolygonZKEVM')

    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://x1-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    
    account = loadAccount()
    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)


    # 设置newZKEVM合约
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {newZKEVM} 'setDataAvailabilityProtocol(address)'  {dataCommitteeContract}"

    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{newZKEVM}", newPolygonZKEVM)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    
