import os
import random
import string
import requests # Para conectar con YouTube (API noembed)
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from passlib.hash import pbkdf2_sha256
from urllib.parse import urlparse, parse_qs

# Cargamos variables de entorno (.env)
load_dotenv()

app = Flask(__name__, template_folder='.')

# --- CONFIGURACIÓN DE SESIÓN ---
app.secret_key = 'clave_super_secreta_muxicos_2025'

# --- DATOS DEL BANNER ---
BANNERS = [
    {"titulo": "Domina el Requinto", "desc": "Descubre las técnicas avanzadas...", "img": "https://images.unsplash.com/photo-1514525253440-b393452e8d26?q=80&w=2800", "tag": "Novedad", "color": "green"},
    {"titulo": "Oferta de Lanzamiento", "desc": "Suscríbete anual y obtén 2 meses gratis...", "img": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?q=80&w=2800", "tag": "Promo", "color": "yellow"},
    {"titulo": "Masterclass de Acordeón", "desc": "Aprende los secretos del estilo norteño...", "img": "https://images.unsplash.com/photo-1627832811394-b2586e376043?q=80&w=2800", "tag": "Exclusivo", "color": "purple"}
]

# --- CONEXIÓN A BASE DE DATOS ---
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except KeyError:
        return "Error: No se encontró la variable DATABASE_URL."

# --- UTILIDADES ---
def generar_username():
    sufijo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"user_{sufijo}"

def obtener_id_video(url):
    if not url: return None
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
    if 'v=' in url: return url.split('v=')[1].split('&')[0]
    return None

# ==========================================
# RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def home():
    if 'usuario' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM cursos ORDER BY id DESC LIMIT 4")
            cursos = cur.fetchall()
        except:
            cursos = []
            conn.rollback()
        cur.close()
        conn.close()
        return render_template('index.html', usuario=session['usuario'], cursos=cursos, banners=BANNERS)
    else:
        return render_template('bienvenida.html')

@app.route('/cursos')
def cursos_page():
    if 'usuario' not in session: return redirect('/login.html')
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM cursos ORDER BY id DESC")
        cursos = cur.fetchall()
    except:
        cursos = []
        conn.rollback()
    cur.close()
    conn.close()
    return render_template('cursos.html', usuario=session['usuario'], cursos=cursos)

@app.route('/curso/<int:id_curso>')
def ver_curso(id_curso):
    if 'usuario' not in session: return redirect('/login.html')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cursos WHERE id = %s", (id_curso,))
    curso = cur.fetchone()
    try:
        cur.execute("SELECT * FROM cursos WHERE id != %s ORDER BY RANDOM() LIMIT 3", (id_curso,))
        sugerencias = cur.fetchall()
    except:
        sugerencias = []
    cur.close()
    conn.close()
    if curso:
        video_id = obtener_id_video(curso[2])
        return render_template('detalle.html', usuario=session['usuario'], curso=curso, video_id=video_id, sugerencias=sugerencias)
    else:
        return "Curso no encontrado", 404

# --- NUEVA RUTA: CONFIGURACIÓN ---
@app.route('/config')
def config_page():
    if 'usuario' not in session: return redirect('/login.html')
    # Renderizamos la vista de configuración pasando el usuario
    return render_template('config.html', user=session['usuario'])

# ==========================================
# GESTIÓN DE PERFIL
# ==========================================

@app.route('/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    if 'usuario' not in session: return redirect('/login.html')
    
    nuevo_nombre = request.form['nombre']
    nuevo_apellido = request.form['apellido']
    nuevo_telefono = request.form['telefono']
    nueva_foto = request.form.get('foto_url', '')
    nuevo_password = request.form['password']
    email_actual = session['usuario']['email']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if nuevo_password:
            pwd_hash = pbkdf2_sha256.hash(nuevo_password)
            cur.execute("""
                UPDATE usuarios_v5 
                SET nombre = %s, apellido = %s, telefono = %s, foto_url = %s, password_hash = %s 
                WHERE email = %s
            """, (nuevo_nombre, nuevo_apellido, nuevo_telefono, nueva_foto, pwd_hash, email_actual))
        else:
            cur.execute("""
                UPDATE usuarios_v5 
                SET nombre = %s, apellido = %s, telefono = %s, foto_url = %s 
                WHERE email = %s
            """, (nuevo_nombre, nuevo_apellido, nuevo_telefono, nueva_foto, email_actual))
        
        conn.commit()
        
        session['usuario']['nombre'] = nuevo_nombre
        session['usuario']['apellido'] = nuevo_apellido
        session['usuario']['telefono'] = nuevo_telefono
        session['usuario']['foto_url'] = nueva_foto
        session.modified = True
        
        flash("Perfil actualizado correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar: {e}", "error")
    finally:
        cur.close()
        conn.close()

    return redirect('/perfil')

@app.route('/eliminar-cuenta', methods=['POST'])
def eliminar_cuenta():
    if 'usuario' not in session: return redirect('/login.html')
    email_actual = session['usuario']['email']
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM usuarios_v5 WHERE email = %s", (email_actual,))
        conn.commit()
        session.clear()
        flash("Cuenta eliminada.", "success")
        return redirect('/')
    except:
        flash("Error al eliminar.", "error")
        return redirect('/perfil')
    finally:
        cur.close()
        conn.close()

# ==========================================
# ADMIN Y AUTH
# ==========================================

@app.route('/admin')
def admin_page():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS cursos (id SERIAL PRIMARY KEY, titulo TEXT, url_video TEXT, url_image TEXT, descripcion TEXT, maestro TEXT);''')
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
        api_url = f"https://noembed.com/embed?url={url_video}"
        response = requests.get(api_url).json()
        if 'error' in response: return redirect('/admin')
        titulo = response.get('title', 'Sin título')
        autor = response.get('author_name', 'Maestro')
        thumbnail = response.get('thumbnail_url', '')
        descripcion = f"Aprende con {autor}."
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO cursos (titulo, url_video, url_image, descripcion, maestro) VALUES (%s, %s, %s, %s, %s)''', (titulo, url_video, thumbnail, descripcion, autor))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/admin')
    except: return redirect('/admin')

@app.route('/login.html')
def login_page(): return render_template('login.html')

@app.route('/registro.html')
def registro_page(): return render_template('registro.html')

@app.route('/detalle.html')
def detalle_page(): return redirect('/')

@app.route('/exito.html')
def exito_page(): return render_template('exito.html')

@app.route('/perfil')
def perfil_page():
    if 'usuario' not in session: return redirect('/login.html')
    return render_template('perfil.html', user=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    try:
        nombre = request.form['nombre']
        apellido = request.form.get('apellido', '')
        email = request.form['email']
        password = request.form['password']
        instrumento = request.form.get('instrumento', 'guitarra')
        username = generar_username()
        pwd_hash = pbkdf2_sha256.hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS usuarios_v5 
                       (id SERIAL PRIMARY KEY, username TEXT, nombre TEXT, apellido TEXT, 
                        email TEXT, password_hash TEXT, instrumento TEXT, telefono TEXT, foto_url TEXT);''')
        cur.execute('''INSERT INTO usuarios_v5 (username, nombre, apellido, email, password_hash, instrumento) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                    (username, nombre, apellido, email, pwd_hash, instrumento, '', ''))
        conn.commit()
        cur.close()
        conn.close()
        session['usuario'] = {'username': username, 'nombre': nombre, 'apellido': apellido, 'email': email, 'instrumento': instrumento, 'telefono': '', 'foto_url': ''}
        return redirect('/exito.html')
    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect('/registro.html')

@app.route('/iniciar-sesion', methods=['POST'])
def iniciar_sesion():
    try:
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password_hash, nombre, apellido, username, instrumento, telefono, foto_url FROM usuarios_v5 WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and pbkdf2_sha256.verify(password, user[0]):
            session['usuario'] = {'nombre': user[1], 'apellido': user[2], 'username': user[3], 'instrumento': user[4], 'email': email, 'telefono': user[5] or '', 'foto_url': user[6] or ''}
            return redirect('/') 
        else:
            flash('Datos incorrectos.', 'error')
            return redirect('/login.html')
    except Exception as e:
        flash(f"Error: {e}", 'error')
        return redirect('/login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)