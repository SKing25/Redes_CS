# Aplicacion para un servicio de inventarios para un comercio

La aplicacion debe tener: 
- 1 servidor (maquina 1)
- 2 clientes (maquina 2 y maquina 3)

## Servidor (Maquina 1)

En la maquina 1 se debe vizualizar el inventario, el inventario se maneja con una base de datos (tal vez sqlite), donde cada producto debe tener:
- ID (llave)
- Nombre
- Cantidad
- Precio

## Clientes (Maquina 2 y 3)

En las otras 2 maquinas se debe usar un formulario para añadir productos a la base de datos:
- ID
- Nombre 
- Cantida
- Precio

---

### Notas:
- Se debe usar socket para las peticiones
- El servidor debe ser capaz de manejar multiples peticiones (clientes)
- Se usa un switch para conectar las 3 maquinas
- Primero intentar correrlo en local y luego si usando un hoster (Render)
- HTML y CSS pal front y flask pal back

---

## NS3

Simular todo en NS3 (obviamente sin la base de datos ni el formulario)
