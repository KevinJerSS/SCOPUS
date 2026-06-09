"""
Dashboard: Impacto de la IA y Data Science en la Empleabilidad de Negocios
Autor: [TU NOMBRE]
Licencia: GPL-3.0
Pregunta de investigacion:
    ¿De que manera el dominio de herramientas de IA y Data Science influye
    en las tasas de empleabilidad y la demanda de profesionales egresados
    de carreras de negocios en la actualidad?
"""

import streamlit as st          # <-- IMPORT QUE FALTABA EN TU CODIGO ORIGINAL
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# ----------------------------------------------------------------------------
# 1. CONFIGURACION DE LA PAGINA  (Criterio 6: Empatia y Estilo)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard: IA en Negocios",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
sns.set_theme(style="whitegrid")

# URL del CSV en GitHub (carga automatizada - Criterio 3 nivel Excelente)
# Reemplaza con la URL "raw" de TU repositorio:
GITHUB_RAW_URL = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/dataset.csv"

# ----------------------------------------------------------------------------
# Titulo y contexto  (Criterio 6: texto explicativo)
# ----------------------------------------------------------------------------
st.title("📈 Impacto de la IA y Data Science en la Empleabilidad de Negocios")

st.markdown(
    """
Bienvenido(a) a esta herramienta interactiva. Este dashboard analiza literatura
científica indexada en **Scopus** para responder a la pregunta de investigación:

> **¿De qué manera el dominio de herramientas de Inteligencia Artificial (IA) y
> Data Science influye en las tasas de empleabilidad y la demanda de
> profesionales egresados de carreras de negocios en la actualidad?**

👈 **Instrucciones:** Usa el menú lateral para subir tu archivo `dataset.csv`,
cargarlo automáticamente desde GitHub, o explorar el dataset local por defecto.
"""
)

# ----------------------------------------------------------------------------
# 2. CARGA Y LIMPIEZA DE DATOS  (Criterios 2 y 3: dataset y modularidad)
# ----------------------------------------------------------------------------
@st.cache_data
def load_and_clean_data(file):
    """Carga un CSV de Scopus y devuelve un DataFrame limpio y enriquecido."""
    df = pd.read_csv(file)

    # Estandarizacion de nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
    )

    # Eliminar columnas innecesarias
    df = df.drop(
        columns=["link", "art_no", "page_start", "page_end", "publication_stage"],
        errors="ignore",
    )

    # Manejo de valores nulos
    for col in ["author_keywords", "index_keywords"]:
        if col in df.columns:
            df[col] = df[col].fillna("")
    if "doi" in df.columns:
        df["doi"] = df["doi"].fillna("No_DOI")
    for col in ["volume", "issue"]:
        if col in df.columns:
            modo = df[col].mode()
            df[col] = df[col].fillna(modo[0] if not modo.empty else "1")
    if "open_access" in df.columns:
        df["open_access"] = df["open_access"].fillna("Unknown")
    if "document_type" in df.columns:
        df["document_type"] = df["document_type"].fillna("Unknown")

    # Variables calculadas
    if "cited_by" in df.columns:
        df["cited_by"] = pd.to_numeric(df["cited_by"], errors="coerce").fillna(0)
        df["cited_by_log"] = np.log1p(df["cited_by"])  # transformacion log
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    return df


def contar_keywords(serie, top_n=15):
    """Cuenta las keywords mas frecuentes a partir de una columna separada por ';'."""
    palabras = []
    for fila in serie.dropna():
        for kw in str(fila).split(";"):
            kw = kw.strip().lower()
            if kw and len(kw) > 2:
                palabras.append(kw)
    return Counter(palabras).most_common(top_n)


# ----------------------------------------------------------------------------
# Barra lateral: carga dinamica  (Criterio 3: widget local + GitHub)
# ----------------------------------------------------------------------------
st.sidebar.header("📂 Carga de Datos")
fuente = st.sidebar.radio(
    "Selecciona la fuente de datos:",
    ["Dataset local (por defecto)", "Subir mi propio CSV", "Cargar desde GitHub"],
)

uploaded_file = None
if fuente == "Subir mi propio CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Sube el archivo extraído de Scopus (CSV)", type=["csv"]
    )

