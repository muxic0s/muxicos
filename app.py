import os
import random
import string
import requests # Para conectar con YouTube (API noembed)
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from passlib.hash import pbkdf2_sha256

# Cargamos variables de entorno (.env)
load_dotenv()

app = Flask(__name__, template_folder='.')

# --- CONFIGURACIÓN DE SESIÓN ---
app.secret_key = 'clave_super_secreta_muxicos_2025'

# --- DATOS DEL BANNER (Ofertas y Noticias) ---
BANNERS = [
    {
        "titulo": "Domina el Requinto",
        "desc": "Descubre las técnicas avanzadas para destacar en cualquier agrupación.",
        "img": "https://images.unsplash.com/photo-1514525253440-b393452e8d26?q=80&w=2800",
        "tag": "Novedad",
        "color": "green"
    },
    {
        "titulo": "Oferta de Lanzamiento",
        "desc": "Suscríbete anual y obtén 2 meses gratis de mentoría personalizada.",
        "img": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?q=80&w=2800",
        "tag": "Promo",
        "color": "yellow"
    },
    {
        "titulo": "Masterclass de Acordeón",
        "desc": "Aprende los secretos del estilo norteño con el legendario Ramón Ayala (Invitado).",
        "img": "https://images.unsplash.com/photo-1627832811394-b2586e376043?q=80&w=2800",
        "tag": "Exclusivo",
        "color": "purple"
    }
]

# --- CONEXIÓN A BASE DE DATOS ---
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except KeyError:
        return "Error: No se encontró la variable DATABASE_URL."

# --- GENERADOR DE USERNAME ---
def generar_username():
    sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"user_{sufijo}"

# --- HELPER: EXTRAER ID DE YOUTUBE (NUEVO) ---
def obtener_id_video(url):
    """
    Convierte 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' 
    en simplemente 'dQw4w9WgXcQ' para que el iframe funcione.
    """
    if not url: return None
    if 'youtu.be' in url:
        return url.split('/')[-1]
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return None

# ==========================================
# RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def home():
    # Lógica del Home (Dashboard)
    if 'usuario' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Traemos SOLO los 4 cursos más recientes para el Home
            cur.execute("SELECT * FROM cursos ORDER BY id DESC LIMIT 4")
            cursos_recientes = cur.fetchall()
        except:
            cursos_recientes = []
            conn.rollback()
            
        cur.close()
        conn.close()
        
        # Renderizamos index.html pasando cursos y banners
        return render_template('index.html', 
                             usuario=session['usuario'], 
                             cursos=cursos_recientes, 
                             banners=BANNERS)
    else:
        # Si no hay usuario, mostramos la Bienvenida
        return render_template('bienvenida.html')

@app.route('/cursos')
def cursos_page():
    # Catálogo completo con buscador
    if 'usuario' not in session: return redirect('/login.html')
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Aquí traemos TODOS los cursos
        cur.execute("SELECT * FROM cursos ORDER BY id DESC")
        todos_los_cursos = cur.fetchall()
    except:
        todos_los_cursos = []
        conn.rollback()
    cur.close()
    conn.close()
    
    return render_template('cursos.html', 
                         usuario=session['usuario'], 
                         cursos=todos_los_cursos)

# --- RUTA PARA VER EL VIDEO (NUEVO) ---
@app.route('/curso/<int:id_curso>')
def ver_curso(id_curso):
    if 'usuario' not in session: return redirect('/login.html')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Buscamos el curso específico por ID
    cur.execute("SELECT * FROM cursos WHERE id = %s", (id_curso,))
    curso = cur.fetchone()
    
    # 2. Buscamos 3 sugerencias aleatorias (que no sean el mismo curso)
    try:
        cur.execute("SELECT * FROM cursos WHERE id != %s ORDER BY RANDOM() LIMIT 3", (id_curso,))
        sugerencias = cur.fetchall()
    except:
        sugerencias = []

    cur.close()
    conn.close()
    
    if curso:
        # Limpiamos el ID de YouTube para pasarlo al HTML
        video_id = obtener_id_video(curso[2]) # La columna 2 es la URL
        
        return render_template('detalle.html', 
                             usuario=session['usuario'], 
                             curso=curso, 
                             video_id=video_id,
                             sugerencias=sugerencias)
    else:
        return "Curso no encontrado", 404

