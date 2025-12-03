pipeline {
    agent any

    environment {
        // Configuración basada en tus capturas de pantalla y guía
        // Nombre definido en: Administrar Jenkins -> System -> SonarQube servers
        SONAR_SERVER = 'Sonar-Server' 
        
        // URL de tu aplicación para las pruebas DAST (ZAP)
        // Asegúrate de que esta IP sea accesible desde el contenedor de ZAP
        TARGET_URL = 'http://172.17.0.1:5000' 
        
        // Configuración para entorno Python
        VENV_NAME = 'venv'
    }

    tools {
        // Nombres definidos en: Global Tool Configuration (según tus fuentes 195, 196, 1203)
        jdk 'OpenJDK-11'
        sonarScanner 'SonarScanner' 
        // Nota: En algunas guías lo llamaste 'DependencyCheck' y en otras 'dependency-check'
        // Asegúrate que coincida con tu configuración global.
    }

    stages {
        stage('Preparación del Entorno') {
            steps {
                script {
                    echo '--- 1. Limpiando y clonando repositorio ---'
                    cleanWs()
                    checkout scm
                }
            }
        }

        stage('Instalación de Dependencias') {
            steps {
                script {
                    echo '--- 2. Creando entorno virtual Python e instalando Flask ---'
                    // Basado en la Guía Pipeline 3 (Source 1226)
                    sh """
                        python3 -m venv ${VENV_NAME}
                        . ${VENV_NAME}/bin/activate
                        pip install --upgrade pip
                        pip install flask mysql-connector-python bcrypt
                        # Si tienes un requirements.txt, usa: pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Análisis Estático (SAST) - SonarQube') {
            steps {
                script {
                    echo '--- 3. Ejecutando análisis de código con SonarQube ---'
                    // El token se maneja automáticamente si configuraste el "Server authentication token" en Jenkins
                    withSonarQubeEnv(SONAR_SERVER) {
                        sh """
                            ${tool 'SonarScanner'}/bin/sonar-scanner \
                            -Dsonar.projectKey=EvaluacionParcial3 \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3 \
                            -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Análisis de Dependencias (SCA) - OWASP Dependency-Check') {
            steps {
                script {
                    echo '--- 4. Buscando librerías vulnerables ---'
                    // Utiliza la herramienta instalada en Jenkins con la NVD API Key configurada
                    dependencyCheck additionalArguments: '--format HTML --format JSON', odzId: 'DependencyCheck'
                }
            }
            post {
                always {
                    // Publica el reporte HTML en Jenkins
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: true, keepAll: true, reportDir: '.', reportFiles: 'dependency-check-report.html', reportName: 'Dependency-Check Report', reportTitles: ''])
                }
            }
        }

        stage('Despliegue Temporal para DAST') {
            steps {
                script {
                    echo '--- 5. Levantando aplicación para pruebas dinámicas ---'
                    // Ejecutamos la app en segundo plano para que ZAP pueda atacarla
                    // Usamos nohup para que no bloquee el pipeline
                    sh """
                        . ${VENV_NAME}/bin/activate
                        nohup python3 vulnerable_app.py > app_output.log 2>&1 &
                        echo "Esperando 10 segundos para que inicie la app..."
                        sleep 10
                    """
                }
            }
        }

        stage('Análisis Dinámico (DAST) - OWASP ZAP') {
            steps {
                script {
                    echo '--- 6. Atacando la aplicación con OWASP ZAP ---'
                    // Ejecutamos ZAP vía Docker, similar a tu Guía (Source 365)
                    // Usamos --network="host" para que el contenedor vea el puerto 5000 del host
                    sh """
                        chmod 777 \$(pwd)
                        docker run --rm --network="host" -v \$(pwd):/zap/wrk/:rw -w /zap/wrk \
                        owasp/zap2docker-stable zap-baseline.py \
                        -t http://127.0.0.1:5000 \
                        -r zap_report.html \
                        || true 
                    """
                    // El "|| true" es para que el pipeline no falle si ZAP encuentra alertas (solo queremos el reporte)
                }
            }
            post {
                always {
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: true, keepAll: true, reportDir: '.', reportFiles: 'zap_report.html', reportName: 'OWASP ZAP Report', reportTitles: ''])
                }
            }
        }
    }

    post {
        always {
            echo '--- Pipeline finalizado ---'
            // Detenemos la aplicación Python que dejamos corriendo
            sh "pkill -f vulnerable_app.py || true"
            cleanWs()
        }
        success {
            echo '¡Éxito! El Build ha pasado todas las etapas de seguridad.'
        }
        failure {
            echo 'Falló el Pipeline. Revisa los logs.'
        }
    }
}