# ----------------------------------------------------------------------------
# Logica de carga con manejo de errores
# ----------------------------------------------------------------------------
df = None
try:
    if fuente == "Subir mi propio CSV" and uploaded_file is not None:
        df = load_and_clean_data(uploaded_file)
        st.sidebar.success("✅ Archivo procesado y limpio.")
    elif fuente == "Cargar desde GitHub":
        df = load_and_clean_data(GITHUB_RAW_URL)
        st.sidebar.success("✅ Datos cargados desde GitHub.")
    else:
        df = load_and_clean_data("dataset.csv")
        st.sidebar.info("ℹ️ Usando dataset local (dataset.csv).")
except FileNotFoundError:
    st.error(
        "No se encontró el archivo `dataset.csv`. "
        "Usa el menú lateral para subir tu CSV o cargarlo desde GitHub."
    )
    st.stop()
except Exception as e:
    st.error(f"Se produjo un error procesando el archivo: {e}")
    st.stop()

if df is None or df.empty:
    st.warning("Aún no hay datos cargados. Selecciona una fuente en el menú lateral.")
    st.stop()

# ----------------------------------------------------------------------------
# Filtros interactivos  (Criterio 4: interactividad)
# ----------------------------------------------------------------------------
st.sidebar.header("🔎 Filtros")
if "year" in df.columns and df["year"].notna().any():
    año_min, año_max = int(df["year"].min()), int(df["year"].max())
    rango = st.sidebar.slider(
        "Rango de años:", año_min, año_max, (año_min, año_max)
    )
    df = df[(df["year"] >= rango[0]) & (df["year"] <= rango[1])]

if "document_type" in df.columns:
    tipos = sorted(df["document_type"].dropna().unique())
    sel = st.sidebar.multiselect("Tipo de documento:", tipos, default=tipos)
    if sel:
        df = df[df["document_type"].isin(sel)]

# ----------------------------------------------------------------------------
# 3. KPIs PRINCIPALES  (Criterio 4)
# ----------------------------------------------------------------------------
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Total de Artículos", df.shape[0])
col2.metric("⭐ Promedio de Citas", round(df["cited_by"].mean(), 2))
col3.metric("🏆 Máx. Citas", int(df["cited_by"].max()))
if df["year"].notna().any():
    col4.metric("📅 Años", f"{int(df['year'].min())}–{int(df['year'].max())}")

st.markdown("---")

# ----------------------------------------------------------------------------
# Fila 1: Tendencias temporales
# ----------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("📅 Evolución de Publicaciones por Año")
    st.markdown(
        "El crecimiento sostenido de publicaciones refleja el creciente interés "
        "académico en la relación entre IA/Data Science y el empleo."
    )
    fig_year, ax_year = plt.subplots(figsize=(8, 4))
    orden = sorted(df["year"].dropna().unique())
    sns.countplot(
        data=df, x="year", order=orden, ax=ax_year,
        hue="year", palette="viridis", legend=False,  # hue evita el warning
    )
    ax_year.set_xlabel("Año")
    ax_year.set_ylabel("Cantidad de Publicaciones")
    plt.setp(ax_year.get_xticklabels(), rotation=45)
    st.pyplot(fig_year)

with c2:
    st.subheader("⭐ Impacto (Citas Logarítmicas) por Año")
    st.markdown(
        "La escala logarítmica permite comparar el impacto de los artículos "
        "sin que los outliers muy citados distorsionen la tendencia."
    )
    citas_anio = df.groupby("year")["cited_by_log"].mean().reset_index()
    fig_log, ax_log = plt.subplots(figsize=(8, 4))
    sns.lineplot(
        data=citas_anio, x="year", y="cited_by_log",
        marker="o", ax=ax_log, color="coral",
    )
    ax_log.set_xlabel("Año")
    ax_log.set_ylabel("Log(Citas Promedio + 1)")
    st.pyplot(fig_log)

# ----------------------------------------------------------------------------
# Fila 2: Respuesta directa a la pregunta - HABILIDADES / COMPETENCIAS
# ----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🧠 ¿Qué competencias y habilidades destacan en la literatura?")
st.markdown(
    "Análisis de las palabras más frecuentes en los **abstracts**, revelando "
    "las competencias de IA/Data Science más demandadas en el ámbito laboral."
)

