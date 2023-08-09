cd ../

rm -rf zkevm-contracts

git clone -b v0.1.2 https://github.com/0xPolygonHermez/zkevm-node.git
git clone -b v0.1.0 https://github.com/0xPolygonHermez/zkevm-bridge-service.git
git clone -b v1.1.0-fork.4 https://github.com/0xPolygonHermez/zkevm-contracts

cd ./zkevm-node
make build-docker
cd -

cd ./zkevm-bridge-service
make build-docker
cd -
cd zkevm-docker  

cp config/deploy_parameters.json ../zkevm-contracts/deployment/deploy_parameters.json
cp config/contract_env_example ../zkevm-contracts/.env