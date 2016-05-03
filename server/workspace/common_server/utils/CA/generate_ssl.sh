#!/bin/sh
echo "generate server key..."
if
openssl genrsa -out server.key 2048
then
	echo "generate server key ok."
else
	echo "generate server key failed!"
	exit 1;
fi

SUBJECT_SER='/C=cn/ST=FuJian/L=Xiamen/O=heat/OU=Game/CN=www.heat/emailAddress=zxw0819@gmail.com'
echo "generate server csr..."
if
openssl req -new -subj $SUBJECT_SER -key server.key -out server.csr
then
	echo "generate server csr ok."
else
	echo "generate server csr failed!"
	exit 1;
fi

echo "generate server cert..."
if
openssl ca -in server.csr -days 3650 -out server.crt -cert ca.crt -keyfile ca.key
then
	echo "generate server cert ok."
else
	echo "generate server cert failed!"
	exit 1;
fi
rm server.csr

echo "generate client key..."
if
openssl genrsa -out client.key 2048
then
        echo "generate client key ok."
else
        echo "generate client key failed!"
        exit 1;
fi

SUBJECT_SER='/C=cn/ST=FuJian/L=Xiamen/O=heat/OU=Game/CN=www/emailAddress=zxw0819@gmail.com'
echo "generate client csr..."
if
openssl req -new -subj $SUBJECT_SER -key client.key -out client.csr
then
        echo "generate client csr ok."
else
        echo "generate client csr failed!"
        exit 1;
fi

echo "generate client cert..."
if
openssl ca -in client.csr -days 3650 -out client.crt -cert ca.crt -keyfile ca.key
then
        echo "generate client cert ok."
else
        echo "generate client cert failed!"
        exit 1;
fi
rm client.csr
