import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

def replace_variable(file_path, variable_name, new_value):
    # logging.info("file_path: " + file_path + " variable_name: " + variable_name + " new_value: " + new_value)
    with open(file_path, 'r') as file:
        file_content = file.read()

    new_content = file_content.replace(variable_name, new_value)

    with open(file_path, 'w') as file:
        file.write(new_content)

def get_value(file_path, key):
    # 读取JSON文件
    with open(file_path, 'r') as file:
        data = json.load(file)

    # 获取 "polygonZkEVMAddress" 的值
    value = data.get(key, None)
    return str(value)

def get_genesis(file_path):
    # 读取JSON文件
    lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 删除第一行和最后一行
    lines = lines[1:-1]

    new_json_data = ''.join(lines)

    return str(new_json_data)

def loadAccount():
    # 读取JSON文件
    with open("account_info.json", 'r') as json_file:
        account_info = json.load(json_file)
    return account_info

if __name__ == '__main__':
    print('Config ...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    command = '''
    docker stop $(docker ps -aq); 
    docker rm $(docker ps -aq);
    docker ps -a;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 替换文件
    deploymentBlockNumber = get_value('./fork9/zkevm-contracts/deployment/v2/create_rollup_output.json', 'createRollupBlockNumber')
    polygonZkEVMAddress = get_value('./fork9/zkevm-contracts/deployment/v2/create_rollup_output.json', 'rollupAddress')
    polygonRollupManagerAddress = get_value('./fork9/zkevm-contracts/deployment/v2/deploy_output.json', 'polygonRollupManagerAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork9/zkevm-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    polygonZkEVMBridgeAddress = get_value('./fork9/zkevm-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork9/zkevm-contracts/deployment/v2/genesis.json')
    dynamicAlloc = "" # TODO
    dynamicRoot = ""
    dynamicTimestamp = ""

    file_list = [
        "./config/fork9/test.genesis.config.json", 
        "./config/fork9/aggregator.node.config.toml", 
        "./config/fork9/seqsender.node.config.toml", 
        "./config/fork9/test.erigon.seq.config.yaml",
        "dynamic-mynetwork-conf.json",
        "dynamic-mynetwork-allocs.json"
    ]

    for file in file_list:
        replace_variable(file, '{polygonZkEVMAddress}', polygonZkEVMAddress)
        replace_variable(file, '{polygonRollupManagerAddress}', polygonRollupManagerAddress)
        replace_variable(file, '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
        replace_variable(file, '{genesisBlockNumber}', deploymentBlockNumber)
        replace_variable(file, '{genesis}', genesisStr)
        replace_variable(file, '{dynamicAlloc}', dynamicAlloc)
        replace_variable(file, '{dynamicRoot}', dynamicRoot)
        replace_variable(file, '{dynamicTimestamp}', dynamicTimestamp)


    logging.info("docker-compose logs --tail 50 -f | grep xlayer-sequencer")
    logging.info("Deploy fork9 done.")

