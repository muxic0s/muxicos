import os
import random
import string
from dotenv import load_dotenv
# AGREGAMOS 'flash' A LOS IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from passlib.hash import pbkdf2_sha256

# Cargamos variables de entorno (.env)
load_dotenv()

app = Flask(__name__, template_folder='.')

# --- CONFIGURACIÓN DE SESIÓN (OBLIGATORIO) ---
app.secret_key = 'clave_super_secreta_muxicos_2025'

# --- CONEXIÓN A BASE DE DATOS ---
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except KeyError:
        return "Error: No se encontró la variable DATABASE_URL."

# --- GENERADOR DE USERNAME RANDOM ---
def generar_username():
    sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"user_{sufijo}"

# --- RUTAS DE VISTAS ---

@app.route('/')
def home():
    # CAMBIO IMPORTANTE: Lógica de Landing Page
    if 'usuario' in session:
        # Si ya inició sesión, le mostramos el Dashboard (index.html)
        datos_usuario = session['usuario']
        return render_template('index.html', usuario=datos_usuario)
    else:
        # Si NO ha iniciado sesión, le mostramos la Bienvenida (bienvenida.html)
        return render_template('bienvenida.html')

@app.route('/login.html')
def login_page():
    if 'usuario' in session:
        return redirect('/perfil')
    return render_template('login.html')

@app.route('/registro.html')
def registro_page():
    if 'usuario' in session:
        return redirect('/perfil')
    return render_template('registro.html')

@app.route('/detalle.html')
def detalle_page():
    return render_template('detalle.html')

@app.route('/exito.html')
def exito_page():
    return render_template('exito.html')

@app.route('/perfil')
def perfil_page():
    if 'usuario' not in session:
        return redirect('/login.html')
    
    datos_usuario = session['usuario']
    return render_template('perfil.html', user=datos_usuario)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# --- LÓGICA DE REGISTRO ---
@app.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    try:
        nombre = request.form['nombre']
        apellido = request.form.get('apellido', '')
        email = request.form['email']
        password_plano = request.form['password'] 
        instrumento = request.form['instrumento']

        username_random = generar_username()
        password_encriptada = pbkdf2_sha256.hash(password_plano)

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''CREATE TABLE IF NOT EXISTS usuarios_v2 
                       (id SERIAL PRIMARY KEY, 
                        username TEXT,
                        nombre TEXT, 
                        apellido TEXT, 
                        email TEXT, 
                        password_hash TEXT, 
                        instrumento TEXT);''')
        
        cur.execute('''INSERT INTO usuarios_v2 (username, nombre, apellido, email, password_hash, instrumento) 
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (username_random, nombre, apellido, email, password_encriptada, instrumento))
        
        conn.commit()
        cur.close()
        conn.close()

        session['usuario'] = {
            'username': username_random,
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'instrumento': instrumento
        }

        return redirect('/exito.html')

    except Exception as e:
        flash(f"Error en el sistema: {e}", "error")
        return redirect('/registro.html')


# --- LÓGICA DE LOGIN (ACTUALIZADA CON FLASH) ---
@app.route('/iniciar-sesion', methods=['POST'])
def iniciar_sesion():
    try:
        email_recibido = request.form['email']
        password_recibido = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT password_hash, nombre, apellido, username, instrumento FROM usuarios_v2 WHERE email = %s', (email_recibido,))
        usuario_bd = cur.fetchone()
        
        cur.close()
        conn.close()

        if usuario_bd:
            hash_guardado = usuario_bd[0]
            
            if pbkdf2_sha256.verify(password_recibido, hash_guardado):
                session['usuario'] = {
                    'nombre': usuario_bd[1],
                    'apellido': usuario_bd[2],
                    'username': usuario_bd[3],
                    'instrumento': usuario_bd[4],
                    'email': email_recibido
                }
                return redirect('/') # Redirigimos a la raíz, que ahora decidirá mostrar el dashboard
            else:
                flash('La contraseña es incorrecta.', 'error')
                return redirect('/login.html')
        else:
            flash('No existe una cuenta con ese correo.', 'error')
            return redirect('/login.html')
            
    except Exception as e:
        flash(f"Error de conexión: {e}", 'error')
        return redirect('/login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)