import grpc.tradeapi.v1.accounts.AccountsServiceGrpcKt
import grpc.tradeapi.v1.accounts.GetAccountRequest
import grpc.tradeapi.v1.auth.AuthRequest
import grpc.tradeapi.v1.auth.AuthServiceGrpcKt
import grpc.tradeapi.v1.auth.TokenDetailsRequest
import io.grpc.ManagedChannelBuilder
import io.grpc.Metadata
import io.grpc.stub.MetadataUtils
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.fail

const val FINAM_SECRET_KEY = "FINAM_SECRET_KEY"

class GetAccountTest {

    private val channel = ManagedChannelBuilder
        .forAddress("api.finam.ru", 443)
        .useTransportSecurity()
        .build()

    @Test
    fun getAccount() = runBlocking<Unit> {
        val apiToken = System.getenv(FINAM_SECRET_KEY)
        if (apiToken.isNullOrEmpty()) {
            "нужно создать переменную окружения '$FINAM_SECRET_KEY'".also {
                println(it)
                fail { it }
            }
        }
        val authStub = AuthServiceGrpcKt.AuthServiceCoroutineStub(channel)
        val authResponse = authStub.auth(
            AuthRequest.newBuilder()
                .setSecret(apiToken)
                .build()
        )
        val tokenDetailsResponse = authStub.tokenDetails(
            TokenDetailsRequest.newBuilder()
                .setToken(authResponse.token)
                .build()
        )

        val accountStub = AccountsServiceGrpcKt.AccountsServiceCoroutineStub(channel)
        val header = Metadata()
        header.put(Metadata.Key.of("Authorization", Metadata.ASCII_STRING_MARSHALLER), authResponse.token)
        val accountId = tokenDetailsResponse.accountIdsList.first()
        val getAccountResponse = accountStub
            .withInterceptors(MetadataUtils.newAttachHeadersInterceptor(header))
            .getAccount(
                GetAccountRequest.newBuilder()
                    .setAccountId(accountId)
                    .build()
            )
        assertEquals(accountId, getAccountResponse.accountId)
        assertTrue(getAccountResponse.type.isNotBlank())
        assertTrue(getAccountResponse.status.isNotBlank())
        assertTrue(getAccountResponse.hasEquity())
        assertTrue(getAccountResponse.hasUnrealizedProfit())
        assertTrue(getAccountResponse.positionsCount > 0)
        assertTrue(getAccountResponse.cashCount > 0)

        println(getAccountResponse)
    }

}
