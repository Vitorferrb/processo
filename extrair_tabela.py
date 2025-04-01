import os
import pdfplumber
import pandas as pd
import zipfile

# Função para limpar o terminal
def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")

# Listar arquivos PDF disponíveis
def listar_pdfs(pasta):
    pdfs = [arquivo for arquivo in os.listdir(pasta) if arquivo.endswith(".pdf")]
    
    if not pdfs:
        print("\nNenhum arquivo PDF encontrado.")
        return None
    
    print("\nArquivos disponíveis:")
    for i, pdf in enumerate(pdfs, start=1):
        print(f"{i}. {pdf}")
    
    while True:
        escolha = input("\nDigite o número do arquivo para converter: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(pdfs):
            return pdfs[int(escolha) - 1]
        print("Opção inválida. Tente novamente.")

# Escolher a pasta onde os PDFs estão armazenados
def escolher_pasta():
    pasta_base = os.path.join(os.path.expanduser("~"), "Downloads")
    print(f"Pasta base: {pasta_base}")
    
    while True:
        nome_pasta = input("\nNome da pasta dentro de Downloads: ").strip()
        pasta_especifica = os.path.join(pasta_base, nome_pasta)
        
        if os.path.isdir(pasta_especifica):
            print(f"Procurando arquivos na pasta: {pasta_especifica}")
            return pasta_especifica
        else:
            print("Pasta não encontrada. Tente novamente.\n")

# Extrair tabelas do PDF
def extrair_dados_pdf(pdf_path):
    colunas = [
        "PROCEDIMENTO", "RN (alteração)", "VIGÊNCIA", "OD", "AMB", "HCO", "HSO",
        "REF", "PAC", "DUT", "SUBGRUPO", "GRUPO", "CAPÍTULO"
    ]
    tabela_dados = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tabela = page.extract_table()
                if tabela:
                    for linha in tabela:
                        linha = [item.strip() if item else "" for item in linha]
                        linha += [""] * (len(colunas) - len(linha))
                        linha = linha[:len(colunas)]
                        tabela_dados.append(linha)
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return pd.DataFrame()
    
    return pd.DataFrame(tabela_dados, columns=colunas)

# Salvar os dados extraídos em um CSV
def salvar_em_csv(df, pasta_destino, nome_base):
    csv_path = os.path.join(pasta_destino, f"{nome_base}.csv")
    df.to_csv(csv_path, index=False, header=True, encoding="utf-8-sig")
    return csv_path

# Compactar o CSV gerado em um arquivo ZIP
def compactar_em_zip(csv_path, pasta_destino):
    zip_name = "resultado"
    zip_path = os.path.join(pasta_destino, f"{zip_name}.zip")
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_path, os.path.basename(csv_path))
    
    if os.path.exists(csv_path):
        os.remove(csv_path)
        print("\nArquivo CSV original excluído após compactação.")
    
    return zip_path

# Função principal do script
def main():
    pasta_destino = escolher_pasta()
    
    pdf_nome = listar_pdfs(pasta_destino)
    if not pdf_nome:
        print("\nNenhum arquivo selecionado.")
        return
    
    limpar_terminal()
    print(f"\nArquivo selecionado: {pdf_nome}")
    
    pdf_path = os.path.join(pasta_destino, pdf_nome)
    df = extrair_dados_pdf(pdf_path)
    
    if df.empty:
        print("\nErro: Nenhuma tabela extraída do PDF.")
        return
    
    nome_base = os.path.splitext(pdf_nome)[0] + "_dados"
    csv_path = salvar_em_csv(df, pasta_destino, nome_base)
    zip_path = compactar_em_zip(csv_path, pasta_destino)
    
    print(f"\nProcesso concluído! Arquivo ZIP salvo em: {zip_path}\n")

if __name__ == "__main__":
    main()