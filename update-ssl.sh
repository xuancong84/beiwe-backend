
set -e -x -o pipefail
mkdir -p ssl
cd ssl

openssl genrsa -des3 -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -out rootCA.pem

openssl genrsa -out ssl.key 2048
openssl req -new -key ssl.key -out ssl.csr
openssl x509 -req -in ssl.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial \
	-out ssl.crt -days 3650 -sha256
#-extfile ssl.ext

