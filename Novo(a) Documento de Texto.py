from flask import Flask, request, jsonify
from flask_cors import CORS

# ----- Configurações -----
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 8080
API_KEY = "key123"

# ----- Inicialização -----
app = Flask(__name__)
CORS(app)
jobs_list = []

# ----- Segurança -----
@app.before_request
def bloquear_acesso_direto():
    user_agent = request.headers.get('User-Agent', '')
    path = request.path

    # Permite /webhook (coletor) sempre
    if path == "/webhook":
        return

    # Permite apenas Roblox no /pets
    roblox_agents = ['Roblox', 'ROBLOX', 'RobloxApp', 'RobloxStudio']
    if not any(agent in user_agent for agent in roblox_agents):
        print(f"🚨 Acesso bloqueado: {user_agent}")
        return jsonify({"error": "Access denied"}), 403

# ----- Endpoint principal -----
@app.route("/pets", methods=["GET"])
def get_pets():
    # Retorna apenas as 2 últimas entradas
    return jsonify(jobs_list[-2:])

# ----- Webhook (para coletor) -----
@app.route("/webhook", methods=["POST"])
def webhook():
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        return "Unauthorized", 401

    data = request.json
    job_ids = data.get("job_ids", [])
    join_links = data.get("join_links", [])

    if job_ids or join_links:
        new_entry = {"job_ids": job_ids, "join_links": join_links}
        jobs_list.append(new_entry)
        print(f"✅ Novo Job adicionado: {new_entry}")

        # Mantém no máximo 10 registros recentes
        if len(jobs_list) > 10:
            jobs_list.pop(0)

    return "", 204

if __name__ == "__main__":
    print(f"🔒 Servidor protegido rodando em http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT)
