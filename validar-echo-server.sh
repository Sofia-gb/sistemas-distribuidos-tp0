#!/bin/bash

MESSAGE=$1
SERVER_CONTAINER="server"
SUCCESS_CODE=0
SUCCESS_MESSAGE="action: test_echo_server | result: success"
FAIL_MESSAGE="action: test_echo_server | result: fail"
FAIL_CODE=1
NETWORK_NAME="tp0_testing_net"
SERVER_PORT=$(grep '^SERVER_PORT' ./server/config.ini | cut -d '=' -f2 | tr -d '[:space:]')

if [ -z "$MESSAGE" ]; then
    MESSAGE="Mensaje de prueba para el servidor echo"
fi

EXPECTED_RESPONSE="$MESSAGE"

SERVER_IP=$(docker inspect \
  --format '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$SERVER_CONTAINER")

if [ -z "$SERVER_IP" ]; then
    echo $FAIL_MESSAGE
    exit $FAIL_CODE
fi

RESPONSE=$(docker run --rm --network container:$SERVER_CONTAINER busybox sh -c "echo $MESSAGE | nc -w 2 $SERVER_IP $SERVER_PORT")

if [ "$RESPONSE" == "$EXPECTED_RESPONSE" ]; then
    echo $SUCCESS_MESSAGE
    exit $SUCCESS_CODE
else
    echo $FAIL_MESSAGE
    exit $FAIL_CODE
fi
