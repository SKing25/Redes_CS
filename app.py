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
        return render_template('servidor.html', mensaje=f"BRO tu ip no es servidor {ip_servidor}")
    productos = db.obtener_productos()
    return render_template('servidor.html', productos=productos, ip=ip_servidor)


@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    # Verificación de IP para clientes (opcional, puedes comentarlo si no lo necesitas)
    # if ip_cliente not in IPS_PERMITIDAS_CLIENTE:
    #     return f"<h1>Acceso denegado para {ip_cliente}</h1>", 403

    return render_template('cliente.html')


# ==================== RUTAS CRUD PARA PRODUCTOS ====================

# CREAR PRODUCTO - Ruta POST para añadir productos desde formulario
@app.route('/producto/crear', methods=['POST'])
def crear_producto():
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        cantidad = int(request.form.get('cantidad'))
        precio = float(request.form.get('precio'))

        # Validación básica
        if not nombre or cantidad < 0 or precio < 0:
            return jsonify({'error': 'Datos inválidos'}), 400

        # Llamar a la función divina de creación
        db.crear_producto(nombre, cantidad, precio)

        # Obtener lista actualizada de productos
        productos = db.obtener_productos()

        # Emitir actualización a todos los clientes conectados via WebSocket
        socketio.emit('actualizar_inventario', {
            'accion': 'crear',
            'productos': productos,
            'mensaje': f'Producto {nombre} creado exitosamente'
        }, broadcast=True)

        # Si es petición AJAX, devolver JSON
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'mensaje': 'Producto creado exitosamente'})

        # Si no, redirigir según el origen
        origen = request.form.get('origen', 'cliente')
        if origen == 'servidor':
            return redirect(url_for('servidor'))
        return redirect(url_for('cliente'))

    except Exception as e:
        print(f"[ERROR DIVINO] Error creando producto: {e}")
        return jsonify({'error': str(e)}), 500


# ELIMINAR PRODUCTO - Ruta DELETE para eliminar productos
@app.route('/producto/eliminar/<int:id_producto>', methods=['POST', 'DELETE'])
def eliminar_producto(id_producto):
    try:
        # Llamar a la función de eliminación
        db.eliminar_producto(id_producto)

        # Obtener lista actualizada
        productos = db.obtener_productos()

        # Emitir actualización a todos los clientes
        socketio.emit('actualizar_inventario', {
            'accion': 'eliminar',
            'productos': productos,
            'id_eliminado': id_producto,
            'mensaje': f'Producto ID {id_producto} eliminado'
        }, broadcast=True)

        if request.method == 'DELETE' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'mensaje': 'Producto eliminado exitosamente'})

        # Redirigir según origen
        origen = request.args.get('origen', 'cliente')
        if origen == 'servidor':
            return redirect(url_for('servidor'))
        return redirect(url_for('cliente'))

    except Exception as e:
        print(f"[ERROR DIVINO] Error eliminando producto: {e}")
        return jsonify({'error': str(e)}), 500


