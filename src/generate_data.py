# EN: Generate synthetic cash flow data (seed=42, reproducible).
# PT: Gera dados sintéticos de fluxo de caixa (seed=42, reproduzível).

from pathlib import Path

import numpy as np
import pandas as pd

# EN: fixed seed, so every run creates the same data
# PT: semente fixa, para cada execução gerar os mesmos dados
SEED = 42
N_CLIENTS = 25           # EN: number of clients / PT: número de clientes
N_SUPPLIERS = 15         # EN: number of suppliers / PT: número de fornecedores
N_RECEIVABLES = 1500     # EN: receivables / PT: recebimentos
N_PAYABLES = 1000        # EN: payables / PT: pagamentos
DAYS = 365               # EN: 12 months / PT: 12 meses
START = pd.Timestamp("2025-01-01")  # EN: start date / PT: data inicial
OPENING_BALANCE = 50_000.00         # EN: fixed opening cash / PT: saldo inicial fixo

# EN: output folder inside the cloned project (ignored by Git)
# PT: pasta de saída dentro do projeto clonado (ignorada pelo Git)
DATA_DIR = Path("data")


def make_receivables(rng: np.random.Generator) -> pd.DataFrame:
    """
    EN: Build receivables, with some paid late.
    PT: Cria recebimentos, com alguns pagos com atraso.
    """
    # EN: late payment rate between 8% and 12% / PT: taxa de atraso entre 8% e 12%
    late_rate = rng.uniform(0.08, 0.12)
    issue_day = rng.integers(0, DAYS, N_RECEIVABLES)
    terms = rng.choice([30, 45, 60], N_RECEIVABLES)  # EN: payment terms / PT: prazos
    is_late = rng.random(N_RECEIVABLES) < late_rate
    delay = np.where(is_late, rng.integers(15, 91, N_RECEIVABLES), 0)
    due_day = issue_day + terms

    clients = [f"Cliente {i:02d}" for i in range(1, N_CLIENTS + 1)]
    return pd.DataFrame({
        "client": rng.choice(clients, N_RECEIVABLES),
        "amount": rng.uniform(200, 5000, N_RECEIVABLES).round(2),
        "due_date": START + pd.to_timedelta(due_day, unit="D"),
        "paid_date": START + pd.to_timedelta(due_day + delay, unit="D"),
    })


def make_payables(rng: np.random.Generator) -> pd.DataFrame:
    """
    EN: Build payables (bills to suppliers).
    PT: Cria pagamentos (contas a pagar para fornecedores).
    """
    suppliers = [f"Fornecedor {i:02d}" for i in range(1, N_SUPPLIERS + 1)]
    return pd.DataFrame({
        "supplier": rng.choice(suppliers, N_PAYABLES),
        "amount": rng.uniform(100, 4000, N_PAYABLES).round(2),
        "due_date": START + pd.to_timedelta(rng.integers(0, DAYS, N_PAYABLES), unit="D"),
    })


def delinquency_rate(receivables: pd.DataFrame) -> float:
    """
    EN: Share of receivables paid after the due date, in percent.
    PT: Percentual de recebimentos pagos depois do vencimento, em %.
    """
    return round((receivables["paid_date"] > receivables["due_date"]).mean() * 100, 2)


def print_summary(receivables: pd.DataFrame, payables: pd.DataFrame) -> None:
    """
    EN: Print the numbers to check against the README.
    PT: Imprime os números para conferir com o README.
    """
    print("Meses: 12")
    print(f"Clientes com recebimento: {receivables['client'].nunique()}")
    print(f"Fornecedores com pagamento: {payables['supplier'].nunique()}")
    print(f"Recebimentos: {len(receivables)}")
    print(f"Pagamentos: {len(payables)}")
    print(f"Inadimplência: {delinquency_rate(receivables)}%")
    print(f"Saldo inicial: {OPENING_BALANCE:.2f}")


def main() -> None:
    """
    EN: Generate the data and save it as CSV.
    PT: Gera os dados e salva em CSV.
    """
    rng = np.random.default_rng(SEED)
    receivables = make_receivables(rng)
    payables = make_payables(rng)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    receivables.to_csv(DATA_DIR / "receivables.csv", index=False)
    payables.to_csv(DATA_DIR / "payables.csv", index=False)

    print_summary(receivables, payables)


if __name__ == "__main__":
    main()
