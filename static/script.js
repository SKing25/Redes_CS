// ================================
// MÓDULO: ThemeManager 
// ================================
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.body = document.body;
        this.init();
    }
    
    init() {
        if (!this.themeToggle) return;
        
        const savedTheme = this.getSavedTheme() || 'light';
        this.applyTheme(savedTheme);
        
        this.themeToggle.addEventListener('change', () => this.toggleTheme());
    }
    
    getSavedTheme() {
        try {
            return localStorage.getItem('theme') || this.getCookieTheme() || window.currentTheme || 'light';
        } catch (e) {
            return this.getCookieTheme() || window.currentTheme || 'light';
        }
    }
    
    saveTheme(theme) {
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.warn('localStorage no disponible, usando cookies');
            this.setCookieTheme(theme);
        }
        window.currentTheme = theme;
    }
    
    applyTheme(theme) {
        // Aplicar clase al body (para que coincida con el CSS)
        if (theme === 'dark') {
            this.body.classList.add('dark-mode');
            this.themeToggle.checked = true;
        } else {
            this.body.classList.remove('dark-mode');
            this.themeToggle.checked = false;
        }
        
        this.saveTheme(theme);
    }

    toggleTheme() {
        const isDark = this.themeToggle.checked;
        const newTheme = isDark ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }
    
    setCookieTheme(theme) {
        document.cookie = `theme=${theme};path=/;max-age=${60 * 60 * 24 * 365}`;
    }
    
    getCookieTheme() {
        const name = 'theme=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) === 0) {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }
}

// ================================
// MÓDULO: PageSelector
// ================================
class PageSelector {
    constructor() {
        this.pageItems = document.querySelectorAll('.page-item');
        this.init();
    }

    init() {
        const currentPage = window.location.pathname.split('/').pop();
        this.pageItems.forEach(item => {
            const dataPage = item.getAttribute('data-page') + '.html';
            if (dataPage === currentPage) {
                item.classList.add('active');
            }
        });
    }
}

// ================================
// MÓDULO: NotificationManager (Compartido)
// ================================
class NotificationManager {
    static mostrarNotificacion(mensaje, tipo) {
        const notificacion = document.createElement('div');
        notificacion.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 2000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;

        if (tipo === 'success') {
            notificacion.style.background = 'linear-gradient(45deg, #27ae60, #2ecc71)';
        } else {
            notificacion.style.background = 'linear-gradient(45deg, #e74c3c, #c0392b)';
        }

        notificacion.textContent = mensaje;
        document.body.appendChild(notificacion);

        setTimeout(() => {
            notificacion.remove();
        }, 4000);
    }

    static initAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from { 
                    transform: translateX(0); 
                    opacity: 1; 
                }
                to { 
                    transform: translateX(100%); 
                    opacity: 0; 
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// ================================
// MÓDULO: InventoryAdmin (Para administrador)
// ================================
class InventoryAdmin {
    constructor() {
        this.socket = null;
        this.productoEditandoId = null;
        this.init();
    }

    init() {
        this.initSocket();
        this.initEventListeners();
        console.log('🔧 Módulo Admin inicializado');
    }

    initSocket() {
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('🔥 Admin conectado al servidor');
            this.updateStatusIndicator('🟢 En Línea');
        });

        this.socket.on('disconnect', () => {
            console.log('💔 Admin desconectado del servidor');
            this.updateStatusIndicator('🔴 Desconectado');
        });

        this.socket.on('actualizar_inventario', (data) => {
            console.log('📦 Admin actualizando inventario:', data);
            this.renderProductosAdmin(data.productos);

            if (data.mensaje) {
                NotificationManager.mostrarNotificacion(data.mensaje, 'success');
            }
        });

        this.socket.on('inventario_inicial', (data) => {
            console.log('📋 Admin inventario inicial recibido');
            this.renderProductosAdmin(data.productos);
        });

        this.socket.on('error', (data) => {
            NotificationManager.mostrarNotificacion(data.mensaje, 'error');
        });
    }

