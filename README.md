# Twitter Sentiment Financial Analysis

Un proyecto de análisis financiero que combina análisis de sentimientos de Twitter con datos históricos del mercado para la toma de decisiones de inversión inteligentes.

##  Descripción del Proyecto

Este sistema utiliza una arquitectura de microservicios distribuidos para analizar tweets relacionados con empresas financieras y generar portafolios de inversión optimizados. El proyecto procesa datos de sentimientos de Twitter, los combina con precios históricos del mercado y genera estrategias de inversión comparándolas con el índice Nasdaq QQQ.

### Características principales:
- **Arquitectura de microservicios**: 5 servicios independientes y escalables
- **Procesamiento paralelo**: Implementado con Ray para acelerar el análisis de grandes volúmenes de datos
- **API REST**: Endpoints accesibles mediante Flask
- **Frontend interactivo**: Interfaz web para visualizar resultados
- **Benchmarking**: Herramientas para medir el rendimiento del sistema
- **Análisis comparativo**: Evaluación de estrategias vs. Nasdaq QQQ

##  Arquitectura del Sistema

```
┌─────────┐    ┌─────────────┐    ┌─────────────────────────────────────────┐
│ Client  │───▶│ API Gateway │───▶│ ┌─────────────────────────────────────┐ │
│         │    │             │    │ │           Microserviices            │ │
└─────────┘    └─────────────┘    │ │                                     │ │
                                  │ │ ┌─────────────────────────────────┐ │ │
                                  │ │ │     sentiment_data_service      │ │ │
                                  │ │ └─────────────────────────────────┘ │ │
                                  │ │                                     │ │
                                  │ │                                     │ │
                                  │ │ ┌─────────────────────────────────┐ │ │
                                  │ │ │      process_data_service       │ │ │
                                  │ │ └─────────────────────────────────┘ │ │
                                  │ │                                     │ │
                                  │ │                                     │ │
                                  │ │ ┌─────────────────────────────────┐ │ │
                                  │ │ │      market_data_service        │ │ │
                                  │ │ └─────────────────────────────────┘ │ │
                                  │ │                                     │ │
                                  │ │                                     │ │
                                  │ │ ┌─────────────────────────────────┐ │ │
                                  │ │ │       portfolio_service         │ │ │
                                  │ │ └─────────────────────────────────┘ │ │
                                  │ │                                     │ │
                                  │ │                                     │ │
                                  │ │ ┌─────────────────────────────────┐ │ │
                                  │ │ │         plot_service            │ │ │
                                  │ │ └─────────────────────────────────┘ │ │
                                  │ └─────────────────────────────────────┘ │
                                  └─────────────────────────────────────────┘
```

### Servicios de Benchmarking

- **Benchmark Process data service ** (`localhost:5002/metrica`)
  - Compara rendimiento paralelo vs. secuencial
  
- **Benchmark Market data service ** (`localhost:5003/metrica`)
  - Mide únicamente tiempo de procesamiento paralelo

##  Microservicios Detallados

### 1. Sentiment Data Service
- **Endpoint**: `localhost:5000/sentiment`
- **Propósito**: Procesamiento inicial de datos de sentimientos
- **Funciones**: 
  - Carga y limpia `sentiment_data.csv`
  - Calcula métricas de engagement (twitterComments/twitterLikes)
  - Filtra tweets relevantes (>20 likes, >10 comentarios)
- **Salida**: JSON con fecha, símbolo, comentarios, likes y ratio de engagement

### 2. Process Data Service
- **Endpoint**: `localhost:5000/process`
- **Propósito**: Ranking y selección de mejores acciones
- **Funciones**:
  - Agrupa datos por mes
  - Calcula promedios mensuales de engagement
  - Genera ranking de las top 5 acciones por mes
- **Salida**: Diccionario JSON con las mejores acciones mensuales

### 3. Market Data Service
- **Endpoint**: `localhost:5000/market`
- **Propósito**: Descarga de datos históricos del mercado
- **Funciones**:
  - Obtiene precios históricos vía yfinance (2021-2023)
  - Procesamiento paralelo con Ray
