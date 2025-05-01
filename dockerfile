# Imagen base liviana de Python 3.12
FROM python:3.12-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todo el contenido del proyecto al contenedor
COPY . .

# Actualizar pip e instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Crear directorios para static y media (por si acaso)
RUN mkdir -p /app/staticfiles /app/media

# Exponer el puerto por el que se servirá la aplicación
EXPOSE 8000

# Comando de arranque usando Gunicorn
CMD ["gunicorn", "django_project.wsgi:application", "--bind", "0.0.0.0:8000"]
