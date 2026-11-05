# Projeção de Fluxo de Caixa e Alerta de Risco / Cash Flow Projection and Risk Alert

> 🇧🇷 [Português](#-português) · 🇺🇸 [English](#-english)

**Painel / Dashboard:** https://projecao-fluxo-caixa-5dn5w4thnfd8u2czcs9ufx.streamlit.app/
**Notebook (Kaggle):** https://www.kaggle.com/code/klaytonsilva/proje-o-de-fluxo-de-caixa-e-alerta-de-risco

---

## 🇧🇷 Português

> Projeto educacional de portfólio. Todos os dados são sintéticos e fictícios; não representam nenhuma empresa real e não há dados pessoais (LGPD).

### 1. Problema que busquei resolver

Pequenas e médias empresas pagam fornecedores, salários e aluguel em datas fixas, mas os clientes pagam em 30, 45 ou 60 dias, e alguns atrasam. Quando o dinheiro que entra demora mais que o dinheiro que sai, o caixa fica negativo, mesmo que a empresa venda bem.

A pergunta do projeto: **"Em que semana o caixa desta empresa fica negativo e o que acontece se as vendas caírem ou os maiores clientes atrasarem?"**

### 2. Como desenvolvi a solução

1. **Dados sintéticos** (`src/generate_data.py`): empresa fictícia com 12 meses de operação, cerca de 25 clientes ("Cliente 01"...) e 15 fornecedores ("Fornecedor 01"...), gerados com `seed=42` (o resultado é sempre o mesmo). Alguns recebimentos atrasam de propósito para simular inadimplência.
2. **Banco de dados** (`src/database.py`): os dados ficam em um arquivo SQLite, sem servidor.
3. **Métricas** (`src/metrics.py`): saldo projetado semanal por 90 dias, dias de caixa, inadimplência e semana crítica.
4. **Cenários** (`src/scenarios.py`):
   - **A:** vendas caem 20%.
   - **B:** os 3 maiores clientes (maior soma de recebimentos no ano) atrasam 30 dias.
   - **C:** A + B juntos.
5. **Painel** (`app/streamlit_app.py`): gráfico do saldo por cenário, tabela comparativa em R$ e alerta de semana crítica.
6. **Notebook** (`notebooks/01_fluxo_caixa.ipynb`): roda do zero (instala dependências, gera os dados, calcula cenários e gráfico), sem depender de arquivo salvo na sessão.

**Por quê dessas escolhas:** dados sintéticos evitam problemas de LGPD e deixam o projeto reproduzível por qualquer pessoa; SQLite e Pandas são leves e não custam nada; Streamlit entrega um painel público sem precisar de servidor próprio.

### 3. Tecnologias utilizadas

- **Python** e **Pandas**: geração de dados, métricas e projeções.
- **SQLite**: banco leve em um único arquivo.
- **Matplotlib / gráficos do Streamlit**: visualização.
- **Streamlit**: painel final com alerta de semana crítica.
- **Kaggle** e **GitHub**: notebook e código.

### 4. Resultados alcançados

Dados gerados com `seed=42`: 1.500 recebimentos e 1.000 pagamentos. Os 3 maiores clientes foram Cliente 13, Cliente 06 e Cliente 08.

| Cenário | Semana crítica | Semanas com saldo negativo | Saldo mínimo | Saldo final (90 dias) |
|---|---|---|---|---|
| Base | 3 | 4 | -R$ 28.630,67 | R$ 135.226,97 |
| A: vendas -20% | 2 | 9 | -R$ 55.131,06 | R$ 26.135,98 |
| B: 3 maiores clientes atrasam 30 dias | 3 | 6 | -R$ 43.419,77 | R$ 106.256,83 |
| C: A + B | 2 | 11 | -R$ 67.874,11 | R$ 2.959,88 |

- Inadimplência (recebimentos pagos com atraso): **11,07%**
- Saldo inicial: **R$ 50.000,00**

**Leitura dos resultados:** mesmo no cenário base o caixa fica negativo na semana 3. Com queda de 20% nas vendas (A) o problema aparece uma semana antes e dura 9 semanas. O atraso dos 3 maiores clientes (B) não antecipa a semana crítica, mas aumenta o tempo no negativo e a profundidade do buraco. No cenário C o saldo final quase zera (R$ 2.959,88), ou seja, a empresa passa a maior parte dos 90 dias no vermelho.

### 5. Aprendizados

- Lucro e caixa são coisas diferentes: uma empresa pode vender bem e mesmo assim ficar sem dinheiro por causa do prazo de recebimento.
- Fixar a `seed` torna a simulação reproduzível: qualquer pessoa roda e chega nos mesmos números.
- Ajustar os parâmetros dos dados muda o resultado (a semana crítica passou de 2 para 3 depois de um ajuste), então é importante registrar os números finais só depois de rodar a versão definitiva.
- Cenários combinados (C) podem ser bem piores que a soma intuitiva dos separados.
- Separar o código em módulos pequenos (`generate_data`, `database`, `metrics`, `scenarios`) facilita testar e reaproveitar no painel e no notebook.

### 6. Como executar e estrutura de pastas

```bash
pip install -r requirements.txt
python src/generate_data.py      # gera os dados em data/
streamlit run app/streamlit_app.py
```

Para o notebook: abra `notebooks/01_fluxo_caixa.ipynb` no Kaggle e use **Run All**. A primeira célula instala as dependências e a segunda gera os dados.

```
projecao-fluxo-caixa/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/01_fluxo_caixa.ipynb
├── src/
│   ├── generate_data.py
│   ├── database.py
│   ├── metrics.py
│   └── scenarios.py
├── app/streamlit_app.py
└── data/            (gerado pelo código, ignorado no Git)
```

### 7. Diferença para outro projeto

O [relatorio-financeiro-automatizado](https://github.com/klaytonsi/relatorio-financeiro-automatizado) **consolida o passado**. Este projeto **prevê o futuro e simula cenários**.

---

## 🇺🇸 English

> Educational portfolio project. All data is synthetic and fictional; it does not represent any real company and contains no personal data (LGPD/GDPR).

### 1. Problem I set out to solve

Small and medium businesses pay suppliers, salaries and rent on fixed dates, but customers pay in 30, 45 or 60 days, and some are late. When incoming cash is slower than outgoing cash, the balance goes negative even if sales are strong.

The project question: **"In which week does this company's cash go negative, and what happens if sales drop or the biggest customers pay late?"**

### 2. How I built the solution

1. **Synthetic data** (`src/generate_data.py`): a fictional company with 12 months of operation, about 25 customers ("Cliente 01"...) and 15 suppliers ("Fornecedor 01"...), generated with `seed=42` (same result every run). Some receipts are late on purpose to simulate defaults.
2. **Database** (`src/database.py`): data is stored in a single SQLite file, no server needed.
3. **Metrics** (`src/metrics.py`): weekly projected balance for 90 days, days of cash, delinquency rate and critical week.
4. **Scenarios** (`src/scenarios.py`):
   - **A:** sales drop 20%.
   - **B:** the 3 biggest customers (highest yearly receipts) pay 30 days late.
   - **C:** A + B together.
5. **Dashboard** (`app/streamlit_app.py`): balance chart per scenario, comparison table in R$ and critical-week alert.
6. **Notebook** (`notebooks/01_fluxo_caixa.ipynb`): runs from scratch (installs dependencies, generates data, computes scenarios and chart), with no dependency on files saved in the session.

**Why these choices:** synthetic data avoids privacy issues and makes the project reproducible by anyone; SQLite and Pandas are lightweight and free; Streamlit delivers a public dashboard without my own server.

### 3. Technologies used

- **Python** and **Pandas**: data generation, metrics and projections.
- **SQLite**: lightweight single-file database.
- **Matplotlib / Streamlit charts**: visualization.
- **Streamlit**: final dashboard with critical-week alert.
- **Kaggle** and **GitHub**: notebook and code.

### 4. Results achieved

Data generated with `seed=42`: 1,500 receipts and 1,000 payments. The 3 biggest customers were Cliente 13, Cliente 06 and Cliente 08.

| Scenario | Critical week | Weeks with negative balance | Minimum balance | Final balance (90 days) |
|---|---|---|---|---|
| Base | 3 | 4 | -R$ 28,630.67 | R$ 135,226.97 |
| A: sales -20% | 2 | 9 | -R$ 55,131.06 | R$ 26,135.98 |
| B: top 3 customers pay 30 days late | 3 | 6 | -R$ 43,419.77 | R$ 106,256.83 |
| C: A + B | 2 | 11 | -R$ 67,874.11 | R$ 2,959.88 |

- Delinquency rate (receipts paid late): **11.07%**
- Starting balance: **R$ 50,000.00**

**Reading the results:** even in the base case the balance turns negative in week 3. A 20% sales drop (A) brings the problem one week earlier and lasts 9 weeks. Late payment from the top 3 customers (B) does not move the critical week earlier, but increases the time in the red and the depth of the hole. In scenario C the final balance almost reaches zero (R$ 2,959.88), meaning the company spends most of the 90 days in the red.

### 5. What I learned

- Profit and cash are different things: a company can sell well and still run out of money because of receipt terms.
- Fixing the `seed` makes the simulation reproducible: anyone runs it and gets the same numbers.
- Changing the data parameters changes the result (the critical week moved from 2 to 3 after an adjustment), so final numbers must be recorded only after running the definitive version.
- Combined scenarios (C) can be much worse than the intuitive sum of the separate ones.
- Splitting the code into small modules (`generate_data`, `database`, `metrics`, `scenarios`) makes it easier to test and reuse in both the dashboard and the notebook.

### 6. How to run and folder structure

```bash
pip install -r requirements.txt
python src/generate_data.py      # generates data in data/
streamlit run app/streamlit_app.py
```

For the notebook: open `notebooks/01_fluxo_caixa.ipynb` on Kaggle and use **Run All**. The first cell installs dependencies and the second generates the data.

(Folder structure: see the tree in the Portuguese section above.)

### 7. Difference from another project

[relatorio-financeiro-automatizado](https://github.com/klaytonsi/relatorio-financeiro-automatizado) **consolidates the past**. This project **forecasts the future and simulates scenarios**.
