package example

import grpc.tradeapi.v1.accounts.GetAccountRequest
import kotlinx.coroutines.runBlocking
import ru.finam.tradeapi.tradeAPIClient

const val FINAM_SECRET_KEY = "FINAM_SECRET_KEY"

object GetAccount {
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        System.setProperty("logback.configurationFile", "/logback.xml")

        val client = tradeAPIClient {
            secret = System.getenv(FINAM_SECRET_KEY)
            if (secret.isNullOrEmpty()) {
                "нужно создать переменную окружения '$FINAM_SECRET_KEY'".also {
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
