package example.ws

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.MessageType
import ru.finam.tradeapi.SubscriptionType
import ru.finam.tradeapi.WsRequest
import ru.finam.tradeapi.parseEnv

object SubscribeTrades : WsSubscriptionBaseExample() {
    private val logger: Logger = LoggerFactory.getLogger(SubscribeTrades::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val accountId = "your-account-id"
        val subscribeRequest = WsRequest.subscribeTradesRequest(accountId)
        run(subscribeRequest) { message ->
            val envelope = parseEnv(message) ?: throw RuntimeException("Failed to parse envelope $message")

            when (envelope.type) {
                MessageType.DATA -> {
                    if (envelope.subscriptionType == SubscriptionType.TRADES) {
                        logger.info("Received trades for account=$accountId: \n {}", message)
                    }
                }

                MessageType.EVENT -> logger.info("Event received: ${envelope.eventInfo}")
                MessageType.ERROR -> logger.error("Error received: ${envelope.errorInfo}")
            }
        }
    }

}