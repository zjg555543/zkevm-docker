# docker stop $(docker ps -aq); docker rm $(docker ps -aq);docker ps -a
# docker rmi --force $(docker images -q)

docker build -t zkevm-aggregator -f ./Dockerfile.aggregator .
docker build -t zkevm-seqsender -f ./Dockerfile.seqsender .

cd xlayer-erigon; make build-docker
