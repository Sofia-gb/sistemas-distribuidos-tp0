#!/bin/bash

CANTIDAD_PARAMETROS=2
CODIGO_ERROR=1
RANGO_CLIENTES='^[0-9]+$'

if [ "$#" -ne $CANTIDAD_PARAMETROS ]; then
    echo "El script de bash debe ejecutarse de la siguiente manera: $0 <archivo_salida> <cantidad_clientes>"
    exit $CODIGO_ERROR 
fi

ARCHIVO_SALIDA=$1
CANTIDAD_CLIENTES=$2

if ! [[ "$CANTIDAD_CLIENTES" =~ $RANGO_CLIENTES  ]]; then
    echo "Error: La cantidad de clientes debe ser un número entero no negativo."
    exit $CODIGO_ERROR
fi


echo "Nombre del archivo de salida: $ARCHIVO_SALIDA"
echo "Cantidad de clientes: $CANTIDAD_CLIENTES"
python3 generate_compose.py "$ARCHIVO_SALIDA" "$CANTIDAD_CLIENTES"