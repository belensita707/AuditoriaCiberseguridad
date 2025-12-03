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
        script {
            // *** CORRECCIÓN: Usamos 'tool name' para obtener la RUTA del ejecutable ***
            // La variable scannerHome ahora contiene la ruta completa, ej: /var/jenkins_home/tools/SonarQubeScanner/.../
            def scannerHome = tool name: 'SonarQubeScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

            withSonarQubeEnv("${SONAR_SERVER}") {
                // Invocamos el ejecutable usando la RUTA COMPLETA obtenida del comando tool
                sh "${scannerHome}/bin/sonar-scanner \
                -Dsonar.projectKey=AuditoriaCiberseguridad \
                -Dsonar.sources=. \
                -Dsonar.python.version=3 \
                -Dsonar.sourceEncoding=UTF-8"
            }
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
