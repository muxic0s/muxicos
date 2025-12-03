import os
import random
import string
import requests
import yt_dlp
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from passlib.hash import pbkdf2_sha256
from urllib.parse import urlparse, parse_qs

# Cargamos variables de entorno (.env)
load_dotenv()

app = Flask(__name__) 
app.secret_key = 'clave_super_secreta_muxicos_2025'

# ... (MANTÉN TU BLOQUE DE BANNERS Y CONEXIÓN DB IGUAL) ...
BANNERS = [
    {"titulo": "Domina el Requinto", "desc": "Descubre las técnicas avanzadas...", "img": "https://images.unsplash.com/photo-1514525253440-b393452e8d26?q=80&w=2800", "tag": "Novedad", "color": "green"},
    {"titulo": "Oferta de Lanzamiento", "desc": "Suscríbete anual y obtén 2 meses gratis...", "img": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?q=80&w=2800", "tag": "Promo", "color": "yellow"},
    {"titulo": "Masterclass de Acordeón", "desc": "Aprende los secretos del estilo norteño...", "img": "https://images.unsplash.com/photo-1627832811394-b2586e376043?q=80&w=2800", "tag": "Exclusivo", "color": "purple"}
]

def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except KeyError:
        return "Error: No se encontró la variable DATABASE_URL."

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

# ... (RUTAS HOME, CURSOS, VER_CURSO, PERFIL SE MANTIENEN IGUAL) ...
# (Pega aquí tus rutas existentes de home, cursos, ver_curso, toggle-favorito, biblioteca, perfil, etc.)
# SOLO VOY A PONER LA FUNCIÓN QUE CAMBIA DRASTICAMENTE: agregar_curso

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
    
    es_favorito = False
    try:
        email_usuario = session['usuario']['email']
        cur.execute("SELECT 1 FROM favoritos WHERE email_usuario = %s AND curso_id = %s", (email_usuario, id_curso))
        if cur.fetchone(): es_favorito = True
    except: pass

    cur.close()
    conn.close()
    if curso:
        video_id = obtener_id_video(curso[2])
        return render_template('detalle.html', usuario=session['usuario'], curso=curso, video_id=video_id, sugerencias=sugerencias, es_favorito=es_favorito)
    else:
        return "Curso no encontrado", 404

@app.route('/toggle-favorito', methods=['POST'])
def toggle_favorito():
    if 'usuario' not in session: return {"error": "No autorizado"}, 401
    data = request.get_json()
    curso_id = data.get('curso_id')
    email_usuario = session['usuario']['email']
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM favoritos WHERE email_usuario = %s AND curso_id = %s", (email_usuario, curso_id))
        if cur.fetchone():
            cur.execute("DELETE FROM favoritos WHERE email_usuario = %s AND curso_id = %s", (email_usuario, curso_id))
            action = "removed"
        else:
            cur.execute("INSERT INTO favoritos (email_usuario, curso_id) VALUES (%s, %s)", (email_usuario, curso_id))
            action = "added"
        conn.commit()
        return {"status": "success", "action": action}
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        cur.close()
        conn.close()

@app.route('/biblioteca')
def biblioteca_page():
    if 'usuario' not in session: return redirect('/login.html')
    email_usuario = session['usuario']['email']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT c.id, c.titulo, c.url_video, c.url_image, c.descripcion, c.maestro 
                   FROM favoritos f JOIN cursos c ON f.curso_id = c.id WHERE f.email_usuario = %s ORDER BY f.id DESC""", (email_usuario,))
    favoritos = cur.fetchall()
    cur.execute("SELECT id, nombre, descripcion, portada_url FROM listas WHERE email_usuario = %s", (email_usuario,))
    raw_listas = cur.fetchall()
    listas = [{'id': l[0], 'nombre': l[1], 'desc': l[2], 'portada': l[3], 'items_count': 0} for l in raw_listas]
    cur.close()
    conn.close()
    return render_template('biblioteca.html', usuario=session['usuario'], favoritos=favoritos, listas=listas)

# ... (RUTAS PERFIL, LOGIN, REGISTRO, ETC. IGUALES) ...
@app.route('/perfil')
def perfil_page():
    if 'usuario' not in session: return redirect('/login.html')
    return render_template('perfil.html', usuario=session['usuario'])

@app.route('/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    if 'usuario' not in session: return redirect('/login.html')
    # ... (Tu código actual de actualizar perfil) ...
    # (Resumido para brevedad, usa el que ya tenías)
    nuevo_nombre = request.form['nombre']
    nuevo_apellido = request.form['apellido']
    nuevo_telefono = request.form['telefono']
    nueva_foto = request.form.get('foto_url', '')
    email_actual = session['usuario']['email']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios_v5 SET nombre=%s, apellido=%s, telefono=%s, foto_url=%s WHERE email=%s", (nuevo_nombre, nuevo_apellido, nuevo_telefono, nueva_foto, email_actual))
    conn.commit()
    session['usuario'].update({'nombre': nuevo_nombre, 'apellido': nuevo_apellido, 'telefono': nuevo_telefono, 'foto_url': nueva_foto})
    session.modified = True
    cur.close()
    conn.close()
    return redirect('/perfil')

@app.route('/eliminar-cuenta', methods=['POST'])
def eliminar_cuenta():
    # ... (Tu código actual) ...
    if 'usuario' not in session: return redirect('/login.html')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios_v5 WHERE email = %s", (session['usuario']['email'],))
    conn.commit()
    session.clear()
    return redirect('/')

@app.route('/login.html')
def login_page(): return render_template('login.html')
@app.route('/registro.html')
def registro_page(): return render_template('registro.html')
@app.route('/detalle.html')
def detalle_page(): return redirect('/')
@app.route('/exito.html')
def exito_page(): return render_template('exito.html')
@app.route('/logout')
def logout(): session.clear(); return redirect('/')
@app.route('/config')
def config_page(): 
    if 'usuario' not in session: return redirect('/login.html')
    return render_template('config.html', usuario=session['usuario'])

@app.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    # ... (Usa tu código actual, está bien) ...
    try:
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        pwd_hash = pbkdf2_sha256.hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios_v5 (username, nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s, 'user')", (generar_username(), nombre, email, pwd_hash))
        conn.commit()
        cur.close()
        conn.close()
        session['usuario'] = {'nombre': nombre, 'email': email, 'rol': 'user', 'foto_url': ''}
        return redirect('/exito.html')
    except: return redirect('/registro.html')

@app.route('/iniciar-sesion', methods=['POST'])
def iniciar_sesion():
    # ... (Usa tu código actual) ...
    email = request.form['email']
    password = request.form['password']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT password_hash, nombre, apellido, username, instrumento, telefono, foto_url, rol FROM usuarios_v5 WHERE email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and pbkdf2_sha256.verify(password, user[0]):
        session['usuario'] = {'nombre': user[1], 'apellido': user[2], 'username': user[3], 'instrumento': user[4], 'email': email, 'telefono': user[5], 'foto_url': user[6], 'rol': user[7]}
        return redirect('/')
    return redirect('/login.html')

@app.route('/admin')
def admin_page():
    if 'usuario' not in session or session['usuario'].get('rol') != 'admin': return redirect('/perfil')
    conn = get_db_connection()
    cur = conn.cursor()
    # Migración silenciosa
    try: cur.execute("ALTER TABLE cursos ADD COLUMN foto_maestro TEXT")
    except: conn.rollback()
    
    cur.execute("SELECT * FROM cursos ORDER BY id DESC")
    cursos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', usuario=session['usuario'], cursos=cursos)

# ==========================================
# IMPORTADOR BLINDADO (YT-DLP + FALLBACK)
# ==========================================
@app.route('/admin/agregar', methods=['POST'])
def agregar_curso():
    if 'usuario' not in session or session['usuario'].get('rol') != 'admin':
        return redirect('/')

    url_video = request.form['url_video']
    
    # 1. Configuración de YT-DLP (Intento Principal)
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'ignoreerrors': True, # No crashear si hay error leve
        # Truco para evadir bloqueos: simular cliente Android
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    # Si subiste el archivo cookies.txt, lo usamos
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    titulo = "Video Importado"
    autor = "Muxicos"
    thumbnail = ""
    descripcion_final = "Descripción no disponible."
    foto_maestro = ""
    tags_originales = ""

    try:
        # INTENTO CON YT-DLP
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_video, download=False)
            
            if info:
                titulo = info.get('title', titulo)
                autor = info.get('uploader', autor)
                thumbnail = info.get('thumbnail', thumbnail)
                desc_yt = info.get('description', '')
                tags_originales = " ".join(info.get('tags', []))
                
                # Auto-Tagging
                texto = (titulo + " " + tags_originales).lower()
                mis_tags = []
                if 'requinto' in texto or 'docerola' in texto: mis_tags.append('requinto guitarra docerola')
                if 'tumbado' in texto or 'natanael' in texto: mis_tags.append('tumbados corridos')
                if 'acordeon' in texto: mis_tags.append('acordeon')
                if 'tololoche' in texto: mis_tags.append('tololoche')
                
                descripcion_final = desc_yt + "\n\n [SYSTEM_TAGS]: " + " ".join(mis_tags)
                
                flash(f"Éxito: Datos extraídos con YT-DLP.", "success")
            else:
                raise Exception("YT-DLP no retornó datos")

    except Exception as e:
        print(f"⚠️ YT-DLP falló: {e}")
        # FALLBACK: INTENTO CON NOEMBED (Método antiguo y seguro)
        try:
            api_url = f"https://noembed.com/embed?url={url_video}"
            resp = requests.get(api_url).json()
            if 'error' not in resp:
                titulo = resp.get('title', titulo)
                autor = resp.get('author_name', autor)
                thumbnail = resp.get('thumbnail_url', thumbnail)
                descripcion_final = f"Aprende con {autor}. (Importado modo simple)."
                flash("Aviso: Se usó el modo simple (Noembed) por bloqueo de YouTube.", "warning")
            else:
                flash("Error crítico: No se pudo importar el video.", "error")
                return redirect('/admin')
        except:
            flash("Error de conexión al intentar modo simple.", "error")
            return redirect('/admin')

    # Guardar en Base de Datos (Sea cual sea el método que funcionó)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''INSERT INTO cursos (titulo, url_video, url_image, descripcion, maestro, foto_maestro) 
                   VALUES (%s, %s, %s, %s, %s, %s)''', 
                (titulo, url_video, thumbnail, descripcion_final, autor, foto_maestro))
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)