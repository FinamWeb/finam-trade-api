package example

import grpc.tradeapi.v1.accounts.GetAccountRequest
import kotlinx.coroutines.runBlocking
import ru.finam.tradeapi.tradeAPIClient

const val SECRET_ENV = "TRADE_API_SECRET"

/** Deprecated name kept as a fallback for existing setups. */
const val LEGACY_SECRET_ENV = "FINAM_SECRET_KEY"

/** Reads the API secret from [SECRET_ENV], falling back to [LEGACY_SECRET_ENV]. */
fun secretFromEnv(): String? =
    System.getenv(SECRET_ENV)?.takeIf { it.isNotEmpty() } ?: System.getenv(LEGACY_SECRET_ENV)

object GetAccount {
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        System.setProperty("logback.configurationFile", "/logback.xml")

        val client = tradeAPIClient {
            secret = secretFromEnv()
            if (secret.isNullOrEmpty()) {
                "нужно создать переменную окружения '$SECRET_ENV'".also {
                    throw RuntimeException(it)
                }
            }
        }
        client.start().collect { details ->
            details.accountIdsList.forEach { accountId ->
                client.accountsServiceStub()
                    .getAccount(
                        GetAccountRequest.newBuilder()
                            .setAccountId(accountId)
                            .build()
                    )
                    .also { acc ->
                        println("Account ID: ${acc.accountId}")
                        acc.cashList.forEach { cash -> println("${cash.currencyCode}: ${cash.units}") }
                        println()
                    }
            }
        }
    }
}
