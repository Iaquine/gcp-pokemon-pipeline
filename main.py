import functions_framework
import requests
import os
from google.cloud import firestore

# --- Configuração ---
# Instancia o cliente do Firestore.
# Em uma Cloud Function, ele automaticamente usa as credenciais do ambiente.
db = firestore.Client()
POKEMON_COLLECTION = 'pokemons' # Nome da coleção no Firestore

def process_single_pokemon(url: str):
    """
    Busca os dados de um Pokémon a partir de uma URL, extrai as informações
    necessárias e as salva no Firestore.
    """
    try:
        # 1. Faz a requisição para a API do Pokémon
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lança um erro para status HTTP 4xx/5xx

        data = response.json()

        # 2. Extrai as informações desejadas
        pokemon_info = {
            'id': data.get('id'),
            'name': data.get('name'),
            'height': data.get('height'),
            'weight': data.get('weight'),
            # Extrai os nomes dos tipos em uma lista
            'types': [t['type']['name'] for t in data.get('types', [])],
            # Conta a quantidade total de movimentos
            'moves_count': len(data.get('moves', []))
        }

        # 3. Salva os dados no Firestore
        # Usamos o ID do Pokémon como o ID do documento para evitar duplicatas
        doc_ref = db.collection(POKEMON_COLLECTION).document(str(pokemon_info['id']))
        doc_ref.set(pokemon_info)
        
        print(f"Sucesso: Pokémon {pokemon_info['name']} (ID: {pokemon_info['id']}) salvo.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL {url}: {e}")
        return False
    except Exception as e:
        print(f"Um erro inesperado ocorreu ao processar {url}: {e}")
        return False


@functions_framework.http
def process_pokemon_urls(request):
    """
    Função principal acionada por HTTP (pelo Cloud Scheduler).
    Lê o arquivo urls.txt e processa cada uma.
    """
    print("Iniciando o processo de carga dos Pokémons...")
    
    # O caminho para o arquivo quando a função está implantada
    urls_file_path = os.path.join(os.path.dirname(__file__), 'urls.txt')

    try:
        with open(urls_file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ("Erro: O arquivo urls.txt não foi encontrado.", 500)

    success_count = 0
    error_count = 0

    for url in urls:
        if process_single_pokemon(url):
            success_count += 1
        else:
            error_count += 1

    final_message = f"Processo finalizado. {success_count} Pokémons salvos, {error_count} falhas."
    print(final_message)
    return (final_message, 200)