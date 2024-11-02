docker build --tag drewoberweis/ucpevbot .
docker create --env-file .env drewoberweis/ucpevbot