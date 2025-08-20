# Juego de Deducción Web

## Descripción del Proyecto

Este es un juego web basado en Django de deducción social, donde:

- **Master (Administrador)**: Gestiona la información secreta y supervisa el juego
- **Players (Jugadores)**: Deben descubrir la información secreta interactuando entre ellos

## Tecnologías Utilizadas

- **Backend**: Django 4.2.23
- **Base de datos**: SQLite3
- **Autenticación**: OAuth2 (django-oauth-toolkit)
- **API**: Django REST Framework
- **Python**: 3.11.9

## Estructura del Proyecto

```
ProyectoMindGame/
├── AIBLGame/              # Configuración principal del proyecto
│   ├── settings.py        # Configuraciones del proyecto
│   ├── urls.py           # URLs principales
│   ├── wsgi.py           # Configuración WSGI
│   └── asgi.py           # Configuración ASGI
├── master/               # Aplicación del Master
│   ├── models.py         # Modelos de datos
│   ├── views.py          # Vistas de la API
│   ├── serializers.py    # Serializadores para la API
│   ├── admin.py          # Configuración del admin
│   └── urls.py           # URLs de la aplicación
├── players/              # Aplicación de los players
│   ├── models.py         # Modelos de datos
│   ├── views.py          # Vistas de la API
│   ├── serializers.py    # Serializadores para la API
│   ├── admin.py          # Configuración del admin
│   └── urls.py           # URLs de la aplicación
└── manage.py             # Comando de gestión de Django
```

## Cómo arrancar el juego

### 1. Clonar el repositorio
```bash
git clone [URL-del-repositorio]
```

### 2. Levantar con Docker
```bash
docker-compose up --build
```

### 3. Conectarse al juego
- **Desde tu PC**: http://localhost:8000
- **Desde móvil (mismo WiFi)**: http://[tu-ip]:8000

