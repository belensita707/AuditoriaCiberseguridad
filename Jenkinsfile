pipeline {
    agent any

    environment {
        // Variables de Entorno (Tomadas de tus configuraciones)
        SONAR_SERVER = 'SonarQubePruebas' 
        TARGET_URL = 'http://localhost:5000/'
    }

    stages {
        // -------------------------------------------------------------------------
        // ETAPA 1: OBTENCIÓN DEL CÓDIGO
        // -------------------------------------------------------------------------
        stage('Checkout') {
            steps {
                echo "Descargando código corregido desde Git..."
                checkout scm
            }
        }

        // -------------------------------------------------------------------------
        // ETAPA 2: ANÁLISIS ESTÁTICO (SAST) - SonarQube
        // La sintaxis ha sido simplificada para eliminar el conflicto de compilación Groovy.
        // -------------------------------------------------------------------------
        stage('SonarQube Analysis (SAST)') {
            steps {
                echo "Iniciando Análisis Estático (SAST) para validar correcciones de código."
                
                // *** SOLUCIÓN DEFINITIVA DE COMPILACIÓN ***
                // Utilizamos el bloque 'withSonarQubeEnv' que inyecta las variables necesarias.
                // El comando 'sonar-scanner' se llama directamente (asumiendo que está en el PATH de Jenkins).
                withSonarQubeEnv("${SONAR_SERVER}") {
                    sh "sonar-scanner \
                    -Dsonar.projectKey=AuditoriaCiberseguridad \
                    -Dsonar.sources=. \
                    -Dsonar.python.version=3 \
                    -Dsonar.sourceEncoding=UTF-8"
                }
            }
        }

        // -------------------------------------------------------------------------
        // ETAPA 3: ANÁLISIS DINÁMICO (DAST) - OWASP ZAP (Requisito del Profesor)
        // -------------------------------------------------------------------------
        stage('OWASP ZAP Scan (DAST)') {
            steps {
                echo "Ejecutando escaneo dinámico con ZAP contra ${TARGET_URL}..."
                sh '''
                    docker run --rm \
                    --network="host" \
                    -v $(pwd):/zap/wrk/:rw \
                    owasp/zap2docker-stable zap-baseline.py \
                    -t ${TARGET_URL} \
                    -r zap_report.html \
                    -I \
                    || echo "ZAP terminó el escaneo"
                '''
            }
            post {
                always {
                    publishHTML([
                        reportDir: '.',
                        reportFiles: 'zap_report.html',
                        reportName: 'OWASP ZAP Security Report',
                        // <<< Parámetros REQUERIDOS Añadidos >>>
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: true
                    ])
                }
            }
        }
        
        // -------------------------------------------------------------------------
        // ETAPA 4: ANÁLISIS DE DEPENDENCIAS (SCA)
        // -------------------------------------------------------------------------
        stage('OWASP Dependency-Check') {
            steps {
                echo "Analizando librerías."
                sh '''
                    docker run --rm \
                    -v $(pwd):/src \
                    owasp/dependency-check \
                    --scan /src \
                    --format HTML \
                    --out /src/dependency-check-report
                '''
            }
            post {
                always {
                    publishHTML([
                        reportDir: '.',
                        reportFiles: 'dependency-check-report/dependency-check-report.html',
                        reportName: 'Dependency Check Report',
                        // <<< Parámetros REQUERIDOS Añadidos >>>
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: true
                    ])
                }
            }
        }
    }
}
