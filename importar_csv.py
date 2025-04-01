import os
import pandas as pd
from sqlalchemy import create_engine, exc

# Caminhos das pastas onde estão os arquivos CSV
caminho_pasta_2023 = r"C:\Users\vitor\Downloads\Meu arquivo teste 3\2023"
caminho_pasta_2024 = r"C:\Users\vitor\Downloads\Meu arquivo teste 3\2024"

# Conectar ao MySQL
def conectar_mysql():
    try:
        usuario = "root"
        senha = "1518"
        host = "127.0.0.1"
        banco = "ans_dados"
        
        conn_string = f"mysql+mysqlconnector://{usuario}:{senha}@{host}/{banco}"
        return create_engine(conn_string)
    except Exception as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Limpar nomes de colunas para evitar erros no banco de dados
def limpar_nome_colunas(colunas):
    try:
        return [coluna.replace('"', '').replace(";", "_").replace(" ", "_") for coluna in colunas]
    except Exception as e:
        print(f"Erro ao limpar nome das colunas: {e}")
        return colunas

# Importar CSV para o banco de dados
def importar_csv_para_db(arquivo_csv, tabela, engine):
    try:
        df = pd.read_csv(arquivo_csv, encoding="utf-8", delimiter=";", on_bad_lines="skip")
        df.columns = limpar_nome_colunas(df.columns)  # Ajusta os nomes das colunas
        
        with engine.begin():  # Inicia a transação
            df.to_sql(tabela, engine, if_exists="replace", index=False)  # Importa os dados
        
        print(f"{arquivo_csv} importado com sucesso para '{tabela}'!")
    except exc.SQLAlchemyError as e:
        print(f"Erro ao importar {arquivo_csv} para '{tabela}': {e}")
    except Exception as e:
        print(f"Erro inesperado ao importar {arquivo_csv} para '{tabela}': {e}")

# Percorrer todas as pastas e processar arquivos CSV
def processar_pastas():
    engine = conectar_mysql()
    if not engine:
        return

    try:
        for pasta_raiz in [caminho_pasta_2023, caminho_pasta_2024]:
            for root, _, files in os.walk(pasta_raiz):
                for file in files:
                    if file.endswith(".csv"):  # Verifica se é um arquivo CSV
                        arquivo_csv = os.path.join(root, file)
                        nome_tabela = os.path.splitext(file)[0]  # Nome da tabela baseado no nome do arquivo
                        importar_csv_para_db(arquivo_csv, nome_tabela, engine)
    except Exception as e:
        print(f"Erro ao processar as pastas: {e}")

# Executar o script principal
def main():
    print("Iniciando importação de arquivos...")
    processar_pastas()
    print("Processo finalizado!")

if __name__ == "__main__":
    main()