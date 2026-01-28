package ru.finam.tradeapi

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.google.protobuf.Message
import com.google.protobuf.util.JsonFormat
import com.google.protobuf.util.Timestamps
import grpc.tradeapi.v1.auth.AuthServiceGrpcKt
import grpc.tradeapi.v1.marketdata.TimeFrame
import io.grpc.ManagedChannelBuilder
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.websocket.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.time.Instant
import java.util.*
import kotlin.properties.Delegates

val logger: Logger = LoggerFactory.getLogger("ru.finam.tradeapi.WebSocket.kt")
val mapper: ObjectMapper = ObjectMapper().apply {
    disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
    registerModule(KotlinModule.Builder().build())
    registerModule(JavaTimeModule())
}

class WebsocketClient(
    private val defaultClientOptions: ClientOptions = defaultClientOptions(),
    parentScope: CoroutineScope? = null
) {
    private val client = HttpClient(CIO) {
        install(WebSockets)
    }
    private val scope = parentScope ?: CoroutineScope(Dispatchers.IO)
    private var authStub: AuthServiceGrpcKt.AuthServiceCoroutineStub by Delegates.notNull<AuthServiceGrpcKt.AuthServiceCoroutineStub>()
    private var token: String? = null
    private var tokenRenewalJob: Job? = null

    suspend fun connect(
        host: String = defaultClientOptions.host,
        port: Int = defaultClientOptions.port,
        endpoint: String = defaultClientOptions.endpoint,
        secret: String = defaultClientOptions.secret,
        timeout: Long = defaultClientOptions.connectionTimeout,
        withAuthorizationHeader: Boolean = true
    ): WsSession {
        authStub = authServiceStub(ManagedChannelBuilder.forAddress(host, port).build())
        try {
            token = withTimeout(timeout) { authStub.auth(secret).token }
            logger.debug("Auth token received")
            tokenRenewalJob = startTokenRenewal(secret)
        } catch (ex: Exception) {
            logger.error("Failed to get auth token: {}", ex.toString())
            throw ex
        }

        try {
            val session = withTimeout(timeout) {
                client.webSocketSession(
                    urlString = "wss://$host:$port$endpoint",
                ) {
                    if (withAuthorizationHeader) {
                        header(HttpHeaders.Authorization, token)
                    }
                }
            }

            logger.info("Websocket connection established")

            val incoming: Flow<String> = channelFlow {
                for (frame in session.incoming) {
                    when (frame) {
                        is Frame.Text -> {
                            val text = frame.readText()
                            logger.trace("Received text frame: {}", text)
                            send(text)
                        }

                        is Frame.Close -> {
                            logger.info("Connection was closed")
                        }

                        else -> logger.error("Unsupported frame type ${frame.frameType}")
                    }
                }
                awaitClose {
                    logger.debug("Incoming message flow closed")
                }
            }

            val send: suspend (WsRequest) -> Unit = { req ->
                if (token == null) {
                    throw IllegalStateException("Authentication token not found")
                }
                session.outgoing.send(Frame.Text(mapper.writeValueAsString(req.copy(token = token!!))))
            }

            val close: suspend () -> Unit = {
                tokenRenewalJob?.cancelAndJoin()
                if (session.isActive) session.close(CloseReason(CloseReason.Codes.NORMAL, "client close"))
                logger.info("Websocket session closed")
            }

            return WsSession(incoming, send, close)

        } catch (ex: Exception) {
            logger.error("Websocket connect failed: {}", ex.toString())
            ex.printStackTrace()
            throw ex
        }

    }

    suspend fun connect(options: ClientOptions) = connect(
        host = options.host,
        port = options.port,
        endpoint = options.endpoint,
        secret = options.secret
    )

    private fun startTokenRenewal(secret: String) = scope.launch {
        logger.debug("Token renewal started")
        authStub.subscribeJwtRenewal(secret).collect {
            token = it.token
            val tokenDetails = authStub.tokenDetails(it.token)
            logger.debug(
                "New auth token received. Expiration: {}",
                Date(Timestamps.toMillis(tokenDetails.expiresAt))
            )
        }
    }

}

