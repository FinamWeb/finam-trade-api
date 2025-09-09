package ru.finam.tradeapi

import grpc.tradeapi.v1.accounts.AccountsServiceGrpcKt
import grpc.tradeapi.v1.auth.AuthRequest
import grpc.tradeapi.v1.auth.AuthServiceGrpcKt
import grpc.tradeapi.v1.auth.TokenDetailsRequest
import grpc.tradeapi.v1.auth.TokenDetailsResponse
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.Metadata
import io.grpc.stub.MetadataUtils

fun tradeAPIClient(block: TradeAPIClientOptions.() -> Unit = {}): TradeAPIClient {
    val options = TradeAPIClientOptions().apply(block)
    val channel = ManagedChannelBuilder
        .forAddress(options.host, options.port)
        .also {
            if (options.port != 443) {
                it.usePlaintext()
            }
        }
        .build()
    return TradeAPIClient(channel, options.secret!!)
}

class TradeAPIClientOptions {
    var host: String = "api.finam.ru"
    var port: Int = 443
    var secret: String? = null
}

class TradeAPIClient(
    private val channel: ManagedChannel,
    private val secret: String
) {
    private val authHeader = Metadata.Key.of("Authorization", Metadata.ASCII_STRING_MARSHALLER)

    private var token: String? = null

    suspend fun auth() {
        token = authServiceStub().auth(
            AuthRequest.newBuilder()
                .setSecret(secret)
                .build()
        ).token
    }

    suspend fun tokenDetails(): TokenDetailsResponse =
        authServiceStub().tokenDetails(
            TokenDetailsRequest.newBuilder()
                .setToken(token)
                .build()
        )

    fun authServiceStub(): AuthServiceGrpcKt.AuthServiceCoroutineStub =
        AuthServiceGrpcKt.AuthServiceCoroutineStub(channel)

    fun accountsServiceStub(): AccountsServiceGrpcKt.AccountsServiceCoroutineStub =
        AccountsServiceGrpcKt.AccountsServiceCoroutineStub(channel)
            .withInterceptors(MetadataUtils.newAttachHeadersInterceptor(authMd()))

    private fun authMd() = Metadata().apply { put(authHeader, token) }
}
