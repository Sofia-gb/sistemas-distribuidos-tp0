import random
import sys
from enum import Enum
import yaml

DNI_LOW_BOUND = 10000000
DNI_HIGH_BOUND = 99999999
YEAR_LOW_BOUND = 1950
YEAR_HIGH_BOUND = 2000
BET_LOW_BOUND = 100
BET_HIGH_BOUND = 10000


class ComposeGeneratorError(Enum):
    """Represents the errors that can occur in the ComposeGenerator script."""

    ARGUMENT_COUNT_ERROR = (
        "El script de python debe ejecutarse de la siguiente manera: "
        "python3 generate_compose.py <archivo_salida> <cantidad_clientes>."
    )
    NUMBER_OF_CLIENTS_ERROR = (
        "Error: La cantidad de clientes debe ser un número entero no negativo."
    )


def exit_with_error(error):
    """ Exits the script with the given error message. """
    sys.stderr.write(error.value + "\n")
    sys.exit(1)


def get_arguments():
    """ Returns the output file and the number of clients from the command line arguments. """

    EXPECTED_PARAMS = 3  # generate_compose.py <archivo_salida> <n_clientes>

    if len(sys.argv) != EXPECTED_PARAMS:
        exit_with_error(ComposeGeneratorError.ARGUMENT_COUNT_ERROR)

    number_of_clients = sys.argv[2]
    output_file = sys.argv[1]

    if not number_of_clients.isdigit() or int(number_of_clients) < 0:
        exit_with_error(ComposeGeneratorError.NUMBER_OF_CLIENTS_ERROR)

    return parse_arguments(output_file, number_of_clients)


def parse_arguments(output_file, number_of_clients):
    """ Returns the output file and the number of clients as a tuple.
    If the output file does not end with .yaml or .yml, the .yaml extension it is added. 
    The number of clients is converted to an integer. """

    if not (output_file.endswith('.yaml') or output_file.endswith('.yml')):
        output_file += '.yaml'

    return output_file, int(number_of_clients)

def generate_random_dni():
    """Generates a random DNI number."""
    return str(random.randint(DNI_LOW_BOUND, DNI_HIGH_BOUND))

def generate_random_birthdate():
    """Generates a random birthdate."""
    year = random.randint(YEAR_LOW_BOUND, YEAR_HIGH_BOUND)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"

def generate_random_number():
    """Generates a random number."""
    return str(random.randint(BET_LOW_BOUND, BET_HIGH_BOUND))


def config_clients(compose, number_of_clients):
    """ Configures the clients in the compose file. 
     The number of clients is determined by the number_of_clients parameter. """

    names = ["Santiago", "Lionel", "Maria", "Pablo", "Ana"]
    surnames = ["Lorca", "Rinaldi", "Belis", "Saez", "Romero"]

    for i in range(1, number_of_clients + 1):
        compose["services"][f"client{i}"] = {
            "container_name": f"client{i}",
            "image": "client:latest",
            "build": "./client",
            "depends_on": ["server"],
            "environment": {
                "SERVER_HOST": "server",
                "CLIENT_ID": str(i),
                "CLIENT_LOG_LEVEL": "DEBUG",
                "CONFIG_FILE": "/config.yaml",
                "NOMBRE": random.choice(names),
                "APELLIDO": random.choice(surnames),
                "DOCUMENTO": generate_random_dni(),
                "NACIMIENTO": generate_random_birthdate(),
                "NUMERO": generate_random_number()
            },
            "networks": ["testing_net"],
            "entrypoint": "/client",
            "volumes": [
                {
                    "type": "bind",
                    "source": "./client/config.yaml",
                    "target": "/config.yaml"
                }
            ]
        }


def config_networks(compose):
    """ Configures the network in the compose file. """

    compose["networks"] = {
        "testing_net": {
            "ipam": {
                "driver": "default",
                "config": [
                    {
                        "subnet": "172.25.125.0/24",
                    }
                ]
            }
        }
    }


def config_server(compose):
    """ Configures the server in the compose file. """

    compose["services"]["server"] = {
            "container_name": "server",
            "image": "server:latest",
            "build": "./server",
            "entrypoint": "python3 /main.py",
            "environment": {
                "PYTHONUNBUFFERED": "1",
                "SERVER_LOG_LEVEL": "DEBUG",
                "CONFIG_FILE": "/config.ini"

            },
            "networks": ["testing_net"],
            "volumes": [
                {
                    "type": "bind",
                    "source": "./server/config.ini",
                    "target": "/config.ini"
                }
            ]
        }


def config_services(compose, number_of_clients):
    """ Configures the services in the compose file. This includes the server and the clients. """

    compose["services"] = {}
    config_server(compose)
    config_clients(compose, number_of_clients)


def generate_compose(output_file, number_of_clients):
    """ Generates the compose file with the given number of clients. 
    This file is saved with the given output file name.
    """

    compose = {"name": "tp0"}
    config_services(compose, number_of_clients)
    config_networks(compose)

    with open(output_file, "w") as f:
        yaml.dump(compose, f, default_flow_style=False)

    sys.stdout.write(f"Archivo {output_file} generado correctamente." + "\n")


if __name__ == "__main__":
    output_file, number_of_clients = get_arguments()
    generate_compose(output_file, number_of_clients)
