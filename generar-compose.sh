#!/bin/bash

EXPECTED_PARAMS=2
ERROR_CODE=1
CLIENTS_RANGE='^[0-9]+$'

if [ "$#" -ne $EXPECTED_PARAMS ]; then
    echo "El script de bash debe ejecutarse de la siguiente manera: $0 <archivo_salida> <cantidad_clientes>"
    exit $ERROR_CODE 
fi

OUTPUT_FILE=$1
NUMBER_OF_CLIENTS=$2

if ! [[ "$NUMBER_OF_CLIENTS" =~ $CLIENTS_RANGE  ]]; then
    echo "Error: La cantidad de clientes debe ser un número entero no negativo."
    exit $ERROR_CODE
fi


echo "Nombre del archivo de salida: $OUTPUT_FILE"
echo "Cantidad de clientes: $NUMBER_OF_CLIENTS"
python3 generate_compose.py "$OUTPUT_FILE" "$NUMBER_OF_CLIENTS"