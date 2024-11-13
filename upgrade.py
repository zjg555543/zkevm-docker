import subprocess
import logging
import json
import time
import os
import subprocess
import logging
import shutil
from eth_account import Account

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

L1Account = "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955";
L1AccountPrivate = "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356"
L1URL = "http://127.0.0.1:8545"

def create_account():
    Account.enable_unaudited_hdwallet_features()
    account, mnemonic = Account.create_with_mnemonic()

    # 获取账户地址
    address = account.address

    # 获取账户的私钥（注意：私钥非常敏感，请妥善保管）
    private_key = account._private_key.hex()

    # 打印结果
    print("\n")
    print(f"Address:        {address}")
    print(f"Private Key:    {private_key}")
    print(f"Mnemonic:       {mnemonic}")
    print("\n")

    # 构建包含账户信息的字典
    account_info = {
        "address": address,
        "private_key": private_key,
        "mnemonic": mnemonic
    }

    # 将字典保存为 JSON 文件
    json_file_path = 'account_info.json'  # 替换为你的实际 JSON 文件路径
    with open(json_file_path, 'w') as json_file:
        json.dump(account_info, json_file, indent=2)

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

def replace_variable(file_path, variable_name, new_value):
    if ".DS_Store" in file_path:
        return
    logging.info("file_path: " + file_path + " variable_name: " + variable_name + " new_value: " + new_value)
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

def get_all_file_paths(folder):
    file_paths = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            # 使用 abspath 转换为绝对路径
            file_paths.append(os.path.abspath(os.path.join(root, filename)))
    return file_paths

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

def copy_all_files(src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    logging.info('Copy all files from ' + src_folder + ' to ' + dest_folder)
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)
        
        if os.path.isfile(src_path):
            shutil.copy(src_path, dest_path)