# ==========================================
# PANEL DE ADMINISTRACIÓN
# ==========================================

@app.route('/admin')
def admin_page():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Creamos tabla cursos si no existe
    cur.execute('''CREATE TABLE IF NOT EXISTS cursos 
                   (id SERIAL PRIMARY KEY, 
                    titulo TEXT, 
                    url_video TEXT, 
                    url_image TEXT, 
                    descripcion TEXT, 
                    maestro TEXT);''')
    conn.commit()
    
    cur.execute("SELECT * FROM cursos ORDER BY id DESC")
    cursos = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin.html', cursos=cursos)

@app.route('/admin/agregar', methods=['POST'])
def agregar_curso():
    url_video = request.form['url_video']
    
    try:
        # Importación automática desde YouTube
        api_url = f"https://noembed.com/embed?url={url_video}"
        response = requests.get(api_url).json()
        
        if 'error' in response:
            flash("Error: Link no válido.", "error")
            return redirect('/admin')

        titulo = response.get('title', 'Curso sin título')
        autor = response.get('author_name', 'Muxicos Maestro')
        thumbnail = response.get('thumbnail_url', '')
        descripcion = f"Aprende con este increíble contenido de {autor}."

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''INSERT INTO cursos (titulo, url_video, url_image, descripcion, maestro) 
                       VALUES (%s, %s, %s, %s, %s)''',
                    (titulo, url_video, thumbnail, descripcion, autor))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash(f"¡Agregado: {titulo}!", "success")
        return redirect('/admin')

    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect('/admin')

# ==========================================
# RUTAS DE NAVEGACIÓN
# ==========================================

@app.route('/login.html')
def login_page():
    if 'usuario' in session: return redirect('/perfil')
    return render_template('login.html')

@app.route('/registro.html')
def registro_page():
    if 'usuario' in session: return redirect('/perfil')
    return render_template('registro.html')

@app.route('/detalle.html')
def detalle_page():
    # Redirección por seguridad si intentan entrar directo sin ID
    return redirect('/')

@app.route('/exito.html')
def exito_page():
    return render_template('exito.html')

@app.route('/perfil')
def perfil_page():
    if 'usuario' not in session: return redirect('/login.html')
    return render_template('perfil.html', user=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==========================================
# LÓGICA DE USUARIOS (AUTH)
# ==========================================

@app.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    try:
        nombre = request.form['nombre']
        apellido = request.form.get('apellido', '')
        email = request.form['email']
        password_plano = request.form['password'] 
        instrumento = request.form.get('instrumento', 'guitarra')

        username_random = generar_username()
        password_encriptada = pbkdf2_sha256.hash(password_plano)

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''CREATE TABLE IF NOT EXISTS usuarios_v2 
                       (id SERIAL PRIMARY KEY, username TEXT, nombre TEXT, apellido TEXT, email TEXT, password_hash TEXT, instrumento TEXT);''')
        
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
        flash(f"Error: {e}", "error")
        return redirect('/registro.html')

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
            if pbkdf2_sha256.verify(password_recibido, usuario_bd[0]):
                session['usuario'] = {
                    'nombre': usuario_bd[1],
                    'apellido': usuario_bd[2],
                    'username': usuario_bd[3],
                    'instrumento': usuario_bd[4],
                    'email': email_recibido
                }
                return redirect('/') 
            else:
                flash('Contraseña incorrecta.', 'error')
                return redirect('/login.html')
        else:
            flash('Usuario no encontrado.', 'error')
            return redirect('/login.html')
            
    except Exception as e:
        flash(f"Error: {e}", 'error')
        return redirect('/login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)