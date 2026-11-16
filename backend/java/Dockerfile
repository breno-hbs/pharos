# Build
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -q -B dependency:go-offline
COPY src ./src
RUN mvn -q -B -DskipTests package

# Execução
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/pharos-api.jar app.jar
EXPOSE 8080
# O Render injeta a variável PORT; as credenciais do Oracle vêm de variáveis de ambiente
ENTRYPOINT ["java", "-jar", "app.jar"]
