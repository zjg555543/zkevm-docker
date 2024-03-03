import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

OKBAddress = "0xe223519d64C0A49e7C08303c2220251be6b70e1d"

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

    value = data.get(key, None)
    return str(value)


def replace_file(file_path, key, value):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    data[key] = value

    # 保存更新后的数据回文件
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

    print("两个新字段已添加并保存到文件.")

def get_genesis(file_path):
    # 读取JSON文件
    lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 删除第一行和最后一行
    lines = lines[1:-1]

    new_json_data = ''.join(lines)

    return str(new_json_data)

if __name__ == '__main__':
    print('Upgrade fork7...')

    # 编译合约
    command = '''
    rm -rf fork7;
    mkdir fork7;
    cd fork7;
    git clone https://github.com/0xPolygonHermez/zkevm-contracts.git;
    cd ./zkevm-contracts;
    git checkout v4.0.0-fork.7; 
    cp ../../fork6/zkevm-contracts/deployment/deploy_parameters.json upgrade/upgradeToV2/;
    cp ../../fork6/zkevm-contracts/deployment/deploy_output.json upgrade/upgradeToV2/;
    cp -rf ../../fork6/zkevm-contracts/.openzeppelin .;
    cp ../../fork6/zkevm-contracts/.env .;
    cd upgrade/upgradeToV2/;
    cp upgrade_parameters.json.example upgrade_parameters.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_file('./fork7/zkevm-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'consensusContract', "PolygonZkEVMEtrog")
    replace_file('./fork7/zkevm-contracts/upgrade/upgradeToV2/deploy_output.json', 'gasTokenAddress', OKBAddress)
    replace_file('./fork7/zkevm-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'realVerifier', True)
    replace_file('./fork7/zkevm-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockDelay', 360)
    replace_file('./fork7/zkevm-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockSalt', "0x0000000000000000000000000000000000000000000000000000000000000000")
    replace_file('./fork7/zkevm-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'polTokenAddress', OKBAddress)

    # 部署合约
    command = '''
    cd fork7/zkevm-contracts;
    npm i;
    npm run upgradev2:timelock:sepolia;
    cat upgrade/upgradeToV2/upgrade_output.json
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译节点
    command = '''
    cd fork7;
    git clone -b release/v0.5.13 https://github.com/0xPolygonHermez/zkevm-node.git;
    cd zkevm-node;
    docker build -t zkevm-node-fork7 -f ./Dockerfile .
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 配置节点
    rollupmgr = get_value('./fork6/zkevm-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork6/zkevm-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    deploymentBlockNumber = get_value('./fork6/zkevm-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    genesisStr = get_genesis('./fork6/zkevm-contracts/deployment/genesis.json')

    newPolygonZKEVM = get_value('./fork7/zkevm-contracts/upgrade/upgradeToV2/upgrade_output.json', 'newPolygonZKEVM')

    replace_variable('./config/fork7/test.genesis.config.json', '{polygonZkEVMAddress}', newPolygonZKEVM)
    replace_variable('./config/fork7/test.genesis.config.json', '{polygonRollupManagerAddress}', rollupmgr)
    replace_variable('./config/fork7/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork7/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork7/test.genesis.config.json', '{genesis}', genesisStr)
