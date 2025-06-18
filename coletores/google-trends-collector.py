import pytrends
from pytrends.request import TrendReq
import pandas as pd
import json
from datetime import datetime
from kafka import KafkaProducer
import time

# Configuração do Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Configuração do pytrends
pytrends = TrendReq(hl='pt-BR', tz=360)

def coletar_trends(palavra_chave):
    """Coleta dados do Google Trends para uma palavra-chave"""
    try:
        # Constrói o payload
        pytrends.build_payload([palavra_chave], 
                              timeframe='now 7-d',  # últimos 7 dias
                              geo='BR')  # Brasil
        
        # Pega interesse ao longo do tempo
        interesse_tempo = pytrends.interest_over_time()
        
        if not interesse_tempo.empty:
            # Converte para formato JSON
            dados = {
                "timestamp": datetime.now().isoformat(),
                "palavra_chave": palavra_chave,
                "dados_interesse": interesse_tempo[palavra_chave].to_dict()
            }
            
            # Envia para o Kafka
            producer.send('google-trends', dados)
            print(f"✅ Dados coletados para '{palavra_chave}'")
            
            # Também pega as queries relacionadas
            related = pytrends.related_queries()
            if palavra_chave in related and related[palavra_chave]['rising'] is not None:
                dados_relacionados = {
                    "timestamp": datetime.now().isoformat(),
                    "palavra_chave": palavra_chave,
                    "tipo": "queries_relacionadas",
                    "dados": related[palavra_chave]['rising'].to_dict('records')
                }
                producer.send('google-trends', dados_relacionados)
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados para '{palavra_chave}': {e}")

def main():
    # Lista de marcas para monitorar
    marcas = [
        "Coca Cola",
        "Pepsi", 
        "Nike",
        "Adidas",
        "Samsung",
        "Apple iPhone"
    ]
    
    print("🚀 Iniciando coleta do Google Trends...")
    
    while True:
        for marca in marcas:
            coletar_trends(marca)
            time.sleep(10)  # Aguarda 10 segundos entre requisições
        
        print("⏰ Aguardando 1 hora para próxima coleta...")
        time.sleep(3600)  # Aguarda 1 hora

if __name__ == "__main__":
    # Cria o tópico no Kafka se não existir
    from kafka.admin import KafkaAdminClient, NewTopic
    
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers="localhost:19092",
            client_id='trends_admin'
        )
        
        topic = NewTopic(name="google-trends",
                        num_partitions=1,
                        replication_factor=1)
        
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print("✅ Tópico 'google-trends' criado no Kafka")
    except:
        print("ℹ️ Tópico já existe ou erro ao criar")
    
    main()