import com.google.protobuf.gradle.remove

plugins {
    id("java")
    id("com.google.protobuf") version "0.9.5"
    id("maven-publish")
    id("groovy")
    id("application")
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
    implementation("org.codehaus.groovy:groovy-all:3.0.10")
    implementation("com.google.code.gson:gson:2.10.1")
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

application {
    mainClass = "MergeAllJsonFiles"
}

tasks.run {
    systemProperty("openapiv2.files.path", "${protobuf.generatedFilesBaseDir}/main/openapiv2")
    systemProperty("openapiv2.merged.file", "${protobuf.generatedFilesBaseDir}/main/openapiv2/grpc/tradeapi/v1/openapi.swagger.json")
    systemProperty("openapiv2.merged.title", "TradeApi")
    systemProperty("openapiv2.merged.version", version)
}

tasks.register<Zip>("golangZip") {
    archiveBaseName = "${archiveBaseName.get()}-golang"
    archiveClassifier = "golang"
    exclude( "protoc-gen-openapiv2/**")
    from(file("${protobuf.generatedFilesBaseDir}/main/go"), file("${protobuf.generatedFilesBaseDir}/main/go-grpc"))
}

tasks.register<Zip>("openapiv2Zip") {
    archiveBaseName = "${archiveBaseName.get()}-openapiv2"
    archiveClassifier = "openapiv2"
    exclude("protoc-gen-openapiv2/**")
    dependsOn(tasks.run)
    from(file("${protobuf.generatedFilesBaseDir}/main/openapiv2"))
}

tasks.publish {
    dependsOn("golangZip")
    dependsOn("openapiv2Zip")
}

