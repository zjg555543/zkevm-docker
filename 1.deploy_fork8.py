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
    print('Deploying fork8...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    command = '''
    docker stop $(docker ps -aq); 
    docker rm $(docker ps -aq);
    docker ps -a;
    docker rmi --force $(docker images -q);
    docker images
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译合约
    command = '''
    rm -rf fork8; 
    mkdir fork8;
    cd fork8; 
    git clone -b release/v0.3.0 https://github.com/okx/xlayer-contracts.git; 
    cd ./xlayer-contracts; 
    cp ../../config/deployment/.env .env;  
    cp ../../config/deployment/create_rollup_parameters.json deployment/v2/create_rollup_parameters.json;
    cp ../../config/deployment/deploy_parameters.json deployment/v2/deploy_parameters.json;  
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('./fork8/xlayer-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./fork8/xlayer-contracts/deployment/v2/create_rollup_parameters.json', '{ADMIN}', genAccount)
    replace_variable('./fork8/xlayer-contracts/deployment/v2/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./fork8/xlayer-contracts; 
    npm i; 
    npm run deploy:v2:sepolia; 
    npm run  verify:v2:sepolia; 
    cat deployment/v2/create_rollup_output.json;
    cat deployment/v2/deploy_output.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # # 编译node
    # command = '''
    # cd fork8; 
    # git clone -b zjg/fork8-upgrade https://github.com/okx/xlayer-node.git; 
    # cd xlayer-node; 
    # docker build -t xlayer-node-fork8 -f ./Dockerfile .
    # '''
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # logging.info(result.stdout)

    # # 编译da
    # command = '''
    # cd fork8;
    # git clone -b zjg/fork8-upgrade https://github.com/okx/xlayer-data-availability.git; 
    # cd xlayer-data-availability; 
    # docker build -t xlayer-data-availability-fork8 -f ./Dockerfile .
    # '''
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # logging.info(result.stdout)

    # # 编译bridge
    # command = ''' 
    # cd fork8;
    # git clone -b hai/fork8 https://github.com/okx/xlayer-bridge-service.git;
    # cd xlayer-bridge-service;
    # docker build -t xlayer-bridge-service-fork8 -f ./Dockerfile .
    # '''

    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # logging.info(result.stdout)

    # 替换文件
    dataCommitteeContract = get_value('./fork8/xlayer-contracts/deployment/v2/create_rollup_output.json', 'polygonDataCommitteeAddress')
    deploymentBlockNumber = get_value('./fork8/xlayer-contracts/deployment/v2/create_rollup_output.json', 'createRollupBlockNumber')
    polygonZkEVMAddress = get_value('./fork8/xlayer-contracts/deployment/v2/create_rollup_output.json', 'rollupAddress')

    polygonRollupManagerAddress = get_value('./fork8/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonRollupManagerAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork8/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    polygonZkEVMBridgeAddress = get_value('./fork8/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork8/xlayer-contracts/deployment/v2/genesis.json')

    replace_variable('./config/fork8/test.da.toml', '{PolygonValidiumAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork8/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)

    replace_variable('./config/fork8/test.genesis.config.json', '{polygonZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork8/test.genesis.config.json', '{polygonRollupManagerAddress}', polygonRollupManagerAddress)
    replace_variable('./config/fork8/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork8/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork8/test.genesis.config.json', '{genesis}', genesisStr)
    replace_variable('./config/fork8/test.genesis.config.json', '{dataCommitteeContract}', dataCommitteeContract)

    replace_variable('./config/fork8/config.bridge.toml', '{GenBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonBridgeAddress}', polygonZkEVMBridgeAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonRollupManagerAddress}', polygonRollupManagerAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonZkEvmAddress}', polygonZkEVMAddress)

    replace_variable('./docker-compose.yml', '{ETHEREUM_BRIDGE_CONTRACT_ADDRESS_FORK8}', polygonZkEVMBridgeAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_PROOF_OF_EFFICIENCY_CONTRACT_ADDRESS_FORK8}', polygonZkEVMAddress)
    replace_variable('./docker-compose.yml', '{POLYGON_ZK_EVM_BRIDGE_CONTRACT_ADDRESS_FORK8}', polygonZkEVMBridgeAddress)

    # 设置da地址
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://xlayer-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    command = command.replace("{genAccount}", genAccount)
    command = command.replace("{genPriveKey}", genPriveKey)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)
    logging.info(command)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 50 -f | grep xlayer-sequencer")
    logging.info("Deploy fork8 done.")

