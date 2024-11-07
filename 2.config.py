import subprocess
import logging
import json
import shutil

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

def get_value_second(file_path, key1, key2):
    # 读取JSON文件
    with open(file_path, 'r') as file:
        data = json.load(file)

    value = data.get(key1, None)
    value2 = value.get(key2, None)
    return str(value2)

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

def get_erigon_genesis(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    new_json_obj = {}
    temp_array = data.get("genesis", None)
    for item in temp_array:
        add = str(item["address"])
        new_item = item
        if "bytecode" in item:
            new_item["code"] = item["bytecode"]
            del new_item["bytecode"] 
        else:
            new_item["code"] = None

        if "storage" not in item:
            new_item["storage"] = None

        del new_item["address"]
        
        new_json_obj[add] = new_item

    return json.dumps(new_json_obj, indent=4)

if __name__ == '__main__':
    print('Config ...')

    # 获取变量
    adminAccount = loadAccount()["address"]
    dataCommitteeContract = get_value('./fork13/xlayer-contracts/deployment/v2/create_rollup_output.json', 'polygonDataCommitteeAddress')
    rawDeplymentBlockNumber = get_value('./fork13/xlayer-contracts/deployment/v2/create_rollup_output.json', 'createRollupBlockNumber')
    deploymentBlockNumber = str(int(rawDeplymentBlockNumber) - 1000)
    polygonZkEVMAddress = get_value('./fork13/xlayer-contracts/deployment/v2/create_rollup_output.json', 'rollupAddress')
    dynamicRoot = get_value('./fork13/xlayer-contracts/deployment/v2/create_rollup_output.json', 'genesis')
    dynamicTimestamp = get_value_second('./fork13/xlayer-contracts/deployment/v2/create_rollup_output.json', 'firstBatchData', 'timestamp')
    polygonRollupManagerAddress = get_value('./fork13/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonRollupManagerAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork13/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    polygonZkEVMBridgeAddress = get_value('./fork13/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork13/xlayer-contracts/deployment/v2/genesis.json')
    dynamicAlloc = get_erigon_genesis('./fork13/xlayer-contracts/deployment/v2/genesis.json')
    logging.info(dynamicAlloc)

    # 拷贝模版
    shutil.copy('./config/template/dynamic-mynetwork-allocs.json', './config/erigon')
    shutil.copy('./config/template/dynamic-mynetwork-chainspec.json', './config/erigon')
    shutil.copy('./config/template/dynamic-mynetwork-conf.json', './config/erigon')
    shutil.copy('./config/template/test.erigon.seq.config.yaml', './config/erigon')
    shutil.copy('./config/template/test.genesis.config.json', './config/erigon')
    shutil.copy('./config/template/test.node.config.toml', './config/erigon')
    shutil.copy('./config/template/test.prover.config.json', './config/erigon')
    shutil.copy('./config/template/test.stateless_executor.config.json', './config/erigon')
    shutil.copy('./config/template/cdk.config.toml', './config/erigon')
    shutil.copy('./config/template/test.da.toml', './config/erigon')
    
    file_list = [
        "./config/erigon/test.genesis.config.json", 
        "./config/erigon/cdk.config.toml", 
        "./config/erigon/test.erigon.seq.config.yaml",
        "./config/erigon/dynamic-mynetwork-conf.json",
        "./config/erigon/dynamic-mynetwork-allocs.json",
        "./config/erigon/test.da.toml"
    ]

    for file in file_list:
        replace_variable(file, '{adminAccount}', adminAccount)
        replace_variable(file, '{polygonZkEVMAddress}', polygonZkEVMAddress)
        replace_variable(file, '{polygonRollupManagerAddress}', polygonRollupManagerAddress)
        replace_variable(file, '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
        replace_variable(file, '{genesisBlockNumber}', deploymentBlockNumber)
        replace_variable(file, '{genesis}', genesisStr)
        replace_variable(file, '{dynamicAlloc}', dynamicAlloc)
        replace_variable(file, '{dynamicRoot}', dynamicRoot)
        replace_variable(file, '{dynamicTimestamp}', dynamicTimestamp)
        replace_variable(file, '{dataCommitteeContract}', dataCommitteeContract)
        replace_variable(file, '{polygonValidiumAddress}', polygonZkEVMAddress)
        replace_variable(file, '{dataCommitteeAddress}', dataCommitteeContract)
        replace_variable(file, '{polygonZkEVMBridgeAddress}', polygonZkEVMBridgeAddress)

    logging.info("Config done.")

