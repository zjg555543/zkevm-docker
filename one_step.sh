docker stop $(docker ps -aq); docker rm $(docker ps -aq);docker ps -a


cd ../

#rm -rf ./zkevm-contracts

git clone -b v0.1.2 https://github.com/0xPolygonHermez/zkevm-node.git
git clone -b v0.1.0 https://github.com/0xPolygonHermez/zkevm-bridge-service.git
git clone -b v1.1.0-fork.4 https://github.com/0xPolygonHermez/zkevm-contracts

cd ./zkevm-node
make build-docker
cd -

cd ./zkevm-bridge-service
make build-docker

cd -
cd ./zkevm-contracts
rm deployment/deploy_output.json 
git reset  --hard

cp ../zkevm-docker/config/deploy_parameters.json deployment/deploy_parameters.json
cp ../zkevm-docker/config/contract_env_example .env
cp ../zkevm-docker/config/1_createGenesis.js deployment/1_createGenesis.js 



cd -
cd zkevm-docker  

docker-compose up -d zkevm-state-db
docker-compose up -d zkevm-pool-db
docker-compose up -d zkevm-event-db
docker-compose up -d zkevm-bridge-db
docker-compose up -d zkevm-mock-l1-network
sleep 3

exit

# echo "转账，转账，转账 0x2ecf31ece36ccac2d3222a303b1409233ecbb225"

cd ../zkevm-contracts
npm i
npm run deploy:testnet:ZkEVM:localhost

docker-compose up -d zkevm-prover
sleep 3
# error, ignore
#docker-compose up -d zkevm-approve 
docker-compose up -d zkevm-sync
sleep 3

docker-compose up -d zkevm-eth-tx-manager
sleep 3
docker-compose up -d zkevm-sequencer
sleep 3
docker-compose up -d zkevm-sequence-sender
sleep 3
docker-compose up -d zkevm-l2gaspricer
sleep 3
docker-compose up -d zkevm-aggregator
sleep 3
docker-compose up -d zkevm-json-rpc

docker-compose up -d zkevm-explorer-json-rpc
sleep 3
docker-compose up -d zkevm-explorer-l1
sleep 3
docker-compose up -d zkevm-explorer-l2
sleep 3
docker-compose up -d zkevm-bridge-service
sleep 3
docker-compose up -d zkevm-bridge-ui

docker ps -a

docker-compose logs --tail 10 -f
