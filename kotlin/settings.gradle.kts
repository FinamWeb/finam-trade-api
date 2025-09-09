plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.8.0"
}
rootProject.name = "finam-trade-api-kotlin"

include(
    "examples",
    "sdk"
)