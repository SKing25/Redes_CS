from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import db

app = Flask(__name__)
socketio = SocketIO(app)
db.init_db()

IPS_PERMITIDAS_SERVIDOR = ['192.168.1.1', '127.0.0.1', '186.155.14.223']
IPS_PERMITIDAS_CLIENTE = ['192.168.1.2', '192.168.1.3', '127.0.0.1']

#AQUI LES DEJO EL CODIGO DE ANTES PA MANEJAR LAS IPS PERMITIDAS
#
#ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
#    print(f"[INTENTO DE ACCESO] IP detectada: {ip_cliente}")
#
#    if ip_cliente not in IPS_PERMITIDAS:
#        print(f"[RECHAZADO] IP no permitida: {ip_cliente}")
#        return f"<h1>Acceso denegado para {ip_cliente}</h1>", 403
#
#    print(f"[ACEPTADO] IP permitida: {ip_cliente}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/servidor', methods=['GET'])
def servidor():
    ip_servidor = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip_servidor not in IPS_PERMITIDAS_SERVIDOR:
        return render_template('servidor.html', mensaje=f"BRO tu ip no es servidor {ip_servidor}")
    productos = db.obtener_productos()
    return render_template('servidor.html', productos=productos, ip=ip_servidor)

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    return render_template('cliente.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
