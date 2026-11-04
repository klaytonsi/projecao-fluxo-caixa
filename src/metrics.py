# EN: Cash flow metrics: weekly balance, days of cash, critical week.
# PT: Métricas de fluxo de caixa: saldo semanal, dias de caixa, semana crítica.

from typing import Optional

import pandas as pd

from database import get_opening_balance, read_table
from generate_data import START, delinquency_rate

WEEKS = 13  # EN: ~90 days / PT: ~90 dias


def _weekly_sum(
    df: pd.DataFrame, date_col: str, start: pd.Timestamp, weeks: int
) -> pd.Series:
    """
    EN: Sum amounts per week index (0..weeks-1), filling empty weeks with 0.
    PT: Soma valores por semana (0..weeks-1), preenchendo semanas vazias com 0.
    """
    idx = (df[date_col] - start).dt.days // 7
    mask = (idx >= 0) & (idx < weeks)
    sums = df.loc[mask, "amount"].groupby(idx[mask]).sum()
    return sums.reindex(range(weeks), fill_value=0.0)


def weekly_balance(
    receivables: pd.DataFrame,
    payables: pd.DataFrame,
    opening_balance: float,
    start: pd.Timestamp = START,
    weeks: int = WEEKS,
) -> pd.DataFrame:
    """
    EN: Weekly projected balance. Money comes in on paid_date, goes out on due_date.
    PT: Saldo projetado semanal. Dinheiro entra na paid_date e sai na due_date.
    """
    inflow = _weekly_sum(receivables, "paid_date", start, weeks)
    outflow = _weekly_sum(payables, "due_date", start, weeks)
    result = pd.DataFrame({"inflow": inflow, "outflow": outflow})
    result["balance"] = opening_balance + (result["inflow"] - result["outflow"]).cumsum()
    result.insert(0, "week", result.index + 1)
    return result.round(2)


def days_of_cash(balance: float, payables: pd.DataFrame) -> float:
    """
    EN: Days of cash = balance / average daily outflow.
    PT: Dias de caixa = saldo / média diária de saídas.
    """
    span = (payables["due_date"].max() - payables["due_date"].min()).days + 1
    daily_outflow = payables["amount"].sum() / span
    return round(balance / daily_outflow, 1)


def critical_week(weekly: pd.DataFrame) -> Optional[int]:
    """
    EN: First week with balance below zero (None if it never happens).
    PT: Primeira semana com saldo abaixo de zero (None se nunca acontecer).
    """
    negative = weekly[weekly["balance"] < 0]
    return int(negative["week"].iloc[0]) if not negative.empty else None


def main() -> None:
    """
    EN: Read the database and print the base metrics.
    PT: Lê o banco e imprime as métricas base.
    """
    receivables = read_table("receivables")
    payables = read_table("payables")
    opening = get_opening_balance()

    weekly = weekly_balance(receivables, payables, opening)
    print(weekly.to_string(index=False))
    print(f"Semana crítica: {critical_week(weekly)}")
    print(f"Dias de caixa: {days_of_cash(opening, payables)}")
    print(f"Inadimplência: {delinquency_rate(receivables)}%")


if __name__ == "__main__":
    main()