- **Salida**: JSON con datos de precios [fecha, ticker, precio_cierre]

### 4. Portfolio Service
- **Endpoint**: `localhost:5000/portfolio`
- **Propósito**: Construcción y evaluación del portafolio
- **Funciones**:
  - Calcula retornos logarítmicos
  - Construye portafolio mensual con top acciones
  - Compara con Nasdaq QQQ
- **Salida**: JSON con retornos del portafolio y Nasdaq

### 5. Plot Service
- **Endpoint**: `localhost:5000/plot`
- **Propósito**: Visualización de resultados
- **Funciones**:
  - Genera gráficos de retornos acumulados
  - Comparación visual estrategia vs. mercado
- **Salida**: Imagen PNG

##  Instalación y Configuración

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd twitter-sentiment
```

2. **Construir los contenedores**
```bash
docker-compose build
```

3. **Iniciar los servicios**
```bash
docker-compose up -d
```

## 💻 Uso del Sistema

### Opción 1: Interfaz Web (Recomendado)

1. **Acceder al frontend**: http://localhost:3000/

2. **Navegación por secciones**:
   - **Tabla de Sentimientos**: Visualiza datos procesados del CSV
   - **Portafolio Resultante**: Muestra la estrategia generada (tiempo de carga: ~30 segundos)
   - **Gráfico de Rendimiento**: Botón para cargar visualización comparativa

### Opción 2: API Endpoints

Ejecutar en el siguiente orden para flujo completo:

```bash
# 1. Procesar datos de sentimientos
curl http://localhost:5000/sentiment

# 2. Generar ranking de acciones
curl http://localhost:5000/process

# 3. Obtener datos de mercado
curl http://localhost:5000/market

# 4. Construir portafolio
curl http://localhost:5000/portfolio

# 5. Generar visualización
curl http://localhost:5000/plot
```

### Benchmarking

```bash
# Comparación Process data service (paralelo vs secuencial)
curl http://localhost:5002/metrica

# Solo medición Market data service
curl http://localhost:5003/metrica
```

**Respuesta de ejemplo**:
```json
{
    "performance_comparison": {
        "parallel_processing": {
            "method": "Ray parallel processing",
            "time_seconds": 8.9165
        }
    }
}
```

##  Tecnologías Utilizadas

- **Python 3.10**: Lenguaje base
- **Flask**: Framework web para APIs REST
- **Ray**: Framework de computación paralela y distribuida
- **Pandas**: Manipulación y análisis de datos
- **yfinance**: Descarga de datos financieros
- **Matplotlib**: Generación de gráficos
- **Docker & Docker Compose**: Containerización y orquestación

##  Datos y Fuentes

- **Datos de Twitter**: `sentiment_data.csv` (incluido en `/data`)
- **Datos financieros**: Yahoo Finance vía yfinance
- **Período de análisis**: Enero 2021 - Marzo 2023
- Nasdaq QQQ como índice de referencia

### Puertos utilizados:
- Frontend: 3000
- API Principal: 5000
- Benchmark: 5002
- Benchmark: 5003

##  Flujo de Datos

```
sentiment_data.csv → Sentiment Service → Process Service
                                            ↓
Market Data (yfinance) ← Market Service ← Portfolio Service
                                            ↓
                                        Plot Service
```

##  Contribución

Este proyecto fue desarrollado para la clase de "Infraestructuras Paralelas y Distribuidas", demostrando la implementación práctica de:
- Microservicios
- Computación paralela
- APIs RESTful

---

##  Equipo de Desarrollo

| Integrante | Código Estudiantil | 
|------------|-------------------|
| **Pablo Esteban Becerra** | 2243506 | 
| **Fernando Cardona Giraldo** | 2241381 | 
| **Juan Manuel Vargas** | 2438185 | 

---

### 🎓 Información Académica
- **Institución:** Universidad del Valle
- **Programa:** Ingeniería de Sistemas
- **Materia:** Infraestructuras Paralelas y Distribuidas
- **Periodo Académico:** 2025-1

---

**Nota**: Asegúrate de que todos los contenedores estén ejecutándose antes de acceder al frontend o realizar llamadas a la API.
