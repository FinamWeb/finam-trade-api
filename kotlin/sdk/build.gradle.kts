import com.google.protobuf.gradle.id
import org.jreleaser.model.Active
import org.jreleaser.model.Signing.Mode

plugins {
    id("com.google.protobuf") version "0.9.5"
    id("maven-publish")
    id("org.jreleaser") version "1.19.0"
}

val coroutinesVersion: String by project
val protobufVersion: String by project
val grpcVersion: String by project
val grpcKotlinVersion: String by project
val slf4jVersion: String by project
val ktorVersion: String by project
val jacksonVersion: String by project

val group = project.group.toString()
val projectName = rootProject.name

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.slf4j:slf4j-api:$slf4jVersion")

    // Kotlin Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:$coroutinesVersion")

    // Protobuf
    implementation("com.google.protobuf:protobuf-java:$protobufVersion")
    implementation("com.google.protobuf:protobuf-kotlin:$protobufVersion")
    implementation("com.google.protobuf:protobuf-java-util:$protobufVersion")

    // gRPC
    implementation("io.grpc:grpc-core:$grpcVersion")
    implementation("io.grpc:grpc-api:$grpcVersion")
    implementation("io.grpc:grpc-protobuf:$grpcVersion")
    implementation("io.grpc:grpc-stub:$grpcVersion")
    runtimeOnly("io.grpc:grpc-netty:$grpcVersion")

    // gRPC Kotlin
    implementation("io.grpc:grpc-kotlin-stub:$grpcKotlinVersion")
    implementation(kotlin("stdlib-jdk8"))

    //ktor
    implementation("io.ktor:ktor-client-core:${ktorVersion}")
    implementation("io.ktor:ktor-client-cio:${ktorVersion}")
    implementation("io.ktor:ktor-client-websockets:${ktorVersion}")
    implementation("io.ktor:ktor-serialization-jackson:${ktorVersion}")

    //jackson
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310:${jacksonVersion}")

}

kotlin {
    jvmToolchain(21)
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:$protobufVersion"
    }
    plugins {
        id("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:$grpcVersion"
        }
        id("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:$grpcKotlinVersion:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach { task ->
            task.plugins {
                create("grpc")
                create("grpckt")
            }
            task.builtins {
                create("kotlin")
            }
        }
    }
    sourceSets.main {
        proto.srcDir("../../proto")
    }
}

java {
    withJavadocJar()
    withSourcesJar()
}

publishing {
    publications {
        create<MavenPublication>("release") {
            from(components["java"])
            groupId = group
            artifactId = projectName
            pom {
                name.set("Finam Trade API")
                description.set("Kotlin Finam Trade API")
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
