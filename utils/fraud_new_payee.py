import csv

TRANSACTION_FILE = "data/transactions.csv"

def is_new_payee(user_id, source):
    """
    Checks if this payee/source is new for the user
    """

    with open(TRANSACTION_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user_id"] == user_id and row["source"] == source:
                return False

    return True
