import csv
import datetime
import time


""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574
EXPECTED_BET_FIELDS = 6
BET_FIELDS_DELIMITER = ","
BET_VALUES_DELIMITER = "="
AGENCY = "AGENCY"
FIRST_NAME = "FIRST_NAME"
LAST_NAME = "LAST_NAME"
NUMBER = "NUMBER"
BIRTH_DATE = "BIRTH_DATE"
DNI = "DNI"


""" A lottery bet registry. """
class Bet:
    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        self.agency = int(agency)
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = datetime.date.fromisoformat(birthdate)
        self.number = int(number)
    
    @classmethod
    def deserialize(cls, data: list[str]):
        """
        Deserialize a bet from a string.
        The string must have the following format:
        "AGENCY=agency,FIRST_NAME=first_name,LAST_NAME=last_name,NUMBER=number,BIRTH_DATE=birth_date,DNI=dni"
        """
        fields = data.split(BET_FIELDS_DELIMITER)
        agency, first_name, last_name, number, birth_date, dni = None, None, None, None, None, None

        if len(fields) != EXPECTED_BET_FIELDS:
            raise ValueError("Invalid Bet format")

        for field in fields:
            field_type, field_value = field.split(BET_VALUES_DELIMITER)

            if field_type == AGENCY:
                agency = field_value
            elif field_type == FIRST_NAME:
                first_name = field_value
            elif field_type == LAST_NAME:
                last_name = field_value
            elif field_type == NUMBER:
                number = field_value
            elif field_type == BIRTH_DATE:
                birth_date = field_value
            elif field_type == DNI:
                dni = field_value
            else:
                raise ValueError(f"Invalid Bet format: {data}")

        return cls(agency, first_name, last_name, dni, birth_date, number)

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])

