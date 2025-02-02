# ye3radius-frontend
Frontend written in python

# Simple usage

## build
```bash
git clone https://github.com/palw3ey/ye3radius-frontend.git
cd ~/ye3radius-frontend
docker build --no-cache --network=host -t ye3radius-frontend .
```

## run
```bash
docker run -dt --name ye3radius-frontend \
	-p 5000:5000 \
	-e DB_HOST=host -e DB_PORT=port -e DB_SSL_DISABLED=True \
	-e DB_USER=user -e DB_PASSWORD=password -e DB_NAME=radius \
	ye3radius-frontend 
```

## verify
```bash
# logs
docker logs ye3radius-frontend

# open the url in your browser : http://IpAddress:5000
```