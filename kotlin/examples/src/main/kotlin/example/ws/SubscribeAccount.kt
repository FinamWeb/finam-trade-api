package example.ws

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.MessageType
import ru.finam.tradeapi.SubscriptionType
import ru.finam.tradeapi.WsRequest
import ru.finam.tradeapi.parseEnv

object SubscribeAccount : WsSubscriptionBaseExample() {
    private val logger: Logger = LoggerFactory.getLogger(SubscribeAccount::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val accountId = "your-account-id"
        val subscribeRequest = WsRequest.subscribeAccountRequest(accountId)
        run(subscribeRequest) { message ->
            val envelope = parseEnv(message) ?: throw RuntimeException("Failed to parse envelope $message")

            when (envelope.type) {
                MessageType.DATA -> {
                    if (envelope.subscriptionType == SubscriptionType.ACCOUNT) {
                        logger.info("Received account info: \n {}", message)
                    }
                }

                MessageType.EVENT -> logger.info("Event received: ${envelope.eventInfo}")
                MessageType.ERROR -> logger.error("Error received: ${envelope.errorInfo}")
            }
        }
    }

}