private fun defaultClientOptions() = ClientOptions()

data class ClientOptions(
    val host: String = "api.finam.ru",
    val port: Int = 443,
    val endpoint: String = "/ws",
    val secret: String = "",
    val connectionTimeout: Long = 10_000
)

data class WsSession(
    val incoming: Flow<String>,
    val send: suspend (WsRequest) -> Unit,
    val close: suspend () -> Unit
)

data class WsRequest(
    val action: Action,
    val type: SubscriptionType? = null,
    val data: Map<String, Any?>? = null,
    val token: String = ""
) {
    companion object {
        fun subscribeBarsRequest(symbol: String, timeframe: TimeFrame) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.BARS,
            mapOf(
                "symbol" to symbol,
                "timeframe" to timeframe.name
            )
        )

        fun subscribeOrderBookRequest(symbol: String) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.ORDER_BOOK,
            mapOf(
                "symbol" to symbol
            )
        )

        fun subscribeQuotesRequest(symbols: List<String>) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.QUOTES,
            mapOf(
                "symbols" to symbols
            )
        )

        fun subscribeLatestTradesRequest(symbol: String) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.INSTRUMENT_TRADES,
            mapOf(
                "symbol" to symbol
            )
        )

        fun subscribeTradesRequest(accountId: String) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.TRADES,
            mapOf(
                "account_id" to accountId
            )
        )

        fun subscribeOrdersRequest(accountId: String) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.ORDERS,
            mapOf(
                "account_id" to accountId
            )
        )

        fun subscribeAccountRequest(accountId: String) = WsRequest(
            Action.SUBSCRIBE, SubscriptionType.ACCOUNT,
            mapOf(
                "account_id" to accountId
            )
        )
    }
}

data class WsEvent(val event: String, val code: Int, val reason: String)
data class WsError(val code: Int, val type: String, val message: String? = null)

data class WsEnvelope(
    val type: MessageType,
    @param:JsonProperty("subscription_type")
    val subscriptionType: SubscriptionType? = null,
    @param:JsonProperty("subscription_key")
    val subscriptionKey: String? = null,
    val payload: Any? = null,
    @param:JsonProperty("error_info")
    val errorInfo: WsError? = null,
    @param:JsonProperty("event_info")
    val eventInfo: WsEvent? = null,
    val timestamp: Instant
)

data class WsEnvelopeInfo(
    val type: MessageType,
    @param:JsonProperty("error_info") val errorInfo: WsError? = null,
    @param:JsonProperty("event_info") val eventInfo: WsEvent? = null,
)

enum class MessageType {
    DATA, ERROR, EVENT
}

enum class Action {
    SUBSCRIBE, UNSUBSCRIBE, UNSUBSCRIBE_ALL
}

enum class SubscriptionType {
    ORDERS, TRADES, QUOTES, ORDER_BOOK, BARS, INSTRUMENT_TRADES, ACCOUNT
}

inline fun <reified M : Message, B : Message.Builder> parseProto(
    rawJson: String,
    builderSupplier: () -> B,
    field: String = "payload"
): M? {
    val builder = builderSupplier()
    return try {
        mapper.readTree(rawJson).get(field)?.let { node ->
            JsonFormat.parser().ignoringUnknownFields().merge(node.asText(), builder)
            builder.build() as? M
        }
    } catch (_: Exception) {
        logger.error("Failed to parse incoming message: $rawJson")
        null
    }
}

fun parseEnvInfo(message: String): WsEnvelopeInfo? = try {
    mapper.readValue(message, WsEnvelopeInfo::class.java)
} catch (_: Exception) {
    logger.error("Failed to parse envelope info: $message")
    null
}

fun parseEnv(message: String): WsEnvelope? = try {
    mapper.readValue(message, WsEnvelope::class.java)
} catch (_: Exception) {
    logger.error("Failed to parse envelope: $message")
    null
}

fun isHandshake(message: String) = parseEnvInfo(message)
    ?.takeIf { it.type == MessageType.EVENT }?.eventInfo?.let { it.event == "HANDSHAKE_SUCCESS" } ?: false