    updateStatusIndicator(status) {
        const indicator = document.getElementById('statusIndicator');
        if (indicator) indicator.innerHTML = status;
    }

    renderProductosAdmin(productos) {
        const container = document.getElementById('productosContainer');
        if (!container) return;

        if (!productos || productos.length === 0) {
            container.innerHTML = `
                <div class="no-products">
                    <h3>🏺 El inventario está vacío</h3>
                    <p>Añade el primer producto</p>
                </div>
            `;
            return;
        }

        container.innerHTML = productos.map(producto => `
            <div class="product-card" data-id="${producto.id}">
                <div class="product-header">
                    <span class="product-name">${producto.nombre}</span>
                    <span class="product-id">ID: ${producto.id}</span>
                </div>

                <div class="product-details">
                    <div class="detail-item">
                        <div class="detail-label">Cantidad</div>
                        <div class="detail-value">${producto.cantidad}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Precio</div>
                        <div class="detail-value">$${parseFloat(producto.precio).toFixed(2)}</div>
                    </div>
                </div>

                <div class="product-actions">
                    <button class="action-btn edit-btn" data-edit-id="${producto.id}" 
                            data-edit-nombre="${producto.nombre}" 
                            data-edit-cantidad="${producto.cantidad}" 
                            data-edit-precio="${producto.precio}">
                        ✏️ Editar
                    </button>
                    <button class="action-btn delete-btn" data-delete-id="${producto.id}">
                        🗑️ Eliminar
                    </button>
                </div>
            </div>
        `).join('');

        this.attachProductActionListeners();
        this.animateCards();
    }

    attachProductActionListeners() {
        // Event listeners para botones de editar
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-edit-id');
                const nombre = e.target.getAttribute('data-edit-nombre');
                const cantidad = e.target.getAttribute('data-edit-cantidad');
                const precio = e.target.getAttribute('data-edit-precio');
                this.editarProducto(id, nombre, cantidad, precio);
            });
        });

        // Event listeners para botones de eliminar
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-delete-id');
                this.eliminarProducto(id);
            });
        });
    }

    editarProducto(id, nombre, cantidad, precio) {
        this.productoEditandoId = id;
        const editNombre = document.getElementById('editNombre');
        const editCantidad = document.getElementById('editCantidad');
        const editPrecio = document.getElementById('editPrecio');
        const modalEditar = document.getElementById('modalEditar');

        if (editNombre) editNombre.value = nombre;
        if (editCantidad) editCantidad.value = cantidad;
        if (editPrecio) editPrecio.value = precio;
        if (modalEditar) modalEditar.style.display = 'flex';
    }

    cerrarModal() {
        const modalEditar = document.getElementById('modalEditar');
        if (modalEditar) modalEditar.style.display = 'none';
        this.productoEditandoId = null;
    }

    eliminarProducto(id) {
        if (confirm(`¿Estás seguro de eliminar el producto ID ${id}? Esta acción no se puede deshacer.`)) {
            this.socket.emit('eliminar_producto', { id: parseInt(id) });
        }
    }

    animateCards() {
        const cards = document.querySelectorAll('.product-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    initEventListeners() {
        // Formulario crear producto
        const formCrear = document.getElementById('formCrearProducto');
        if (formCrear) {
            formCrear.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                this.socket.emit('crear_producto', {
                    nombre: formData.get('nombre'),
                    cantidad: parseInt(formData.get('cantidad')),
                    precio: parseFloat(formData.get('precio'))
                });
                e.target.reset();
            });
        }

        // Formulario editar producto
        const formEditar = document.getElementById('formEditarProducto');
        if (formEditar) {
            formEditar.addEventListener('submit', (e) => {
                e.preventDefault();
                if (!this.productoEditandoId) return;

                const formData = new FormData(e.target);
                this.socket.emit('modificar_producto', {
                    id: parseInt(this.productoEditandoId),
                    nombre: formData.get('nombre'),
                    cantidad: parseInt(formData.get('cantidad')),
                    precio: parseFloat(formData.get('precio'))
                });
                this.cerrarModal();
            });
        }

        // Cerrar modal con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.cerrarModal();
            }
        });

        // Botón cerrar modal (si existe)
        const btnCerrarModal = document.querySelector('.close-modal, .cancel-btn');
        if (btnCerrarModal) {
            btnCerrarModal.addEventListener('click', () => this.cerrarModal());
        }
    }
}

