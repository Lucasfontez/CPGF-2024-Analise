import pandas as pd
import sqlite3
import os
import glob

# Caminhos — ajuste conforme seu ambiente virtual
PASTA_CSV = r'C:\Users\User\Desktop\Projeto_GOV_DATA'
BANCO_DB  = r'C:\Users\User\Desktop\Projeto_GOV_DATA\Database_CPGF\cpgf_2024.db'

def converter_valor(serie):
    return (
        serie.astype(str)
             .str.strip()
             .str.replace('.', '', regex=False) # Remove separador de milhar
             .str.replace(',', '.', regex=False) # Troca vírgula decimal por ponto
             .pipe(pd.to_numeric, errors='coerce') # Converte pra número, NaN se falhar
    )

def renomear_colunas(df):
    """Padroniza nomes de colunas: remove acentos, coloca em minúsculas com underscore.
    Necessário porque os CSVs do Portal vêm com nomes como 'NOME ÓRGÃO SUPERIOR'.
    """
    mapa = {
        'CÓDIGO ÓRGÃO SUPERIOR': 'codigo_orgao_superior',
        'NOME ÓRGÃO SUPERIOR': 'nome_orgao_superior',
        'CÓDIGO ÓRGÃO': 'codigo_orgao',
        'NOME ÓRGÃO': 'nome_orgao',
        'CÓDIGO UNIDADE GESTORA': 'codigo_unidade_gestora',
        'NOME UNIDADE GESTORA': 'nome_unidade_gestora',
        'ANO EXTRATO': 'ano_extrato',
        'MÊS EXTRATO': 'mes_extrato',
        'CPF PORTADOR': 'cpf_portador',
        'NOME PORTADOR': 'nome_portador',
        'CNPJ OU CPF FAVORECIDO': 'cnpj_cpf_favorecido',
        'NOME FAVORECIDO': 'nome_favorecido',
        'TRANSAÇÃO': 'transacao',
        'DATA TRANSAÇÃO': 'data_transacao',
        'VALOR TRANSAÇÃO': 'valor_transacao',
    }
    df.columns = df.columns.str.strip()
    return df.rename(columns=mapa)

# --------------------------------------------------------------------------------
# BUSCA OS 12 CSVs MENSAIS
# Procura arquivos que começam com '2024_' e contêm 'CPGF' no nome
# --------------------------------------------------------------------------------

arquivos = glob.glob(os.path.join(PASTA_CSV, '**', '*.csv'), recursive=True)
arquivos = [a for a in arquivos if os.path.basename(a).startswith('2024_') and 'CPGF' in a.upper()]

if not arquivos:
    print("Nenhum arquivo encontrado! Verifique o caminho PASTA_CSV.")
    exit()

print(f"{len(arquivos)} arquivo(s) encontrado(s)\n")

# --------------------------------------------------------------------------------
# CARGA NO SQLITE (um CSV por vez)
# O primeiro CSV recria a tabela (replace) e os demais acrescentam o (append).
# Encoding windows-1252 porque é o padrão dos CSVs do Portal da Transparência.
# ---------------------------------------------------------------------------------

conn = sqlite3.connect(BANCO_DB)
total_inserido = 0

for i, arquivo in enumerate(sorted(arquivos)):
    try:
        df = pd.read_csv(
            arquivo,
            sep=';', # Separador padrão dos CSVs do Portal
            encoding='windows-1252', # Encoding dos arquivos do governo
            encoding_errors='replace', # Caracteres inválidos viram '?'
            dtype=str,  # Lê tudo como texto pra tratar depois
            quotechar='"'
        )
        df = renomear_colunas(df)
        df['valor_transacao'] = converter_valor(df['valor_transacao'])
        df['ano_extrato']     = pd.to_numeric(df['ano_extrato'], errors='coerce')
        df['mes_extrato']     = pd.to_numeric(df['mes_extrato'], errors='coerce')

        # Primeiro arquivo recria a tabela, os demais acrescentam
        modo = 'replace' if i == 0 else 'append'
        df.to_sql('cpgf', conn, if_exists=modo, index=False, chunksize=500)

        total_inserido += len(df)
        print(f"OK {os.path.basename(arquivo)} - {len(df):,} registros | Total: {total_inserido:,}")

    except Exception as e:
        print(f"ERRO em {os.path.basename(arquivo)}: {e}")

# --------------------------------------------------------------------------------
# VALIDAÇÃO — confirma que os dados foram carregados corretamente
# --------------------------------------------------------------------------------

total_db = pd.read_sql("SELECT COUNT(*) as total FROM cpgf", conn).iloc[0, 0]
amostra  = pd.read_sql(
    "SELECT valor_transacao, typeof(valor_transacao) AS tipo FROM cpgf LIMIT 5",
    conn
)
conn.close()

print(f"\nIMPORTACAO CONCLUIDA!")
print(f"Total no banco: {total_db:,}")
print(f"\nAmostra de valores:")
print(amostra.to_string(index=False))