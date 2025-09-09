package example

import grpc.tradeapi.v1.accounts.GetAccountRequest
import kotlinx.coroutines.runBlocking
import ru.finam.tradeapi.tradeAPIClient

const val FINAM_SECRET_KEY = "FINAM_SECRET_KEY"

object GetAccount {
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {

        val client = tradeAPIClient {
            secret = System.getenv(FINAM_SECRET_KEY)
            if (secret.isNullOrEmpty()) {
                "нужно создать переменную окружения '$FINAM_SECRET_KEY'".also {
                    throw RuntimeException(it)
                }
            }
        }
        client.auth()

        val tokenDetailsResponse = client.tokenDetails()
        println(tokenDetailsResponse)

        val accountId = tokenDetailsResponse.accountIdsList.first()
        val getAccountResponse = client.accountsServiceStub()
            .getAccount(
                GetAccountRequest.newBuilder()
                    .setAccountId(accountId)
                    .build()
            )

        println(getAccountResponse)
    }
}