def send_tx(form, fromkey, to, value, url):
    logging.info('Send tx' + form + ' ' + fromkey + ' ' + to + ' ' + value + ' ' + url)
    command = "cast send --legacy --from {form} --private-key {forKey} --rpc-url {url} {to} --value {value}"
    command = command.replace("{form}", form)
    command = command.replace("{forKey}", fromkey)
    command = command.replace("{url}", url)
    command = command.replace("{to}", to)
    command = command.replace("{value}", value)
    logging.info(command)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def deploy_fork9():
    # logging.info('Deploying fork9...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    # 停止所有节点
    command = "docker stop $(docker ps -aq); docker rm $(docker ps -aq); docker ps -a;"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    command = '''
    docker-compose up -d xlayer-l1
    sleep 10
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")
    send_tx(L1Account, L1AccountPrivate, genAccount, "10ether", L1URL)

    # 编译合约
    command = '''
    # rm -rf contracts; 
    # mkdir contracts;
    cd contracts; 
    # git clone -b release/v0.3.1 https://github.com/okx/xlayer-contracts.git; 
    # mv xlayer-contracts fork9;
    cd ./fork9; 
    cp ../../deployment/.env .env;  
    cp ../../deployment/create_rollup_parameters.json deployment/v2/create_rollup_parameters.json;
    cp ../../deployment/deploy_parameters.json deployment/v2/deploy_parameters.json;  
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('contracts/fork9/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('contracts/fork9/deployment/v2/create_rollup_parameters.json', '{ADMIN}', genAccount)
    replace_variable('contracts/fork9/deployment/v2/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./contracts/fork9/; 
    npm i; 
    npm run deploy:v2:localhost; 
    npm run  verify:v2:localhost; 
    cat deployment/v2/create_rollup_output.json;
    cat deployment/v2/deploy_output.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 替换文件
    adminAddress = loadAccount()["address"]
    dataCommitteeContract = get_value('./contracts/fork9/deployment/v2/create_rollup_output.json', 'polygonDataCommitteeAddress')
    polygonZkEVMAddress = get_value('./contracts/fork9/deployment/v2/create_rollup_output.json', 'rollupAddress')
    dynamicRoot = get_value('./contracts/fork9/deployment/v2/create_rollup_output.json', 'genesis')
    createRollupBlockNumber = get_value('./contracts/fork9/deployment/v2/create_rollup_output.json', 'createRollupBlockNumber')
    dynamicTimestamp = get_value_second('./contracts/fork9/deployment/v2/create_rollup_output.json', 'firstBatchData', 'timestamp')
    polygonRollupManagerAddress = get_value('./contracts/fork9/deployment/v2/deploy_output.json', 'polygonRollupManagerAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./contracts/fork9/deployment/v2/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    polygonZkEVMBridgeAddress = get_value('./contracts/fork9/deployment/v2/deploy_output.json', 'polygonZkEVMBridgeAddress')
    deploymentBlockNumber = get_value('./contracts/fork9/deployment/v2/deploy_output.json', 'deploymentRollupManagerBlockNumber')
    polTokenAddress = get_value('./contracts/fork9/deployment/v2/deploy_output.json', 'polTokenAddress')
    genesisStr = get_genesis('./contracts/fork9/deployment/v2/genesis.json')
    dynamicAlloc = get_erigon_genesis('./contracts/fork9/deployment/v2/genesis.json')
    logging.info(dynamicAlloc)

    # 拷贝模版
    copy_all_files('./config-template/common', './config/common')
    copy_all_files('./config-template/fork9', './config/fork9')
    copy_all_files('./config-template/fork13', './config/fork13')
    file_list = get_all_file_paths("./config")
    for file in file_list:
        replace_variable(file, '{polygonZkEVMAddress}', polygonZkEVMAddress)
        replace_variable(file, '{polygonRollupManagerAddress}', polygonRollupManagerAddress)
        replace_variable(file, '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
        replace_variable(file, '{deploymentBlockNumber}', deploymentBlockNumber)
        replace_variable(file, '{createRollupBlockNumber}', createRollupBlockNumber)
        replace_variable(file, '{genesis}', genesisStr)
        replace_variable(file, '{dynamicAlloc}', dynamicAlloc)
        replace_variable(file, '{dynamicRoot}', dynamicRoot)
        replace_variable(file, '{dynamicTimestamp}', dynamicTimestamp)
        replace_variable(file, '{adminAddress}', adminAddress)
        replace_variable(file, '{dataCommitteeContract}', dataCommitteeContract)
        replace_variable(file, '{polTokenAddress}', polTokenAddress)
        replace_variable(file, '{polygonZkEVMBridgeAddress}', polygonZkEVMBridgeAddress)


    logging.info("Config done.")

    # 设置da地址
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url {l1URL} {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://xlayer-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    command = command.replace("{genAccount}", genAccount)
    command = command.replace("{genPriveKey}", genPriveKey)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)
    command = command.replace("{l1URL}", L1URL)
    logging.info(command)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 50 -f | grep xlayer-sequencer")
    logging.info("Deploy fork9 done.")


def start_fork9():
    logging.info('Deploying fork9...')

    command = '''
    docker-compose up -d xlayer-state-db-fork9
    docker-compose up -d xlayer-pool-db-fork9
    docker-compose up -d xlayer-event-db-fork9
    docker-compose up -d xlayer-da-db
    docker-compose up -d xlayer-bridge-db
    docker-compose up -d xlayer-bridge-redis

    docker-compose up -d xlayer-da-fork9
    docker-compose up -d xlayer-executor-fork9
    docker-compose up -d xlayer-prover-fork9
    sleep 3
    docker-compose up -d xlayer-sync-fork9
    sleep 1
    docker-compose up -d xlayer-seq-fork9
    sleep 1
    docker-compose up -d xlayer-tm-fork9
    docker-compose up -d xlayer-seqs-fork9
    docker-compose up -d xlayer-gp-fork9
    docker-compose up -d xlayer-agg-fork9
    docker-compose up -d xlayer-rpc-fork9
    sleep 1
    docker-compose up -d kafka-zookeeper
    docker-compose up -d xlayer-bridge-kafka
    docker-compose up -d xlayer-bridge
    docker-compose up -d xlayer-bridge-ui
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")

def upgrade_fork13():
    logging.info('Upgrade fork13...')

    # 编译合约
    command = '''
    cd contract; 
    rm -rf fork13;
    mkdir fork13;
    git clone -b upstream/v8.1.0-rc.1-fork.13 https://github.com/okx/xlayer-contracts.git;
    mv xlayer-contracts fork13;
    cd ./fork13;
    cp ../../fork9/deployment/v2/deploy_parameters.json upgrade/upgradeToV2/;
    cp ../../fork9/deployment/v2/deploy_output.json upgrade/upgradeToV2/;
    cp -rf ../../fork9/.openzeppelin .;
    cp ../../fork9/.env .;
    cd upgrade/upgradeToV2/;
    cp upgrade_parameters.json.example upgrade_parameters.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'consensusContract', "PolygonValidiumEtrogIsolated")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'dataAvailabilityProtocol', "PolygonDataCommittee")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_output.json', 'gasTokenAddress', OKBAddress)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'realVerifier', True)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockDelay', 125)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockSalt', "0x0000000000000000000000000000000000000000000000000000000000000000")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'polTokenAddress', OKBAddress)

    # 部署合约
    command = '''
    cd fork8/xlayer-contracts;
    npm i;
    npm run upgradev2:timelock:sepolia;
    cat upgrade/upgradeToV2/upgrade_output.json
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 配置节点
    rollupmgr = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    deploymentBlockNumber = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    polygonZkEVMBridgeAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork6/xlayer-contracts/deployment/genesis.json')

    dataCommitteeContract = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'polygonDataCommittee')
    newPolygonZKEVM = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'newPolygonZKEVM')

    replace_variable('./config/fork8/test.da.toml', '{PolygonValidiumAddress}', newPolygonZKEVM)
    replace_variable('./config/fork8/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)

    replace_variable('./config/fork8/test.genesis.config.json', '{polygonZkEVMAddress}', newPolygonZKEVM)
    replace_variable('./config/fork8/test.genesis.config.json', '{polygonRollupManagerAddress}', rollupmgr)
    replace_variable('./config/fork8/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork8/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork8/test.genesis.config.json', '{genesis}', genesisStr)

    replace_variable('./config/fork8/config.bridge.toml', '{GenBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonBridgeAddress}', polygonZkEVMBridgeAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonRollupManagerAddress}', rollupmgr)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonZkEvmAddress}', newPolygonZKEVM)

    replace_variable('./docker-compose.yml', '{ETHEREUM_ROLLUP_MANAGER_ADDRESS_FORK8}', rollupmgr)
    replace_variable('./docker-compose.yml', '{ETHEREUM_BRIDGE_CONTRACT_ADDRESS_FORK8}', polygonZkEVMBridgeAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_PROOF_OF_EFFICIENCY_CONTRACT_ADDRESS_FORK8}', newPolygonZKEVM)
    replace_variable('./docker-compose.yml', '{POLYGON_ZK_EVM_BRIDGE_CONTRACT_ADDRESS_FORK8}', polygonZkEVMBridgeAddress)


if __name__ == '__main__':
    # deploy fork9
    create_account()
    deploy_fork9()
    start_fork9()
    for i in range(0, 10):
        logging.info("Waiting for 2s...")
        time.sleep(1)
        
    # upgrade fork13
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


