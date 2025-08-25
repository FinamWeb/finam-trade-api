plugins {
    id("java")
    kotlin("jvm") version "2.2.0"
    id("com.google.protobuf") version "0.9.5"
}

sourceSets.main {
    java.srcDir("../../sdk/kotlin/src/main")
}

val coroutinesVersion: String by project
val protobufVersion: String by project
val grpcVersion: String by project
val grpcKotlinVersion: String by project
val junitJupiterVersion: String by project
val junitPlatformLauncherVersion: String by project

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:$coroutinesVersion")

//    // Protobuf
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

    testImplementation("org.junit.platform:junit-platform-launcher:${junitPlatformLauncherVersion}")
    testImplementation("org.junit.jupiter:junit-jupiter-engine:${junitJupiterVersion}")
    testImplementation("org.junit.jupiter:junit-jupiter-api:${junitJupiterVersion}")

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

tasks.test {
    useJUnitPlatform()
    testLogging {
        showStandardStreams = true
    }
}