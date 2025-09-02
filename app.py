from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'el-codigo-divino-2024'
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_db()

IPS_PERMITIDAS_SERVIDOR = ['192.168.1.1', '127.0.0.1', '186.155.14.223']
IPS_PERMITIDAS_CLIENTE = ['192.168.1.2', '192.168.1.3', '127.0.0.1']


# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/servidor', methods=['GET'])
def servidor():
    ip_servidor = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip_servidor not in IPS_PERMITIDAS_SERVIDOR:
        return render_template('servidor.html', mensaje=f"Tu ip no es de servidor {ip_servidor}")
    productos = db.obtener_productos()
    return render_template('servidor.html', productos=productos, ip=ip_servidor)


@app.route('/cliente', methods=['GET'])
def cliente():
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip_cliente not in IPS_PERMITIDAS_CLIENTE:
        return render_template('cliente.html', mensaje=f"Tu ip no es de cliente {ip_cliente}")
    productos = db.obtener_productos()
    return render_template('cliente.html', productos=productos, ip=ip_cliente)


# ==================== HANDLERS DE EVENTOS SOCKET.IO ====================

@socketio.on('connect')
def handle_connect():
    print(f'Un nuevo cliente se ha conectado: {request.sid}')
    productos = db.obtener_productos()
    emit('inventario_inicial', {'productos': productos})


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Un cliente se ha desconectado: {request.sid}')


@socketio.on('crear_producto')
def handle_crear_producto(data):
    try:
        nombre = data.get('nombre')
        cantidad = data.get('cantidad')
        precio = data.get('precio')

        if not nombre or cantidad is None or precio is None:
            emit('error', {'mensaje': 'Faltan campos para crear el producto.'})
            return

        db.crear_producto(nombre, cantidad, precio)
        productos = db.obtener_productos()

        # Emitir a todos los clientes que el inventario se ha actualizado
        emit('actualizar_inventario', {
            'accion': 'crear',
            'productos': productos,
            'mensaje': f'Producto "{nombre}" creado con éxito.'
        }, broadcast=True)

    except Exception as e:
        emit('error', {'mensaje': str(e)})


@socketio.on('modificar_producto')
def handle_modificar_producto(data):
    try:
        id_producto = data.get('id')
        nombre = data.get('nombre')
        cantidad = data.get('cantidad')
        precio = data.get('precio')

        if not id_producto or not nombre or cantidad is None or precio is None:
            emit('error', {'mensaje': 'Faltan campos para modificar el producto.'})
            return

        db.modificar_producto(id_producto, nombre, cantidad, precio)
        productos = db.obtener_productos()

        # Emitir a todos los clientes que el inventario se ha actualizado
        emit('actualizar_inventario', {
            'accion': 'modificar',
            'productos': productos,
            'id_modificado': id_producto,
            'mensaje': f'Producto ID {id_producto} modificado con éxito.'
        }, broadcast=True)

    except Exception as e:
        emit('error', {'mensaje': str(e)})


@socketio.on('eliminar_producto')
def handle_eliminar_producto(data):
    try:
        id_producto = data.get('id')
        if not id_producto:
            emit('error', {'mensaje': 'Falta el ID del producto a eliminar.'})
            return

        db.eliminar_producto(id_producto)
        productos = db.obtener_productos()

        # Emitir a todos los clientes que el inventario se ha actualizado
        emit('actualizar_inventario', {
            'accion': 'eliminar',
            'productos': productos,
            'id_eliminado': id_producto,
            'mensaje': f'Producto ID {id_producto} eliminado con éxito.'
        }, broadcast=True)

    except Exception as e:
        emit('error', {'mensaje': str(e)})


# ==================== RUTAS DE FORMULARIOS Y REDIRECCIÓN ====================

# Ahora estas rutas solo redirigen a la lógica de Socket.IO
@app.route('/producto/crear', methods=['POST'])
def crear_producto_form():
    data = request.form
    nombre = data.get('nombre')
    cantidad = int(data.get('cantidad'))
    precio = float(data.get('precio'))
    socketio.emit('crear_producto', {
        'nombre': nombre,
        'cantidad': cantidad,
        'precio': precio
    })
    return jsonify({'success': True, 'mensaje': f'Petición de creación de "{nombre}" enviada a todos los clientes.'})


@app.route('/producto/modificar/<int:id_producto>', methods=['PUT'])
def modificar_producto_http(id_producto):
    data = request.json
    nombre = data.get('nombre')
    cantidad = int(data.get('cantidad'))
    precio = float(data.get('precio'))
    socketio.emit('modificar_producto', {
        'id': id_producto,
        'nombre': nombre,
        'cantidad': cantidad,
        'precio': precio
    })
    return jsonify({'success': True,
                    'mensaje': f'Petición de modificación del producto ID {id_producto} enviada a todos los clientes.'})


@app.route('/producto/eliminar/<int:id_producto>', methods=['DELETE'])
def eliminar_producto_http(id_producto):
    socketio.emit('eliminar_producto', {'id': id_producto})
    return jsonify({'success': True,
                    'mensaje': f'Petición de eliminación del producto ID {id_producto} enviada a todos los clientes.'})


# ==================== RUTA DE ESTADO/SALUD ====================

@app.route('/status')
def status():
    try:
        productos = db.obtener_productos()
        return jsonify({
            'status': 'El servidor divino está operativo',
            'total_productos': len(productos),
            'mensaje': 'El templo del inventario funciona perfectamente'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'mensaje': str(e)
        }), 500


# ==================== PUNTO DE ENTRADA PRINCIPAL ====================

if __name__ == '__main__':
  
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host="0.0.0.0")
