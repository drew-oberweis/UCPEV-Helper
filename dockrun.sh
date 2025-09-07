docker build --tag drewoberweis/ucpevbot .
docker stop ucpevbot_testing
docker rm ucpevbot_testing
docker create --name ucpevbot_testing drewoberweis/ucpevbot

docker start ucpevbot_testing