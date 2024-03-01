import subprocess
import logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

genAccount = "0x4E1eDE630015b6124555920cE07340055a83fFa4"
genPriveKey = "0x0a9d0d0c583897af3bd66ce1209a393c364f61d53c251416c6ff3f03a2d156db"
genMnemonic = "view bleak actress village ride dismiss load sausage want fitness cloth quantum"

def greet(name):
    print(f"Hello, {name}!")

def replace_variable(file_path, variable_name, new_value):
    logging.info("file_path: " + file_path)
    with open(file_path, 'r') as file:
        file_content = file.read()

    new_content = file_content.replace(variable_name, new_value)

    with open(file_path, 'w') as file:
        file.write(new_content)

if __name__ == '__main__':
    print('Deploying fork6...')

    command = "docker stop $(docker ps -aq); docker rm $(docker ps -aq);docker ps -a;docker rmi --force $(docker images -q);docker images"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # 编译合约
    command = "rm -rf x1-contracts; git clone -b release/v0.2.0 https://github.com/okx/x1-contracts.git; cd ./x1-contracts; cp ../config/deployment/deploy_parameters.json deployment/deploy_parameters.json;  cp ../config/deployment/.env .env;  cp ../config/deployment/hardhat.config.js hardhat.config.js;  cp ../config/deployment/1_createGenesis.js deployment/1_createGenesis.js"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    replace_variable('./x1-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./x1-contracts/deployment/deploy_parameters.json', '{ADMIN}', genAccount)

    # 编译node
    command = "rm -rf x1-node; git clone -b release/v0.2.0 https://github.com/okx/x1-node.git; cd x1-node; docker build -t x1-node-fork6 -f ./Dockerfile ."
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # 编译da
    command = "rm -rf x1-data-availability; git clone -b release/v0.2.0 https://github.com/okx/x1-data-availability.git; cd x1-data-availability; docker build -t x1-data-availability-fork6 -f ./Dockerfile ."
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # 部署合约
    command = "cd ./x1-contracts; npm run deploy:deployer:ZkEVM:sepolia; npm run  deploy:ZkEVM:sepolia; npm run  verify:ZkEVM:sepolia; cat deployment/genesis.json; cat deployment/deploy_output.json "
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)



    
