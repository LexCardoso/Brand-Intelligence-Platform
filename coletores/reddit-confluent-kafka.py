import requests
import json
from confluent_kafka import Producer
import time

# Configuração do Kafka
conf = {
    'bootstrap.servers': 'localhost:19092',  # Porta externa do Redpanda
    'client.id': 'reddit-collector'
}

# Criar producer
producer = Producer(conf)

# Callback para confirmação
def delivery_report(err, msg):
    if err is not None:
        print(f'❌ Erro: {err}')
    else:
        print(f'✓ Enviado: {msg.key()}')

# Coletar Reddit
def coletar_reddit(termo):
    url = f"https://www.reddit.com/search.json?q={termo}&sort=new&limit=10"
    headers = {'User-Agent': 'BrandIntel/1.0'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        posts = data['data']['children']
        
        for post in posts:
            p = post['data']
            
            # Dados simples
            msg = {
                'fonte': 'reddit',
                'termo': termo,
                'titulo': p['title'],
                'subreddit': p['subreddit'],
                'score': p['score'],
                'timestamp': int(time.time())
            }
            
            # Enviar para Kafka
            producer.produce(
                'reddit-posts',
                key=str(p['id']),
                value=json.dumps(msg),
                callback=delivery_report
            )
            
            print(f"📤 {p['title'][:50]}...")
        
        # Esperar envio
        producer.flush()
        return len(posts)
    return 0

# Teste
print("Coletando dados do Reddit...")
total = coletar_reddit("Nike")
print(f"\n✅ Total enviado ao Kafka: {total}")
print("Ver no Redpanda Console: http://localhost:8080")