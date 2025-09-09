import java.net.URI

plugins {
    id("com.google.protobuf") version "0.9.5"
    id("maven-publish")
}

val coroutinesVersion: String by project
val protobufVersion: String by project
val grpcVersion: String by project
val grpcKotlinVersion: String by project

repositories {
    mavenCentral()
}

dependencies {
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
}

kotlin {
    jvmToolchain(21)
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:$protobufVersion"
    }
    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:$grpcVersion"
        }
        create("grpckt") {
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

publishing {
    repositories {
        maven {
            name = "OSSRH"
            url = URI("https://oss.sonatype.org/service/local/staging/deploy/maven2/")
            credentials {
                username = System.getenv("MAVEN_USERNAME")
                password = System.getenv("MAVEN_PASSWORD")
            }
        }
    }
}
