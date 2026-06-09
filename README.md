# 📈 Impacto de la IA y Data Science en la Empleabilidad de Negocios

Dashboard interactivo desarrollado en **Streamlit** que analiza literatura científica
indexada en **Scopus** para responder a una pregunta de investigación sobre el mercado
laboral y las competencias en Inteligencia Artificial.

## ❓ Pregunta de Investigación

> ¿De qué manera el dominio de herramientas de Inteligencia Artificial (IA) y Data
> Science influye en las tasas de empleabilidad y la demanda de profesionales
> egresados de carreras de negocios en la actualidad?

## 🔑 Keywords (estrategia de búsqueda en Scopus)

Cadena booleana utilizada para extraer el dataset:

```
( "Artificial Intelligence" OR "Data Science" )
AND ( "Employability" OR "Job Market" )
AND ( "Business" OR "Skills" )
```

Las 4 palabras clave principales son: **Artificial Intelligence**, **Data Science**,
**Employability**, **Business Skills**.

## 📊 Dataset

- Fuente: **Scopus** (exportación CSV).
- **41 artículos** científicos vigentes (2014–2026).
- Metadatos: Autores, Título, Año, Abstract, Citas, Keywords, Tipo de documento, DOI.

## 🚀 Funcionalidades

- Carga de datos en **3 modos**: dataset local, subida manual (widget) y carga
  automatizada desde **GitHub**.
- KPIs principales (total de artículos, promedio y máximo de citas, rango de años).
- Filtros interactivos por año y tipo de documento.
- Gráficos: evolución de publicaciones, impacto logarítmico de citas, análisis de
  palabras en abstracts, keywords de autores, distribución por tipo de documento y
  ranking de artículos más citados.

## 🛠️ Instalación y ejecución local

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Despliegue

La aplicación puede desplegarse gratuitamente en **Streamlit Community Cloud**
conectando este repositorio de GitHub.

## 📂 Estructura del proyecto

```
.
├── app.py            # Aplicación principal de Streamlit
├── dataset.csv       # Dataset extraído de Scopus
├── requirements.txt  # Dependencias
├── LICENSE           # Licencia GPL-3.0
└── README.md         # Este archivo
```

## 📜 Licencia

Este proyecto está bajo la licencia **GPL-3.0**. Consulta el archivo [LICENSE](LICENSE).

---

Autor: **[TU NOMBRE]** · Curso: Machine Learning · Dr. Jesús Alvarado
