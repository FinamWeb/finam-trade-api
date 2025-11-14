package example.ws

import example.FINAM_SECRET_KEY
import kotlinx.coroutines.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.Action
import ru.finam.tradeapi.WebsocketClient
import ru.finam.tradeapi.WsRequest
import ru.finam.tradeapi.isHandshake
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds


abstract class WsSubscriptionBaseExample {
    private val logger: Logger = LoggerFactory.getLogger(this::class.java)

    fun run(
        subscribeRequest: WsRequest,
        duration: Duration = 30.seconds,
        withAuthorizationHeader: Boolean = true,
        onMessage: (String) -> Unit
    ) = runBlocking {
        val secret = System.getenv(FINAM_SECRET_KEY)
        if (secret.isNullOrEmpty()) {
            throw IllegalStateException("$FINAM_SECRET_KEY env is not set")
        }
        val unsubscribeRequest = subscribeRequest.copy(action = Action.UNSUBSCRIBE)

        val client = WebsocketClient()
        val handshakeReceived = CompletableDeferred<Unit>()

        val session = client.connect(secret = secret, withAuthorizationHeader = withAuthorizationHeader)

        val job = CoroutineScope(Dispatchers.IO).launch {
            session.incoming.collect { message ->
                if (isHandshake(message)) {
                    handshakeReceived.complete(Unit)
                } else {
                    onMessage(message)
                }
            }
        }

        try {
            withTimeout(20_000) { handshakeReceived.await() }
            logger.info("Handshake received")
            session.send(subscribeRequest)
            delay(duration)
            session.send(unsubscribeRequest)
        } catch (ex: Exception) {
            when (ex) {
                is TimeoutCancellationException -> logger.error("Handshake failed: {}", ex.toString())
                else -> logger.error("Websocket error: {}", ex.toString())
            }
        } finally {
            session.close.invoke()
            job.cancelAndJoin()
        }
    }

}