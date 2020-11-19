cd ..
cd audit_log
docker build -t audit:latest .

cd ..
cd processing
docker build -t processing:latest .

cd ..
cd receiver
docker build -t receiver:latest .

cd ..
cd storage
docker build -t storage:latest .

cd ..
cd deployment
docker-compose up -d
