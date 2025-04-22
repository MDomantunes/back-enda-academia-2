from flask import Flask, jsonify, request  
import firebase_admin  
from firebase_admin import credentials, firestore  
from flask_cors import CORS 
import os 
import json
from dotenv import load_dotenv  

app = Flask(__name__)  
CORS(app)  


load_dotenv()
FBKEY = json.loads(os.getenv('CONFIG_FIREBASE')) 


cred = credentials.Certificate(FBKEY)  
firebase_admin.initialize_app(cred)

# Conecta ao Firestore.
db = firestore.client()

# ---- Rota principal de teste ----
@app.route('/', methods=['GET'])  # Define uma rota principal de teste.
def index():
    return 'API OK', 200  # Retorna uma mensagem simples para confirmar que a API está rodando.


# Rota para verificar o status de um aluno com base no CPF
@app.route('/verificar/<cpf>', methods=['GET'])
def verificar_cpf(cpf):
    doc_ref = db.collection('alunos').document(cpf)  # Acessa o documento com o CPF
    doc = doc_ref.get()  # Obtém os dados do documento

    if doc.exists:
        status = doc.to_dict().get('status')  # Pega o valor do campo 'status'
        return jsonify({'status': status}), 200
    else:
        return jsonify({'mensagem': 'CPF não encontrado'}), 404

# Rota para cadastrar um novo aluno
@app.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    dados = request.json  # Recebe os dados do corpo da requisição

    # Verifica se os dados obrigatórios foram enviados
    if 'cpf' not in dados or 'nome' not in dados:
        return jsonify({'mensagem': 'Dados incompletos'}), 400

    # Cria um novo documento com o CPF como identificador
    doc_ref = db.collection('alunos').document(dados['cpf'])
    doc_ref.set({
        'cpf': dados['cpf'],
        'nome': dados['nome'],
        'status': dados['status']
    })

    return jsonify({'mensagem': 'Aluno cadastrado com sucesso'}), 201


# Rota para editar os dados de um aluno já existente
@app.route('/alunos/<cpf>', methods=['PUT'])
def editar_aluno(cpf):
    dados = request.json  # Novos dados recebidos

    doc_ref = db.collection('alunos').document(cpf)  # Acessa o documento pelo CPF

    # Verifica se o aluno existe
    if not doc_ref.get().exists:
        return jsonify({'mensagem': 'Aluno não encontrado'}), 404

    # Atualiza o documento com os novos dados
    doc_ref.update(dados)

    return jsonify({'mensagem': 'Aluno atualizado com sucesso'}), 200


# Rota para deletar um aluno pelo CPF
@app.route('/alunos/<cpf>', methods=['DELETE'])
def excluir_aluno(cpf):
    doc_ref = db.collection('alunos').document(cpf)

    # Verifica se o aluno existe antes de excluir
    if not doc_ref.get().exists:
        return jsonify({'mensagem': 'Aluno não encontrado'}), 404

    doc_ref.delete()  # Deleta o documento
    return jsonify({'mensagem': 'Aluno excluído com sucesso'}), 200


# Rota para listar todos os alunos cadastrados
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = []  # Lista que vai armazenar os alunos
    docs = db.collection('alunos').stream()  # Recupera todos os documentos da coleção "alunos"

    # Itera sobre cada documento e adiciona os dados na lista
    for doc in docs:
        alunos.append(doc.to_dict())

    return jsonify(alunos), 200  # Retorna todos os alunos


# Rota para buscar os dados de um aluno específico usando o CPF
@app.route('/alunos/<cpf>', methods=['GET'])
def buscar_aluno(cpf):
    doc = db.collection('alunos').document(cpf).get()  # Acessa o documento

    # Verifica se existe e retorna os dados
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    else:
        return jsonify({'mensagem': 'Aluno não encontrado'}), 404

if __name__ == '__main__':
    app.run()