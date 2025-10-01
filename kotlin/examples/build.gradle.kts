plugins {
    id("application")
}

application {
    mainClass = System.getenv("APP_MAIN_CLASS") ?: "example.GetAccount"
}

val coroutinesVersion: String by project
val protobufVersion: String by project
val grpcVersion: String by project
val grpcKotlinVersion: String by project
val junitJupiterVersion: String by project
val junitPlatformLauncherVersion: String by project
val logbackVersion: String by project

dependencies {
    api(project(":sdk"))
    implementation("ch.qos.logback:logback-classic:$logbackVersion")

    // Kotlin Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:${coroutinesVersion}")

    // Protobuf
    implementation("com.google.protobuf:protobuf-java:${protobufVersion}")
    implementation("com.google.protobuf:protobuf-kotlin:${protobufVersion}")
    implementation("com.google.protobuf:protobuf-java-util:${protobufVersion}")

    // gRPC
    implementation("io.grpc:grpc-api:${grpcVersion}")
    implementation("io.grpc:grpc-protobuf:${grpcVersion}")
    implementation("io.grpc:grpc-stub:${grpcVersion}")

    // gRPC Kotlin
    implementation("io.grpc:grpc-kotlin-stub:${grpcKotlinVersion}")
}
