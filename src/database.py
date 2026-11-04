# EN: Create the SQLite database from the generated CSV files.
# PT: Cria o banco SQLite a partir dos CSVs gerados.

import sqlite3
from pathlib import Path

import pandas as pd

from generate_data import DATA_DIR, OPENING_BALANCE

# EN: database file inside data/ (ignored by Git)
# PT: arquivo do banco dentro de data/ (ignorado pelo Git)
DB_PATH = DATA_DIR / "cashflow.db"


def build_database(
    receivables: pd.DataFrame,
    payables: pd.DataFrame,
    opening_balance: float,
    db_path: Path = DB_PATH,
) -> None:
    """
    EN: Write both tables and the opening balance to SQLite (replaces old data).
    PT: Grava as duas tabelas e o saldo inicial no SQLite (substitui dados antigos).
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    config = pd.DataFrame({"key": ["opening_balance"], "value": [opening_balance]})

    # EN: dates go in as ISO text, the SQLite standard
    # PT: datas entram como texto ISO, o padrão do SQLite
    with sqlite3.connect(db_path) as conn:
        receivables.to_sql("receivables", conn, if_exists="replace", index=False)
        payables.to_sql("payables", conn, if_exists="replace", index=False)
        config.to_sql("config", conn, if_exists="replace", index=False)


def read_table(name: str, db_path: Path = DB_PATH) -> pd.DataFrame:
    """
    EN: Read a table and convert date columns back to datetime.
    PT: Lê uma tabela e converte as colunas de data de volta para datetime.
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
    for col in ("due_date", "paid_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def get_opening_balance(db_path: Path = DB_PATH) -> float:
    """
    EN: Read the opening balance saved in the config table.
    PT: Lê o saldo inicial salvo na tabela config.
    """
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'opening_balance'"
        ).fetchone()
    return float(row[0])


def main() -> None:
    """
    EN: Load the CSVs from data/ and build the database.
    PT: Carrega os CSVs de data/ e monta o banco.
    """
    receivables = pd.read_csv(DATA_DIR / "receivables.csv")
    payables = pd.read_csv(DATA_DIR / "payables.csv")
    build_database(receivables, payables, OPENING_BALANCE)
    print(f"Banco criado: {DB_PATH}")
    print(f"Recebimentos: {len(read_table('receivables'))}")
    print(f"Pagamentos: {len(read_table('payables'))}")
    print(f"Saldo inicial: {get_opening_balance():.2f}")


if __name__ == "__main__":
    main()
