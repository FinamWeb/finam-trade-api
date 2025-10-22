import com.google.protobuf.gradle.remove
import groovy.json.JsonSlurper
import org.jreleaser.model.Active
import org.jreleaser.model.Signing.Mode
import shadow.com.google.gson.GsonBuilder

plugins {
    id("java")
    id("com.google.protobuf") version "0.9.5"
    id("maven-publish")
    id("org.jreleaser") version "1.19.0"
}

group = "ru.finam.protobuf"
version = "1.0"

repositories {
    mavenCentral()
    gradlePluginPortal()
}

val grpcVersion: String by project
val protobufVersion: String by project

dependencies {
    // gRPC
    implementation("io.grpc:grpc-protobuf:${grpcVersion}")
}

tasks.test {
    enabled = false
}
tasks.compileJava {
    enabled = false
}

tasks.compileTestJava {
    enabled = false
}

protobuf {
    generateProtoTasks {
        sourceSets.main {
            proto.srcDir("../proto")
        }
        all().configureEach {
            ofSourceSet("main")
            builtins {
                create("go")
                create("openapiv2").apply {
                    option("logtostderr=true")
                }
                create("go-grpc") {
                    outputSubDir = "go"
                }
                remove("java")
            }
        }
    }
}

tasks.register("mergeAllJsonFiles") {
    /**
     * Рекурсивно объединяет две карты (Map).
     *
     * @param map1 Первая карта, которая служит основой.
     * @param map2 Вторая карта, значения которой добавляются или перезаписывают значения первой.
     * @return Новая карта, представляющая собой результат объединения.
     */
    @Suppress("UNCHECKED_CAST")
    fun deepMerge(map1: MutableMap<Any, Any>, map2: MutableMap<Any, Any>): MutableMap<Any, Any> {
        // 1. Создаем изменяемую копию первой карты.
        val result = map1.toMutableMap()

        // 2. Итерируемся по второй карте.
        for ((key, value) in map2) {
            val existingValue = result[key]

            when (existingValue) {
                is Map<*, *> if value is Map<*, *> -> {
                    result[key] = deepMerge(existingValue as MutableMap<Any, Any>, value as MutableMap<Any, Any>)
                }

                // 4. Если значения - это списки, объединяем их, добавляя только уникальные
                //    элементы из второго списка.
                is List<*> if value is List<*> -> {
                    result[key] = existingValue + value.filter { it !in existingValue }
                }

                // 5. Во всех остальных случаях значение из второй карты перезаписывает значение в первой.
                else -> {
                    result[key] = value
                }
            }
        }
        return result
    }

    doLast {
        val startDir = File("${protobuf.generatedFilesBaseDir}/main/openapiv2")

        println("Поиск файлов *.swagger.json в директории: ${startDir.absolutePath}")
        println("--------------------------------------------------------")
        val slurper = JsonSlurper()
        var resultMergedMap = mutableMapOf<Any, Any>()
        // 3. Рекурсивно обходим все ФАЙЛЫ
        // FileType.FILES говорит, что нас интересуют только файлы, а не папки
        startDir.walkTopDown().filter { file ->
            // 4. Проверяем, заканчивается ли имя файла на ".swagger.json"
            file.name.endsWith(".swagger.json")
        }.onEach { println("  [Найден] -> ${it.path}") }.forEach {
            val fileContent = it.readText(Charsets.UTF_8)
            if (fileContent.isBlank()) {
                println("Файл ${it.absolutePath} пустой, пропускаем.")
            } else {
                try {
                    val parsedMap = slurper.parseText(fileContent) as MutableMap<Any, Any>
                    resultMergedMap = deepMerge(resultMergedMap, parsedMap)
                } catch (e: Exception) {
                    println("-> Ошибка парсинга JSON: ${e.message}")
                }
            }
        }
        resultMergedMap["info"] = mapOf(
            "title" to "TradeApi",
            "version" to version
        )
        val mergedJson = GsonBuilder()
            .setPrettyPrinting()
            .disableHtmlEscaping() // Полезно для OpenAPI/Swagger
            .create()
            .toJson(resultMergedMap)

        val outputFile = File("${protobuf.generatedFilesBaseDir}/main/openapiv2/grpc/tradeapi/v1/openapi.swagger.json")
        outputFile.writeText(mergedJson, Charsets.UTF_8)

        println("Слияние завершено. Результат сохранен в: ${outputFile.absolutePath}")
    }
}

