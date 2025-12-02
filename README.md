🎸 Muxicos - Plataforma de Aprendizaje Musical

Muxicos es una plataforma web estilo SaaS (Software as a Service) diseñada para conectar a estudiantes con cursos de música regional mexicana (Guitarra, Acordeón, Tololoche, etc.).

El proyecto combina una interfaz moderna y oscura (inspirada en Spotify/Netflix) con un backend robusto en Python que gestiona usuarios, seguridad y contenido dinámico.

🚀 Características Principales

🔐 Autenticación y Seguridad

Registro Seguro: Validación de contraseñas en tiempo real (8 caracteres, mayúsculas, símbolos).

Hashing: Las contraseñas se encriptan con PBKDF2-SHA256 antes de guardarse en la base de datos.

Sesiones: Gestión de estado de usuario mediante cookies seguras (flask.session).

🎓 Gestión de Cursos (LMS)

Catálogo Dinámico: Buscador en tiempo real y filtros por instrumento sin recargar la página (JS Vanilla).

Admin Panel Secreto: /admin permite subir cursos pegando solo el link de YouTube.

YouTube Scraper: El sistema extrae automáticamente título, miniatura y autor usando la API noembed.

Reproductor Optimizado: Usa lite-youtube-embed para carga instantánea y evita el rastreo de cookies de terceros.

👤 Perfil de Usuario

Dashboard Personal: Vista de cursos recientes y progreso.

Configuración Modal: Edición de datos (Nombre, Teléfono, Foto) sin salir de la página.

Checkout Simulado: Interfaz de pago con pestañas para Tarjeta, PayPal, Google Pay y Apple Pay.

🛠️ Stack Tecnológico

Backend: Python 3, Flask.

Base de Datos: PostgreSQL (Alojada en Neon Tech - Serverless).

Frontend: HTML5, JavaScript (Vanilla), Tailwind CSS (vía CDN).

Infraestructura: GitHub Codespaces.

📦 Instalación y Despliegue

Requisitos Previos

Python 3.8+

Una base de datos PostgreSQL (recomendado Neon.tech).

Pasos para correr localmente

Clonar el repositorio:

git clone [https://github.com/tu-usuario/muxicos.git](https://github.com/tu-usuario/muxicos.git)
cd muxicos


Instalar dependencias:

pip install -r requirements.txt


Configurar Variables de Entorno:
Crea un archivo .env en la raíz y agrega tu conexión a Neon:

DATABASE_URL=postgresql://usuario:password@ep-cool-db.us-east-2.aws.neon.tech/neondb


Ejecutar el servidor:

python app.py


La aplicación correrá en http://localhost:8000.

📂 Estructura del Proyecto

muxicos/
├── app.py              # Cerebro de la aplicación (Rutas y Lógica)
├── requirements.txt    # Lista de librerías necesarias
├── .env                # Credenciales (No subir a GitHub)
├── templates/          # Vistas HTML (Frontend)
│   ├── bienvenida.html # Landing Page (Pública)
│   ├── index.html      # Dashboard (Privado)
│   ├── login.html      # Inicio de sesión
│   ├── registro.html   # Crear cuenta
│   ├── perfil.html     # Configuración de usuario
│   ├── cursos.html     # Catálogo y Buscador
│   ├── detalle.html    # Reproductor de video
│   ├── config.html     # Pagos y Ajustes
│   └── admin.html      # Panel de carga de videos
└── README.md           # Documentación


🤝 Contribución

Este proyecto fue desarrollado con fines educativos para la materia de Metodologías para el Desarrollo de Proyectos / Seguridad Informática.

Desarrollado por: Angel Anguiano y Axel Suarez.   