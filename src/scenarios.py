# EN: Stress scenarios: sales drop, late top clients, and both together.
# PT: Cenários de estresse: queda de vendas, maiores clientes atrasando e os dois juntos.

import pandas as pd

from database import get_opening_balance, read_table
from generate_data import START
from metrics import critical_week, weekly_balance

SALES_DROP = 0.20  # EN: sales fall 20% / PT: vendas caem 20%
TOP_N = 3          # EN: number of biggest clients / PT: número de maiores clientes
DELAY_DAYS = 30    # EN: extra delay in days / PT: atraso extra em dias


def apply_sales_drop(receivables: pd.DataFrame, drop: float = SALES_DROP) -> pd.DataFrame:
    """
    EN: Scenario A. Reduce every receivable amount by the given share.
    PT: Cenário A. Reduz o valor de todos os recebimentos pela fração dada.
    """
    result = receivables.copy()
    result["amount"] = (result["amount"] * (1 - drop)).round(2)
    return result


def top_clients(receivables: pd.DataFrame, n: int = TOP_N) -> list[str]:
    """
    EN: The n clients with the largest yearly sum of receivables.
    PT: Os n clientes com a maior soma anual de recebimentos.
    """
    totals = receivables.groupby("client")["amount"].sum()
    return totals.nlargest(n).index.tolist()


def apply_client_delay(
    receivables: pd.DataFrame,
    clients: list[str],
    days: int = DELAY_DAYS,
    start: pd.Timestamp = START,
) -> pd.DataFrame:
    """
    EN: Scenario B. Delay payments of the given clients (only those not yet paid at start).
    PT: Cenário B. Atrasa os pagamentos dos clientes dados (só os que ainda não foram pagos no início).
    """
    result = receivables.copy()
    mask = result["client"].isin(clients) & (result["paid_date"] >= start)
    result.loc[mask, "paid_date"] += pd.Timedelta(days=days)
    return result


def summarize(name: str, weekly: pd.DataFrame) -> dict:
    """
    EN: Key numbers of one scenario.
    PT: Números principais de um cenário.
    """
    return {
        "scenario": name,
        "critical_week": critical_week(weekly),
        "weeks_negative": int((weekly["balance"] < 0).sum()),
        "min_balance": weekly["balance"].min(),
        "final_balance": weekly["balance"].iloc[-1],
    }


def run_scenarios() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """
    EN: Run base, A, B and C. Return the summary table and each weekly balance.
    PT: Roda base, A, B e C. Devolve a tabela-resumo e o saldo semanal de cada um.
    """
    receivables = read_table("receivables")
    payables = read_table("payables")
    opening = get_opening_balance()
    clients = top_clients(receivables)

    variants = {
        "Base": receivables,
        "A: vendas -20%": apply_sales_drop(receivables),
        "B: top 3 atrasam 30d": apply_client_delay(receivables, clients),
        "C: A + B": apply_client_delay(apply_sales_drop(receivables), clients),
    }
    weekly = {
        name: weekly_balance(data, payables, opening) for name, data in variants.items()
    }
    summary = pd.DataFrame([summarize(name, df) for name, df in weekly.items()])
    summary["critical_week"] = summary["critical_week"].astype("Int64")
    return summary, weekly


def main() -> None:
    """
    EN: Print the scenario comparison.
    PT: Imprime a comparação dos cenários.
    """
    summary, _ = run_scenarios()
    print(f"Maiores clientes: {top_clients(read_table('receivables'))}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
