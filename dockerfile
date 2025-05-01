# Usa una imagen base oficial de Python
FROM python:3.12-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto en el que gunicorn correrá
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "django_project.wsgi:application", "--bind", "0.0.0.0:8000"]
