<p align="center">
  <img src="static/logo.png" width="420" alt="Muxicos Logo">
</p>

<h1 align="center">🎸 Muxicos</h1>
<h3 align="center">Plataforma SaaS para Aprender Música Regional Mexicana</h3>

<p align="center">
  <em>Un escenario donde la técnica y la pasión se encuentran.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-En%20Desarrollo-6A5ACD?style=for-the-badge">
  <img src="https://img.shields.io/badge/Frontend-HTML%20%7C%20JS%20%7C%20Tailwind-1E90FF?style=for-the-badge">
  <img src="https://img.shields.io/badge/Backend-Python%20Flask-32CD32?style=for-the-badge">
  <img src="https://img.shields.io/badge/Gestión-SCRUM%20Methodology-FF8C00?style=for-the-badge">
</p>

---

## 🌑 ¿Qué es Muxicos?

Muxicos es una página web **PaaS** (Platform as a Service) enfocada en brindar apoyo, soporte y enseñanza para el aprendizaje de instrumentos musicales del **regional mexicano**.

La plataforma está diseñada para atender a cualquier usuario, ya sea **nacional o internacional**, y se adapta a todos los niveles, desde personas **sin experiencia** hasta músicos **con experiencia** que buscan perfeccionar su técnica.

---

## 🚀 Características Principales

### 🎨 Experiencia de Usuario (UI/UX) - **¡NUEVO!**
- **Sidebar Responsiva:** Navegación lateral colapsable con animaciones suaves y cambio dinámico de logotipos.
- **Hero Banner Cinemático:** Slider automático en el Home con degradados inmersivos.
- **Ambient Glow:** Reproductor de video con efecto de luz ambiental reactiva (estilo streaming moderno).
- **Modo Oscuro Nativo:** Interfaz optimizada para largas sesiones de estudio sin fatiga visual.

### 🔐 Autenticación y Seguridad
- Validación avanzada de contraseñas en tiempo real.  
- Contraseñas encriptadas con **PBKDF2-SHA256**.  
- Manejo seguro de sesiones con cookies firmadas.

### 🎓 Sistema de Cursos (LMS)
- Panel administrativo secreto: **/admin**.  
- Carga de cursos inteligente (Scraper automático de metadatos de YouTube).  
- Filtros por instrumento y categorías.
- Reproductor rápido con **lite-youtube-embed** (sin rastreo ni cookies de terceros).

---

## 📊 Gestión del Proyecto (SCRUM)

El desarrollo de este proyecto sigue la metodología Ágil/SCRUM.  
Se incluye el artefacto de gestión principal en la raíz del repositorio:
- **Archivo:** `Muxicos_Project_Management.xlsx`
- **Contenido:** Product Backlog histórico, Planificación de 5 Sprints y Dashboard de métricas (Velocity & Burndown Charts).

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Backend | Python + Flask |
| Base de Datos | PostgreSQL (Neon.tech serverless) |
| Frontend | HTML5, Tailwind CSS (CDN), JavaScript Vanilla |
| Infraestructura | GitHub Codespaces |

---

## 📦 Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/muxicos.git](https://github.com/tu-usuario/muxicos.git)
cd muxicos
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto y agrega tu conexión a la base de datos:
```bash
# Ejemplo de contenido para .env
DATABASE_URL=postgresql://usuario:password@ep-cool-db.us-east-2.aws.neon.tech/neondb
```

### 4. Ejecutar el servidor
```bash
python app.py
```
La aplicación correrá en: http://localhost:8000

## 📂 Estructura del Proyecto

```bash
muxicos/
├── app.py                      # Lógica principal y rutas
├── requirements.txt            # Librerías necesarias
├── .env                        # Variables sensibles
├── Muxicos_Project_Management.xlsx  # 📊 Documentación SCRUM (Backlog/Sprints)
├── static/                     # Archivos estáticos (Imágenes/CSS/JS)
│   ├── icon.png                # Icono modo claro
│   ├── icon_alt.png            # Icono modo oscuro
│   ├── logo.png                # Logo modo claro
│   └── logo_alt.png            # Logo modo oscuro
├── templates/                  # Vistas HTML (Jinja2)
│   ├── index.html              # Home con Hero Slider
│   ├── sidebar.html            # Componente: Barra lateral responsiva
│   ├── user_menu.html          # Componente: Menú de usuario
│   ├── detalle.html            # Vista de curso con efecto Glow
│   ├── cursos.html             # Catálogo
│   ├── login.html              # Autenticación
│   ├── registro.html
│   ├── perfil.html
│   ├── admin.html              # Panel de control
│   └── ... (otros)
└── README.md
```