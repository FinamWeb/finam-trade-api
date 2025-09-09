plugins {
    kotlin("jvm") version "2.2.10"
}

allprojects {
    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "kotlin")
}
