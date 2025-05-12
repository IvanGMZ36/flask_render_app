from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = '1234'

# Configuración de la base de datos
DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/tienda_db'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Función para conectar a la base de datos
def conectar_db():
    return psycopg2.connect(DATABASE_URL)

# Modelo de usuario
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1])
    return None

# ======================== AUTENTICACIÓN ========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1]))
            flash("Inicio de sesión exitoso.")
            return redirect(url_for('index'))
        flash("Nombre de usuario o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = conectar_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash("Usuario registrado exitosamente.")
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash("Error al registrar usuario.")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión.")
    return redirect(url_for('login'))

# ======================== INICIO ========================

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ======================== PEDIDOS ========================

@app.route('/pedidos_detalles')
@login_required
def vista_pedidos_detalles():
    conn = conectar_db()  # Usar la función de conexión
    cursor = conn.cursor()  # Obtener el cursor de la conexión
    cursor.execute("SELECT * FROM vista_pedidos_detalles")
    datos = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conn.close()  # No olvidar cerrar la conexión
    return render_template('tabla_generica.html', titulo='Detalles de Pedidos', columnas=columnas, datos=datos)


@app.route('/clientes_pedidos')
@login_required
def vista_clientes_con_pedidos():
    conn = conectar_db()  # Usar la función de conexión
    cursor = conn.cursor()  # Obtener el cursor de la conexión
    cursor.execute("SELECT * FROM vista_clientes_con_pedidos")
    datos = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conn.close()  # No olvidar cerrar la conexión
    return render_template('tabla_generica.html', titulo='Clientes con Pedidos', columnas=columnas, datos=datos)


@app.route('/ventas_resumen')
@login_required
def vista_ventas_resumen():
    conn = conectar_db()  # Usar la función de conexión
    cursor = conn.cursor()  # Obtener el cursor de la conexión
    cursor.execute("SELECT * FROM vista_ventas_resumen")
    datos = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conn.close()  # No olvidar cerrar la conexión
    return render_template('tabla_generica.html', titulo='Resumen de Ventas', columnas=columnas, datos=datos)


@app.route('/inventario_actual')
@login_required
def vista_inventario_actual():
    conn = conectar_db()  # Usar la función de conexión
    cursor = conn.cursor()  # Obtener el cursor de la conexión
    cursor.execute("SELECT * FROM vista_inventario_actual")
    datos = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conn.close()  # No olvidar cerrar la conexión
    return render_template('tabla_generica.html', titulo='Inventario Actual', columnas=columnas, datos=datos)

# ======================== PRODUCTOS ========================

# Ruta para crear un nuevo producto
@app.route('/nuevo_producto', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio_unitario = request.form['precio_unitario']

        conn = conectar_db()
        cursor = conn.cursor()
        try:
            cursor.execute(""" 
                INSERT INTO productos (nombre, descripcion, precio_unitario) 
                VALUES (%s, %s, %s)
            """, (nombre, descripcion, precio_unitario))
            conn.commit()
            flash("Producto creado exitosamente.")
            return redirect(url_for('vista_productos_completos'))
        except Exception as e:
            conn.rollback()
            flash("Error al crear el producto. Intenta nuevamente.")
        finally:
            conn.close()

    return render_template('nuevo_producto.html')  # Crear esta plantilla si es necesario


@app.route('/productos_completos')
@login_required
def vista_productos_completos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")  # Obtener los productos completos
    productos = cursor.fetchall()
    conn.close()
    return render_template("vista_productos_completos.html", productos=productos)

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    conn = conectar_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio_unitario = request.form['precio_unitario']
        cursor.execute("""
            UPDATE productos
            SET nombre = %s, descripcion = %s, precio_unitario = %s
            WHERE id = %s
        """, (nombre, descripcion, precio_unitario, id))
        conn.commit()
        conn.close()
        flash("Producto actualizado correctamente.")
        return redirect(url_for('vista_productos_completos'))

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    conn.close()
    return render_template("editar_producto.html", producto=producto)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conn.commit()
        flash("Producto eliminado correctamente.")
    except Exception:
        conn.rollback()
        flash("No se pudo eliminar el producto.")
    finally:
        conn.close()
    return redirect(url_for('vista_productos_completos'))

# ======================== EJECUCIÓN ========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