// ================================
// MÓDULO: InventoryClient (Para cliente/visualización)
// ================================
class InventoryClient {
    constructor() {
        this.socket = null;
        this.productos = [];
        this.init();
    }

    init() {
        this.initSocket();
        this.initEventListeners();
        console.log('👁️ Módulo Cliente inicializado');
    }

    initSocket() {
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('🔥 Cliente conectado al servidor');
            this.updateStatusIndicator('🟢 En Línea');
        });

        this.socket.on('disconnect', () => {
            console.log('💔 Cliente desconectado del servidor');
            this.updateStatusIndicator('🔴 Desconectado');
        });

        this.socket.on('actualizar_inventario', (data) => {
            console.log('📦 Cliente actualizando inventario:', data);
            this.productos = data.productos;
            this.renderProductosCliente();

            if (data.mensaje) {
                NotificationManager.mostrarNotificacion(data.mensaje, 'success');
            }
        });

        this.socket.on('inventario_inicial', (data) => {
            console.log('📋 Cliente inventario inicial recibido');
            this.productos = data.productos;
            this.renderProductosCliente();
        });

        this.socket.on('error', (data) => {
            NotificationManager.mostrarNotificacion(data.mensaje, 'error');
        });
    }

    updateStatusIndicator(status) {
        const indicator = document.getElementById('statusIndicator');
        if (indicator) indicator.innerHTML = status;
    }

    renderProductosCliente() {
        const container = document.getElementById('productosContainer');
        if (!container) return;

        if (!this.productos || this.productos.length === 0) {
            container.innerHTML = `
                <div class="no-products">
                    <h3>🏺 El inventario está vacío</h3>
                    <p>Añade el primer producto</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.productos.map(producto => `
            <div class="product-card" data-id="${producto.id}">
                <div class="product-header">
                    <span class="product-name">${producto.nombre}</span>
                    <span class="product-id">ID: ${producto.id}</span>
                </div>

                <div class="product-details">
                    <div class="detail-item">
                        <div class="detail-label">Cantidad</div>
                        <div class="detail-value">${producto.cantidad}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Precio</div>
                        <div class="detail-value">$${parseFloat(producto.precio).toFixed(2)}</div>
                    </div>
                </div>

                <div class="product-status">
                    <span class="status-badge ${producto.cantidad > 0 ? 'in-stock' : 'out-of-stock'}">
                        ${producto.cantidad > 0 ? '✅ Disponible' : '❌ Agotado'}
                    </span>
                </div>
            </div>
        `).join('');

        this.animateCards();
    }

    animateCards() {
        const cards = document.querySelectorAll('.product-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    initEventListeners() {
        // Formulario crear producto (solo si existe en vista cliente)
        const formCrear = document.getElementById('formCrearProducto');
        if (formCrear) {
            formCrear.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                this.socket.emit('crear_producto', {
                    nombre: formData.get('nombre'),
                    cantidad: parseInt(formData.get('cantidad')),
                    precio: parseFloat(formData.get('precio'))
                });
                e.target.reset();
            });
        }
    }
}

// ================================
// INICIALIZACIÓN
// ================================
window.addEventListener('load', () => {
    // Inicializar módulos comunes
    new ThemeManager();
    new PageSelector();
    NotificationManager.initAnimationStyles();
    
    // Determinar qué módulo de inventario inicializar basado en la página
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('admin') || currentPage.includes('servidor') || 
        document.getElementById('modalEditar') || document.querySelector('.edit-btn')) {
        // Página de administrador
        window.inventoryManager = new InventoryAdmin();
        console.log('🔧 Modo Administrador activado');
    } else if (document.getElementById('productosContainer')) {
        // Página de cliente
        window.inventoryManager = new InventoryClient();
        console.log('👁️ Modo Cliente activado');
    }
});