package ru.finam.tradeapi

import com.google.protobuf.util.Timestamps
import grpc.tradeapi.v1.accounts.AccountsServiceGrpcKt
import grpc.tradeapi.v1.assets.AssetsServiceGrpcKt
import grpc.tradeapi.v1.auth.AuthServiceGrpcKt
import grpc.tradeapi.v1.auth.SubscribeJwtRenewalRequest
import grpc.tradeapi.v1.auth.TokenDetailsRequest
import grpc.tradeapi.v1.auth.TokenDetailsResponse
import grpc.tradeapi.v1.marketdata.MarketDataServiceGrpcKt
import grpc.tradeapi.v1.orders.OrdersServiceGrpcKt
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.Metadata
import io.grpc.stub.AbstractStub
import io.grpc.stub.MetadataUtils
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.SendChannel
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.util.*

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
    return options.secret?.let { TradeAPIClient(channel, it) }
        ?: throw IllegalArgumentException("Missing secret")
}

class TradeAPIClientOptions {
    var host: String = "api.finam.ru"
    var port: Int = 443
    var secret: String? = null
}

class TradeAPIClient(
    private val grpc: ManagedChannel,
    private val secret: String
) {
    private val logger: Logger = LoggerFactory.getLogger(TradeAPIClient::class.java)
    private val authHeader = Metadata.Key.of("Authorization", Metadata.ASCII_STRING_MARSHALLER)

    private var token: String? = null
    private var job: Job? = null

    private fun job(sender: SendChannel<TokenDetailsResponse>): Job = CoroutineScope(Dispatchers.IO).launch {
        while (currentCoroutineContext().isActive) {
            try {
                authServiceStub().subscribeJwtRenewal(
                    SubscribeJwtRenewalRequest.newBuilder()
                        .setSecret(secret)
                        .build()
                ).collect {
                    token = it.token
                    val details = tokenDetails()
                    logger.debug(
                        "New auth token received. Expiration: {}",
                        Date(Timestamps.toMillis(details.expiresAt))
                    )
                    sender.send(details)
                }
            } catch (e: Exception) {
                logger.error(e.message)
                delay(10000L)
            }
        }
    }

    fun start(): Flow<TokenDetailsResponse> = channelFlow {
        if (job != null) {
            throw IllegalStateException("Trade API client already started")
        }
        job = job(channel)
        job?.invokeOnCompletion { t ->
            logger.debug("Job completed")
            channel.close(t)
        }
        awaitClose {
            logger.debug("Flow closed")
            job?.cancel()
            job = null
        }
    }

    fun stop() {
        job?.cancel()
        job = null
        logger.debug("Client stopped")
    }

    suspend fun tokenDetails(): TokenDetailsResponse =
        authServiceStub().tokenDetails(
            TokenDetailsRequest.newBuilder()
                .setToken(token)
                .build()
        )

    fun accountsServiceStub(): AccountsServiceGrpcKt.AccountsServiceCoroutineStub =
        AccountsServiceGrpcKt.AccountsServiceCoroutineStub(grpc).authorized()

    fun assetsServiceStub(): AssetsServiceGrpcKt.AssetsServiceCoroutineStub =
        AssetsServiceGrpcKt.AssetsServiceCoroutineStub(grpc).authorized()

    fun authServiceStub(): AuthServiceGrpcKt.AuthServiceCoroutineStub =
        AuthServiceGrpcKt.AuthServiceCoroutineStub(grpc)

    fun marketDataServiceStub(): MarketDataServiceGrpcKt.MarketDataServiceCoroutineStub =
        MarketDataServiceGrpcKt.MarketDataServiceCoroutineStub(grpc).authorized()

    fun ordersServiceStub(): OrdersServiceGrpcKt.OrdersServiceCoroutineStub =
        OrdersServiceGrpcKt.OrdersServiceCoroutineStub(grpc).authorized()

    private fun <T : AbstractStub<T>> T.authorized() = withInterceptors(
        MetadataUtils.newAttachHeadersInterceptor(
            Metadata().apply { put(authHeader, token) }
        )
    )
}
