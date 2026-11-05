# EN: Streamlit dashboard: critical week alert and stress scenarios.
# PT: Painel Streamlit: alerta de semana crítica e cenários de estresse.

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# EN: make the src/ folder importable
# PT: deixa a pasta src/ importável
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from database import DB_PATH, build_database, read_table  # noqa: E402
from generate_data import (  # noqa: E402
    OPENING_BALANCE,
    SEED,
    delinquency_rate,
    make_payables,
    make_receivables,
)
from scenarios import run_scenarios  # noqa: E402


def brl(value: float) -> str:
    """
    EN: Format a number as Brazilian currency.
    PT: Formata um número como moeda brasileira.
    """
    text = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {text}"


def ensure_database() -> None:
    """
    EN: Create the synthetic data and the database if they do not exist yet.
    PT: Cria os dados sintéticos e o banco se ainda não existirem.
    """
    if DB_PATH.exists():
        return
    rng = np.random.default_rng(SEED)
    receivables = make_receivables(rng)
    payables = make_payables(rng)
    build_database(receivables, payables, OPENING_BALANCE)


@st.cache_data
def load_results() -> tuple[pd.DataFrame, dict[str, pd.DataFrame], float]:
    """
    EN: Run all scenarios once and get the delinquency rate.
    PT: Roda todos os cenários uma vez e calcula a inadimplência.
    """
    ensure_database()
    summary, weekly = run_scenarios()
    rate = delinquency_rate(read_table("receivables"))
    return summary, weekly, rate


def show_alert(summary: pd.DataFrame) -> None:
    """
    EN: Show the critical week alert for the base scenario.
    PT: Mostra o alerta de semana crítica do cenário base.
    """
    week = summary.loc[0, "critical_week"]
    if pd.isna(week):
        st.success("Base: o caixa não fica negativo no período projetado.")
    else:
        st.error(f"Base: o caixa fica negativo na semana {int(week)}.")


def balance_chart(weekly: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    EN: One balance column per scenario, indexed by week number.
    PT: Uma coluna de saldo por cenário, indexada pelo número da semana.
    """
    size = min(len(df) for df in weekly.values())
    data = {name: df["balance"].to_numpy()[:size] for name, df in weekly.items()}
    return pd.DataFrame(data, index=pd.RangeIndex(1, size + 1, name="Semana"))


def main() -> None:
    """
    EN: Build the dashboard page.
    PT: Monta a página do painel.
    """
    st.set_page_config(page_title="Projeção de Fluxo de Caixa", layout="wide")
    st.title("Projeção de Fluxo de Caixa e Alerta de Risco")
    st.caption("Dados 100% sintéticos (seed=42). Projeto educacional.")

    summary, weekly, rate = load_results()
    show_alert(summary)

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo inicial", brl(OPENING_BALANCE))
    col2.metric("Inadimplência", f"{rate:.2f}%")
    col3.metric("Menor saldo (base)", brl(summary.loc[0, "min_balance"]))

    st.subheader("Saldo projetado por semana")
    # EN: axis labels make the chart readable
    # PT: títulos nos eixos deixam o gráfico legível
    st.line_chart(balance_chart(weekly), x_label="Semana", y_label="Saldo (R$)")

    st.subheader("Comparação dos cenários")
    # EN: make sure the scenario names are a column, not a hidden index
    # PT: garante que os nomes dos cenários sejam coluna, não índice escondido
    table = summary.reset_index() if "scenario" not in summary.columns else summary.copy()
    table = table.rename(columns={
        "index": "scenario",
        "scenario": "scenario",
    }).rename(columns={
        "scenario": "Cenário",
        "critical_week": "Semana crítica",
        "weeks_negative": "Semanas negativas",
        "min_balance": "Menor saldo",
        "final_balance": "Saldo final",
    })
    # EN: format money columns as BRL
    # PT: formata as colunas de dinheiro em reais
    for col in ("Menor saldo", "Saldo final"):
        table[col] = table[col].map(brl)
    st.dataframe(table, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    main()
  
