from flask import Flask, render_template, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uwuntu-kawaii-key'
socketio = SocketIO(app)

IPS_PERMITIDAS = ['192.168.1.2', '192.168.1.3', '127.0.0.1']

@app.route('/')
def index():
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    print(f"[INTENTO DE ACCESO] IP detectada: {ip_cliente}")

    if ip_cliente not in IPS_PERMITIDAS:
        print(f"[RECHAZADO] IP no permitida: {ip_cliente}")
        return f"<h1>Acceso denegado para {ip_cliente}</h1>", 403

    print(f"[ACEPTADO] IP permitida: {ip_cliente}")
    return render_template('chat.html', ip=ip_cliente)

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    return "hola cliente"


@socketio.on('message')
def manejar_mensaje(msg):
    ip_cliente = request.remote_addr
    mensaje_formateado = f"({ip_cliente}) dice: {msg}"
    print(f"[CHAT] {mensaje_formateado}")
    send(mensaje_formateado, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
