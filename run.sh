docker-compose up -d zkevm-state-db
docker-compose up -d zkevm-pool-db
docker-compose up -d zkevm-event-db
docker-compose up -d zkevm-bridge-db
docker-compose up -d zkevm-mock-l1-network
sleep 3

# docker-compose up -d zkevm-prover
# sleep 3
# # error, ignore
# docker-compose up -d zkevm-approve 
# docker-compose up -d zkevm-sync
# sleep 3

# docker-compose up -d zkevm-eth-tx-manager
# docker-compose up -d zkevm-sequencer
# docker-compose up -d zkevm-sequence-sender
# docker-compose up -d zkevm-l2gaspricer
# docker-compose up -d zkevm-aggregator
# docker-compose up -d zkevm-json-rpc

# docker-compose up -d zkevm-explorer-json-rpc
# docker-compose up -d zkevm-explorer-l1
# docker-compose up -d zkevm-explorer-l2
# docker-compose up -d zkevm-bridge-service
# docker-compose up -d zkevm-bridge-ui

docker ps -a
