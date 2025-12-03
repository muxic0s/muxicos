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

app = Flask(__name__) # Corrección: Ya no usamos template_folder='.' porque tienes la carpeta templates/
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
    usuario = session.get('usuario')
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
    return render_template('index.html', usuario=usuario, cursos=cursos, banners=BANNERS)

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

# ==========================================
# GESTIÓN DE PERFIL (AQUÍ ESTABA EL ERROR)
# ==========================================

@app.route('/perfil')
def perfil_page():
    if 'usuario' not in session: return redirect('/login.html')
    # CORRECCIÓN IMPORTANTE: Cambiamos 'user' por 'usuario'
    return render_template('perfil.html', usuario=session['usuario'])

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
    if 'usuario' not in session: return redirect('/login.html')
    rol_actual = session['usuario'].get('rol', 'user')
    
    if rol_actual != 'admin':
        flash("⚠️ Acceso Denegado: Se requieren permisos de administrador.", "error")
        return redirect('/perfil')

    conn = get_db_connection()
    cur = conn.cursor()
    # Nos aseguramos que la tabla cursos exista
    cur.execute('''CREATE TABLE IF NOT EXISTS cursos (id SERIAL PRIMARY KEY, titulo TEXT, url_video TEXT, url_image TEXT, descripcion TEXT, maestro TEXT);''')
    conn.commit()
    cur.execute("SELECT * FROM cursos ORDER BY id DESC")
    cursos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', usuario=session['usuario'], cursos=cursos)

@app.route('/admin/agregar', methods=['POST'])
def agregar_curso():
    if 'usuario' not in session or session['usuario'].get('rol') != 'admin':
        return redirect('/')

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
        flash("Curso agregado exitosamente.", "success")
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/config')
def config_page():
    if 'usuario' not in session: return redirect('/login.html')
    return render_template('config.html', usuario=session['usuario'])

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
        
        # INSERT coincidiendo con tu CSV: rol incluido
        cur.execute('''INSERT INTO usuarios_v5 (username, nombre, apellido, email, password_hash, instrumento, telefono, foto_url, rol) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'user')''', 
                    (username, nombre, apellido, email, pwd_hash, instrumento, '', ''))
        
        conn.commit()
        cur.close()
        conn.close()
        session['usuario'] = {
            'username': username, 
            'nombre': nombre, 
            'apellido': apellido, 
            'email': email, 
            'instrumento': instrumento, 
            'telefono': '', 
            'foto_url': '',
            'rol': 'user'
        }
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
        # SELECT explícito para mapear los datos correctamente
        cur.execute('SELECT password_hash, nombre, apellido, username, instrumento, telefono, foto_url, rol FROM usuarios_v5 WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and pbkdf2_sha256.verify(password, user[0]):
            session['usuario'] = {
                'nombre': user[1], 
                'apellido': user[2], 
                'username': user[3], 
                'instrumento': user[4], 
                'email': email, 
                'telefono': user[5] or '', 
                'foto_url': user[6] or '',
                'rol': user[7] or 'user' # El rol está en la posición 7 de nuestro SELECT
            }
            return redirect('/') 
        else:
            flash('Datos incorrectos.', 'error')
            return redirect('/login.html')
    except Exception as e:
        flash(f"Error: {e}", 'error')
        return redirect('/login.html')

# Herramienta Secreta para Admin (Temporal)
@app.route('/secret-setup-angel')
def setup_admin():
    if 'usuario' not in session: return "Primero inicia sesión."
    email_actual = session['usuario']['email']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios_v5 SET rol = 'admin' WHERE email = %s", (email_actual,))
    conn.commit()
    cur.close()
    conn.close()
    session['usuario']['rol'] = 'admin'
    session.modified = True
    return f"¡Listo! Usuario {email_actual} ahora es ADMIN."

if __name__ == '__main__':
    # Modo debug activado para ver errores en consola si algo falla
    app.run(host='0.0.0.0', port=8000, debug=True)