# MODIFICAR PRODUCTO - Ruta PUT/POST para actualizar productos
@app.route('/producto/modificar/<int:id_producto>', methods=['POST', 'PUT'])
def modificar_producto(id_producto):
    try:
        # Obtener datos del formulario o JSON
        if request.is_json:
            data = request.get_json()
            nombre = data.get('nombre')
            cantidad = int(data.get('cantidad'))
            precio = float(data.get('precio'))
        else:
            nombre = request.form.get('nombre')
            cantidad = int(request.form.get('cantidad'))
            precio = float(request.form.get('precio'))

        # Validación
        if not nombre or cantidad < 0 or precio < 0:
            return jsonify({'error': 'Datos inválidos'}), 400

        # Llamar a la función de modificación
        db.modificar_producto(id_producto, nombre, cantidad, precio)

        # Obtener lista actualizada
        productos = db.obtener_productos()

        # Emitir actualización
        socketio.emit('actualizar_inventario', {
            'accion': 'modificar',
            'productos': productos,
            'id_modificado': id_producto,
            'mensaje': f'Producto ID {id_producto} modificado'
        }, broadcast=True)

        if request.is_json or request.method == 'PUT':
            return jsonify({'success': True, 'mensaje': 'Producto modificado exitosamente'})

        # Redirigir según origen
        origen = request.form.get('origen', 'cliente')
        if origen == 'servidor':
            return redirect(url_for('servidor'))
        return redirect(url_for('cliente'))

    except Exception as e:
        print(f"[ERROR DIVINO] Error modificando producto: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== RUTAS API ADICIONALES ====================

# OBTENER TODOS LOS PRODUCTOS - API REST
@app.route('/api/productos', methods=['GET'])
def api_obtener_productos():
    try:
        productos = db.obtener_productos()
        return jsonify({'success': True, 'productos': productos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# OBTENER UN PRODUCTO ESPECÍFICO
@app.route('/api/producto/<int:id_producto>', methods=['GET'])
def api_obtener_producto(id_producto):
    try:
        productos = db.obtener_productos()
        producto = next((p for p in productos if p[0] == id_producto), None)

        if producto:
            return jsonify({
                'success': True,
                'producto': {
                    'id': producto[0],
                    'nombre': producto[1],
                    'cantidad': producto[2],
                    'precio': producto[3]
                }
            })
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== EVENTOS WEBSOCKET ====================

@socketio.on('connect')
def handle_connect():
    print(f"[CONEXIÓN DIVINA] Cliente conectado: {request.sid}")
    # Enviar inventario actual al cliente que se conecta
    productos = db.obtener_productos()
    emit('inventario_inicial', {'productos': productos})


@socketio.on('disconnect')
def handle_disconnect():
    print(f"[DESCONEXIÓN] Cliente desconectado: {request.sid}")


@socketio.on('solicitar_actualizacion')
def handle_solicitar_actualizacion():
    productos = db.obtener_productos()
    emit('actualizar_inventario', {
        'accion': 'actualización_solicitada',
        'productos': productos
    })


# Evento para crear producto via WebSocket
@socketio.on('crear_producto_ws')
def handle_crear_producto_ws(data):
    try:
        nombre = data.get('nombre')
        cantidad = int(data.get('cantidad'))
        precio = float(data.get('precio'))

        db.crear_producto(nombre, cantidad, precio)
        productos = db.obtener_productos()

        # Emitir a TODOS los clientes
        socketio.emit('actualizar_inventario', {
            'accion': 'crear',
            'productos': productos,
            'mensaje': f'Producto {nombre} creado via WebSocket'
        }, broadcast=True)

    except Exception as e:
        emit('error', {'mensaje': str(e)})


# Evento para eliminar producto via WebSocket
@socketio.on('eliminar_producto_ws')
def handle_eliminar_producto_ws(data):
    try:
        id_producto = int(data.get('id'))

        db.eliminar_producto(id_producto)
        productos = db.obtener_productos()

        socketio.emit('actualizar_inventario', {
            'accion': 'eliminar',
            'productos': productos,
            'id_eliminado': id_producto,
            'mensaje': f'Producto ID {id_producto} eliminado via WebSocket'
        }, broadcast=True)

    except Exception as e:
        emit('error', {'mensaje': str(e)})


# Evento para modificar producto via WebSocket
@socketio.on('modificar_producto_ws')
def handle_modificar_producto_ws(data):
    try:
        id_producto = int(data.get('id'))
        nombre = data.get('nombre')
        cantidad = int(data.get('cantidad'))
        precio = float(data.get('precio'))

        db.modificar_producto(id_producto, nombre, cantidad, precio)
        productos = db.obtener_productos()

        socketio.emit('actualizar_inventario', {
            'accion': 'modificar',
            'productos': productos,
            'id_modificado': id_producto,
            'mensaje': f'Producto ID {id_producto} modificado via WebSocket'
        }, broadcast=True)

    except Exception as e:
        emit('error', {'mensaje': str(e)})


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
    print("\n" + "=" * 50)
    print("🔥 EL SERVIDOR DIVINO DEL INVENTARIO ESTÁ DESPERTANDO 🔥")
    print("=" * 50 + "\n")

    socketio.run(app,
                 debug=True,
                 host='0.0.0.0',
                 port=5000,
                 allow_unsafe_werkzeug=True)