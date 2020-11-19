docker-compose down

docker rmi receiver --force
docker rmi audit_log --force
docker rmi processing --force
docker rmi storage --force
