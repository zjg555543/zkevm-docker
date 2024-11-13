import subprocess
import logging
import json
import time
import psycopg2

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

def replace_file(file_path, key, value):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    data[key] = value

    # 保存更新后的数据回文件
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

    logging.info("两个新字段已添加并保存到文件.")

def zkevm_batchNumber():
    command = '''
    curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"zkevm_batchNumber","params":[],"id":83}' http://127.0.0.1:8123 | jq
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    parsed_data = json.loads(result.stdout)
    # 获取 result 的值并转换为十进制
    result_hex = parsed_data["result"]
    result_decimal = int(result_hex, 16)
    return result_decimal

def zkevm_verifiedBatchNumber():
    command = '''
    curl -X POST --data '{    "jsonrpc": "2.0",    "method": "zkevm_verifiedBatchNumber",    "params": [],    "id": 1}' -H "Content-Type: application/json" 127.0.0.1:8123 | jq
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    parsed_data = json.loads(result.stdout)
    # 获取 result 的值并转换为十进制
    result_hex = parsed_data["result"]
    result_decimal = int(result_hex, 16)
    return result_decimal

def send_tx():
    logging.info('Send tx...')

    account = loadAccount()
    command = "sleep 10; cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url http://127.0.0.1:8123 0xC949254d682D8c9ad5682521675b8F43b102aec4 --value 0.0001ether"

    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def deploy_fork9():
    logging.info('Deploying fork9...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    command = "docker stop $(docker ps -aq); docker rm $(docker ps -aq); docker ps -a;"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译合约
    command = '''
    rm -rf fork9; 
    mkdir fork9;
    cd fork9; 
    git clone -b release/v0.3.1 https://github.com/okx/xlayer-contracts.git; 
    cd ./xlayer-contracts; 
    cp ../../config/deployment/.env .env;  
    cp ../../config/deployment/create_rollup_parameters.json deployment/v2/create_rollup_parameters.json;
    cp ../../config/deployment/deploy_parameters.json deployment/v2/deploy_parameters.json;  
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('./fork9/xlayer-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./fork9/xlayer-contracts/deployment/v2/create_rollup_parameters.json', '{ADMIN}', genAccount)
    replace_variable('./fork9/xlayer-contracts/deployment/v2/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./fork9/xlayer-contracts; 
    npm i; 
    npm run deploy:v2:sepolia; 
    npm run  verify:v2:sepolia; 
    cat deployment/v2/create_rollup_output.json;
    cat deployment/v2/deploy_output.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 替换文件
    dataCommitteeContract = get_value('./fork9/xlayer-contracts/deployment/v2/create_rollup_output.json', 'polygonDataCommitteeAddress')
    deploymentBlockNumber = get_value('./fork9/xlayer-contracts/deployment/v2/create_rollup_output.json', 'createRollupBlockNumber')
    rollupManagerCreationBlockNumber = get_value('./fork9/xlayer-contracts/deployment/v2/deploy_output.json', 'deploymentRollupManagerBlockNumber')
    polygonZkEVMAddress = get_value('./fork9/xlayer-contracts/deployment/v2/create_rollup_output.json', 'rollupAddress')

    polygonRollupManagerAddress = get_value('./fork9/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonRollupManagerAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork9/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    polygonZkEVMBridgeAddress = get_value('./fork9/xlayer-contracts/deployment/v2/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork9/xlayer-contracts/deployment/v2/genesis.json')

    replace_variable('./config/fork9/test.da.toml', '{PolygonValidiumAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork9/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)

    replace_variable('./config/fork9/test.genesis.config.json', '{polygonZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork9/test.genesis.config.json', '{polygonRollupManagerAddress}', polygonRollupManagerAddress)
    replace_variable('./config/fork9/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork9/test.genesis.config.json', '{rollupCreationBlockNum}', deploymentBlockNumber)
    replace_variable('./config/fork9/test.genesis.config.json', '{rollupManagerCreationBlockNumber}', rollupManagerCreationBlockNumber)
    replace_variable('./config/fork9/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork9/test.genesis.config.json', '{genesis}', genesisStr)
    replace_variable('./config/fork9/test.genesis.config.json', '{dataCommitteeContract}', dataCommitteeContract)

    replace_variable('./config/fork9/config.bridge.toml', '{GenBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork9/config.bridge.toml', '{PolygonBridgeAddress}', polygonZkEVMBridgeAddress)
    replace_variable('./config/fork9/config.bridge.toml', '{PolygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork9/config.bridge.toml', '{PolygonRollupManagerAddress}', polygonRollupManagerAddress)
    replace_variable('./config/fork9/config.bridge.toml', '{PolygonZkEvmAddress}', polygonZkEVMAddress)

    replace_variable('./docker-compose.yml', '{ETHEREUM_ROLLUP_MANAGER_ADDRESS}', polygonRollupManagerAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_BRIDGE_CONTRACT_ADDRESS}', polygonZkEVMBridgeAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_PROOF_OF_EFFICIENCY_CONTRACT_ADDRESS}', polygonZkEVMAddress)
    replace_variable('./docker-compose.yml', '{POLYGON_ZK_EVM_BRIDGE_CONTRACT_ADDRESS}', polygonZkEVMBridgeAddress)

    # 设置da地址
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://xlayer-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    command = command.replace("{genAccount}", genAccount)
    command = command.replace("{genPriveKey}", genPriveKey)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)
    logging.info(command)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 50 -f | grep xlayer-sequencer")
    logging.info("Deploy fork9 done.")


if __name__ == '__main__':
    # deploy fork9
    deploy_fork9()
    start_fork9()
    for i in range(0, 10):
        logging.info("Waiting for 2s...")
        time.sleep(1)
        send_tx()

    # upgrade fork8
    upgrade_fork13()
    schedule_fork13()
    logging.info("Waiting for 180s...")
    time.sleep(180)

    # 需要确保不再出块
    while True:
        batch = zkevm_batchNumber()
        verifyBatch = zkevm_verifiedBatchNumber()
        logging.info("batch: " + str(batch) + " verifyBatch: " + str(verifyBatch))
        time.sleep(10)
        if verifyBatch + 1 == batch:
            break 
        else:
            logging.info("wating...")
    
    batch = zkevm_batchNumber()
    # 停止fork9所有节点
    stop_fork9()
    time.sleep(30)

    # 执行 execute
    execute_fork13()
    time.sleep(30)

    # 启动 fork13 程序
    start_fork13(str(batch))
    time.sleep(30)