if "abstract" in df.columns and df["abstract"].notna().any():
    text = " ".join(df["abstract"].dropna().tolist()).lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    stopwords = {
        "the", "and", "to", "of", "in", "a", "is", "for", "that", "this",
        "with", "as", "on", "are", "by", "be", "data", "we", "an", "from",
        "can", "which", "it", "or", "study", "research", "paper", "has",
        "have", "these", "their", "model", "results", "based", "using",
        "such", "also", "more", "other", "into", "they", "between", "been",
        "will", "than", "both", "while", "however", "among", "through",
    }
    meaningful = [w for w in words if w not in stopwords and len(w) > 4]
    word_counts = Counter(meaningful).most_common(15)
    df_words = pd.DataFrame(
        word_counts, columns=["Concepto", "Frecuencia"]
    ).sort_values(by="Frecuencia", ascending=True)

    fig_words, ax_words = plt.subplots(figsize=(10, 5))
    ax_words.barh(df_words["Concepto"], df_words["Frecuencia"], color="teal")
    ax_words.set_xlabel("Frecuencia en Abstracts")
    ax_words.set_title("Top 15 conceptos en los resúmenes")
    st.pyplot(fig_words)
else:
    st.warning("No se encontró la columna de resúmenes (abstracts).")

# ----------------------------------------------------------------------------
# Fila 3: Keywords de los autores + Tipos de documento
# ----------------------------------------------------------------------------
st.markdown("---")
c3, c4 = st.columns(2)

with c3:
    st.subheader("🏷️ Keywords más usadas por los autores")
    st.markdown("Términos que los propios investigadores asignan a sus trabajos.")
    col_kw = "author_keywords" if "author_keywords" in df.columns else None
    if col_kw and df[col_kw].str.strip().astype(bool).any():
        top_kw = contar_keywords(df[col_kw], top_n=12)
        df_kw = pd.DataFrame(top_kw, columns=["Keyword", "Frecuencia"]).sort_values(
            by="Frecuencia", ascending=True
        )
        fig_kw, ax_kw = plt.subplots(figsize=(7, 5))
        ax_kw.barh(df_kw["Keyword"], df_kw["Frecuencia"], color="#6a4c93")
        ax_kw.set_xlabel("Frecuencia")
        st.pyplot(fig_kw)
    else:
        st.info("No hay suficientes 'Author Keywords' para graficar.")

with c4:
    st.subheader("📚 Distribución por Tipo de Documento")
    st.markdown("Composición de la base documental analizada.")
    if "document_type" in df.columns:
        conteo = df["document_type"].value_counts()
        fig_dt, ax_dt = plt.subplots(figsize=(7, 5))
        ax_dt.pie(
            conteo.values, labels=conteo.index, autopct="%1.1f%%",
            startangle=90, colors=sns.color_palette("Set2"),
        )
        ax_dt.axis("equal")
        st.pyplot(fig_dt)
    else:
        st.info("No se encontró la columna 'Document Type'.")

# ----------------------------------------------------------------------------
# Fila 4: Artículos más citados (tabla interactiva)
# ----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🏆 Artículos más influyentes (por número de citas)")
st.markdown(
    "Los trabajos más citados marcan la dirección del campo y suelen reflejar "
    "las habilidades de IA/Data Science con mayor impacto en la empleabilidad."
)
cols_tabla = [c for c in ["title", "authors", "year", "cited_by", "source_title"]
              if c in df.columns]
top_cited = df.sort_values("cited_by", ascending=False).head(10)[cols_tabla]
top_cited.columns = [c.replace("_", " ").title() for c in top_cited.columns]
st.dataframe(top_cited, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# Conclusion / cierre  (Criterio 6: empatia)
# ----------------------------------------------------------------------------
st.markdown("---")
with st.expander("📝 Interpretación: ¿qué nos dice esto sobre la empleabilidad?"):
    st.markdown(
        """
La evidencia analizada sugiere que el dominio de herramientas de IA y Data Science
(machine learning, análisis de datos, Python, business intelligence) está cada vez
más presente en la literatura sobre mercados laborales. Los abstracts y keywords
destacan competencias **híbridas** que combinan capacidades técnicas con habilidades
de negocio y comunicación, lo que apunta a una creciente demanda de egresados de
negocios capaces de manejar estas tecnologías.
"""
    )

st.caption(
    "Dashboard académico • Fuente: Scopus • Licencia GPL-3.0 • "
    "Desarrollado con Streamlit"
)