tasks.register<Zip>("golangZip") {
    archiveBaseName = "${archiveBaseName.get()}-golang"
    archiveClassifier = "golang"
    mustRunAfter("generateProto")
    exclude("protoc-gen-openapiv2/**")
    from(file("${protobuf.generatedFilesBaseDir}/main/go"), file("${protobuf.generatedFilesBaseDir}/main/go-grpc"))
}

tasks.register<Zip>("openapiv2Zip") {
    archiveBaseName = "${archiveBaseName.get()}-openapiv2"
    archiveClassifier = "openapiv2"
    mustRunAfter("generateProto")
    dependsOn("mergeAllJsonFiles")
    exclude("protoc-gen-openapiv2/**")
    from(file("${protobuf.generatedFilesBaseDir}/main/openapiv2"))
}

tasks.publish {
    dependsOn("golangZip", "openapiv2Zip")
}

publishing {
    publications {
        create<MavenPublication>("golangPublication") {
            artifactId = rootProject.name + "-golang"
            artifact(tasks["golangZip"])
            pom {
                name.set("Finam Trade API")
                description.set("Go Finam Trade API")
                url.set("https://github.com/FinamWeb/finam-trade-api")
                issueManagement {
                    url.set("https://github.com/FinamWeb/finam-trade-api/issues")
                }
                licenses {
                    license {
                        name.set("The Apache Software License, Version 2.0")
                        url.set("http://www.apache.org/licenses/LICENSE-2.0.txt")
                        distribution.set("repo")
                    }
                }
                developers {
                    developer {
                        id.set("FinamTrade")
                        name.set("FinamTrade")
                        url.set("https://tradeapi.finam.ru/")
                    }
                }
                scm {
                    connection.set("scm:git://github.com/FinamWeb/finam-trade-api.git")
                    developerConnection.set("scm:git://github.com/FinamWeb/finam-trade-api.git")
                    url.set("https://github.com/FinamWeb/finam-trade-api")
                }
            }
        }
        create<MavenPublication>("openapiv2Publication") {
            artifactId = rootProject.name + "-openapiv2"
            artifact(tasks["openapiv2Zip"])
            pom {
                name.set("Finam Trade API")
                description.set("Go Finam Trade API")
                url.set("https://github.com/FinamWeb/finam-trade-api")
                issueManagement {
                    url.set("https://github.com/FinamWeb/finam-trade-api/issues")
                }
                licenses {
                    license {
                        name.set("The Apache Software License, Version 2.0")
                        url.set("http://www.apache.org/licenses/LICENSE-2.0.txt")
                        distribution.set("repo")
                    }
                }
                developers {
                    developer {
                        id.set("FinamTrade")
                        name.set("FinamTrade")
                        url.set("https://tradeapi.finam.ru/")
                    }
                }
                scm {
                    connection.set("scm:git://github.com/FinamWeb/finam-trade-api.git")
                    developerConnection.set("scm:git://github.com/FinamWeb/finam-trade-api.git")
                    url.set("https://github.com/FinamWeb/finam-trade-api")
                }
            }
        }
    }
    repositories {
        maven {
            name = "PreDeploy"
            url = uri(layout.buildDirectory.dir("pre-deploy"))
        }
    }
}

jreleaser {
    gitRootSearch = true
    project {
        inceptionYear.set("2025")
        author("FinamTrade")
    }
    signing {
        active = Active.ALWAYS
        armored = true
        mode = Mode.MEMORY
        verify = true
    }
    deploy {
        maven {
            mavenCentral.create("sonatype") {
                active = Active.ALWAYS
                url = "https://central.sonatype.com/api/v1/publisher"
                stagingRepository("build/pre-deploy")
                setAuthorization("Basic")
                retryDelay = 60
            }
        }
    }
    release {
        github {
            enabled = true
            skipRelease = true
            skipTag = true
        }
    }
}

