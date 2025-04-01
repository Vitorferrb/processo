import requests
import zipfile
import os
from io import BytesIO
from bs4 import BeautifulSoup
from tqdm import tqdm

def limpar_tela():
    """Limpa a tela do terminal."""
    if os.name == 'nt':
        os.system('cls')  # Para Windows
    else:
        os.system('clear')  # Para sistemas Unix

def acessar_pagina(url):
    """Faz a requisição à URL e retorna o conteúdo HTML."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Erro no acesso. Código: {response.status_code}")
        return None

def buscar_anexos(soup):
    """Busca links de arquivos PDF que contenham 'Anexo I' ou 'Anexo II'."""
    links = soup.find_all("a")
    anexos = []

    for link in links:
        anexo_url = link.get('href', '')
        if anexo_url and not anexo_url.startswith("http"):
            anexo_url = "https://www.gov.br" + anexo_url

        if anexo_url.endswith(".pdf"):
            link_text = link.text.strip().lower()
            if "anexo i" in link_text or "anexo ii" in link_text:
                anexos.append(anexo_url)

    return anexos

def criar_arquivo_zip(nome_zip):
    """Define o caminho do arquivo ZIP na pasta Downloads."""
    zip_file_path = os.path.join(os.path.expanduser("~/Downloads"), f"{nome_zip}.zip")
    return zip_file_path

def baixar_e_compactar(anexos, zip_file_path):
    """Baixa os PDFs encontrados e os compacta em um único arquivo ZIP."""
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        with tqdm(total=len(anexos), desc="Baixando arquivos", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} arquivos") as pbar:
            for anexo_url in anexos:
                file_response = requests.get(anexo_url)
                if file_response.status_code == 200:
                    file_name = anexo_url.split("/")[-1]
                    file_data = BytesIO(file_response.content)

                    with zipf.open(file_name, 'w') as zf:
                        zf.write(file_data.read())

                    pbar.set_postfix_str(f"{file_name}")
                    pbar.update(1)

    print("\nArquivos PDF baixados e compactados com sucesso!")

def main():
    url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
    page_content = acessar_pagina(url)
    if not page_content:
        return

    limpar_tela()
    print("\nAcesso confirmado!\n")

    # Processa o HTML da página para encontrar os PDFs
    soup = BeautifulSoup(page_content, "html.parser")
    anexos = buscar_anexos(soup)

    if not anexos:
        print("\nNenhum arquivo PDF encontrado.\n")
        return

    # Solicita o nome do arquivo ZIP ao usuário
    zip_name = input("\nDigite o nome do arquivo ZIP (sem .zip): ")
    zip_file_path = criar_arquivo_zip(zip_name)

    limpar_tela()
    print(f"\nArquivo ZIP criado: {zip_file_path}\n")
    baixar_e_compactar(anexos, zip_file_path)

if __name__ == "__main__":
    main()