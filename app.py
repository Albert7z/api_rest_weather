# app.py (Versão Final Proativa com Alertas por E-mail)

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv


app = Flask(__name__)

# --- CONFIGURAÇÕES GERAIS ---
# ATENÇÃO: Em um projeto real, NUNCA deixe senhas e chaves no código.
# Use variáveis de ambiente para máxima segurança.
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///historico.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') # Seu e-mail do Google
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # Senha de App do Google

db = SQLAlchemy(app)
mail = Mail(app)


# --- MODELOS DE DADOS (AS TABELAS DO BANCO) ---
class HistoricoAQI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    indice_aqi = db.Column(db.Integer, nullable=False)
    risco = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'timestamp': self.timestamp.isoformat() + 'Z',
            'latitude': self.latitude, 'longitude': self.longitude,
            'indice_aqi': self.indice_aqi, 'risco': self.risco
        }

class Inscrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    ultimo_alerta = db.Column(db.DateTime, nullable=True)


# --- FUNÇÕES AUXILIARES ---
def interpretar_aqi(aqi):
    if aqi == 1: return {"risco": "Bom", "recomendacao": "Qualidade do ar excelente. Ótimo para atividades ao ar livre."}
    if aqi == 2: return {"risco": "Razoável", "recomendacao": "Qualidade do ar aceitável. Pessoas muito sensíveis podem sentir algum desconforto."}
    if aqi == 3: return {"risco": "Moderado", "recomendacao": "Membros de grupos sensíveis podem ter efeitos na saúde. Limite a exposição prolongada."}
    if aqi == 4: return {"risco": "Ruim", "recomendacao": "Qualquer pessoa pode começar a sentir efeitos na saúde. Reduza atividades ao ar livre."}
    if aqi == 5: return {"risco": "Muito Ruim", "recomendacao": "Alerta de saúde. Evite qualquer esforço ao ar livre."}
    return {"risco": "Desconhecido", "recomendacao": "Índice AQI inválido ou indisponível."}

def enviar_alerta(destinatario, aqi_info, lat, lon):
    try:
        msg = Message(
            subject=f"ALERTA: Qualidade do Ar Ruim na sua região ({aqi_info['risco']})",
            sender=app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        msg.body = f"""
        Olá!
        
        Detectamos uma piora na qualidade do ar na sua região monitorada ({lat}, {lon}).

        Nível de Risco Atual: {aqi_info['risco']} (Índice {aqi_info['indice_qualidade_ar']})
        Recomendação: {aqi_info['recomendacao']}

        Por favor, tome as precauções necessárias.

        - Seu Sistema de Alerta Climático Pessoal
        """
        mail.send(msg)
        print(f"E-mail de alerta enviado para {destinatario}")
    except Exception as e:
        print(f"Erro ao enviar e-mail para {destinatario}: {e}")


# --- ENDPOINTS DA API ---
@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.json
    email = data.get('email')
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not all([email, lat, lon]):
        return jsonify({"erro": "Dados incompletos (email, latitude, longitude são obrigatórios)"}), 400

    if Inscrito.query.filter_by(email=email).first():
        return jsonify({"mensagem": "Este e-mail já está registrado."}), 200

    novo_inscrito = Inscrito(email=email, latitude=str(lat), longitude=str(lon))
    db.session.add(novo_inscrito)
    db.session.commit()
    return jsonify({"mensagem": "Usuário registrado com sucesso para receber alertas!"}), 201

@app.route('/alerta-ar/<lat>/<lon>')
def get_alerta_ar(lat, lon):
    API_KEY = os.getenv('API_KEY_OWM')
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        dados_brutos = response.json()
        
        aqi = dados_brutos['list'][0]['main']['aqi']
        dados_interpretados = interpretar_aqi(aqi)

        novo_registro = HistoricoAQI(latitude=lat, longitude=lon, indice_aqi=aqi, risco=dados_interpretados['risco'])
        db.session.add(novo_registro)
        db.session.commit()
        
        # Lógica de Alerta Proativo
        if aqi >= 1: # Limite de risco para enviar alerta
            inscritos_na_area = Inscrito.query.filter_by(latitude=lat, longitude=lon).all()
            for inscrito in inscritos_na_area:
                if not inscrito.ultimo_alerta or (datetime.utcnow() - inscrito.ultimo_alerta > timedelta(hours=6)):
                    info_alerta = {
                        "risco": dados_interpretados['risco'],
                        "indice_qualidade_ar": aqi,
                        "recomendacao": dados_interpretados['recomendacao']
                    }
                    enviar_alerta(inscrito.email, info_alerta, lat, lon)
                    inscrito.ultimo_alerta = datetime.utcnow()
                    db.session.commit()
        
        resultado_final = {
            "aviso": "Dados em tempo real. Registro salvo no histórico.",
            "indice_qualidade_ar": aqi,
            "risco": dados_interpretados['risco'],
            "recomendacao": dados_interpretados['recomendacao'],
        }
        return jsonify(resultado_final), 200

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro: {str(e)}"}), 500

@app.route('/historico')
def get_historico():
    try:
        registros = HistoricoAQI.query.order_by(HistoricoAQI.timestamp.desc()).all()
        return jsonify([registro.to_dict() for registro in registros]), 200
    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro ao consultar o histórico: {str(e)}"}), 500

@app.route('/tendencia/<lat>/<lon>')
def get_tendencia(lat, lon):
    try:
        tempo_limite = datetime.utcnow() - timedelta(hours=3)
        registros_recentes = HistoricoAQI.query.filter(
            HistoricoAQI.latitude == lat,
            HistoricoAQI.longitude == lon,
            HistoricoAQI.timestamp >= tempo_limite
        ).order_by(HistoricoAQI.timestamp.asc()).all()

        if len(registros_recentes) < 2:
            tendencia = "Dados insuficientes para análise"
        else:
            primeiro_aqi = registros_recentes[0].indice_aqi
            ultimo_aqi = registros_recentes[-1].indice_aqi
            if ultimo_aqi > primeiro_aqi: tendencia = "Piorando"
            elif ultimo_aqi < primeiro_aqi: tendencia = "Melhorando"
            else: tendencia = "Estável"
        
        return jsonify({
            "coordenadas": {"latitude": lat, "longitude": lon},
            "periodo_analisado_horas": 3,
            "registros_encontrados": len(registros_recentes),
            "tendencia_qualidade_ar": tendencia
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro ao analisar a tendência: {str(e)}"}), 500


# --- BLOCO DE EXECUÇÃO ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Garante que TODAS as tabelas (HistoricoAQI e Inscrito) sejam criadas
    app.run(debug=True)
