<p align="center">
  <img src="assets/logo.png" width="420" alt="Muxicos Logo">
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
  <img src="https://img.shields.io/badge/Database-PostgreSQL-316192?style=for-the-badge">
</p>

---

## 🌑 ¿Qué es Muxicos?

Muxicos es una plataforma web moderna, con una estética oscura y elegante, diseñada para conectar a estudiantes con cursos de guitarra, acordeón, tololoche y más.  
Su espíritu es simple: **hacer accesible el aprendizaje musical con una experiencia fluida, rápida y sin ruido innecesario**.

---

## 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- Validación avanzada de contraseñas en tiempo real.  
- Contraseñas encriptadas con **PBKDF2-SHA256**.  
- Manejo seguro de sesiones con cookies firmadas.

---

### 🎓 Sistema de Cursos (LMS)
- Catálogo con **búsqueda instantánea** sin recargar la página.  
- Filtros por instrumento (Vanilla JS).  
- Panel administrativo secreto: **/admin**.  
- Carga de cursos solo pegando un enlace de YouTube.  
- Scraper automático vía *noembed* (título, autor y miniatura).  
- Reproductor rápido con **lite-youtube-embed** (sin rastreo).

---

### 👤 Perfil del Usuario
- Dashboard personalizado.  
- Edición del perfil desde un modal elegante.  
- Checkout simulado: Tarjeta, PayPal, Google Pay, Apple Pay.  

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
git clone https://github.com/tu-usuario/muxicos.git
cd muxicos
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Crear archivo .env
```bash
DATABASE_URL=postgresql://usuario:password@ep-cool-db.us-east-2.aws.neon.tech/neondb
```

### 4. Ejecutar el servidor
```bash
python app.py
La app correrá en: http://localhost:8000
```

## 📂 Estructura del Proyecto

```text
muxicos/
├── app.py              # Lógica principal y rutas
├── requirements.txt    # Librerías necesarias
├── .env                # Variables sensibles
├── assets
│   ├──icon.png
│   ├──logo.png
├── templates/
│   ├── bienvenida.html
│   ├── index.html
│   ├── login.html
│   ├── registro.html
│   ├── perfil.html
│   ├── cursos.html
│   ├── detalle.html
│   ├── config.html
│   └── admin.html
└── README.md
```