package example.ws

import grpc.tradeapi.v1.marketdata.SubscribeOrderBookResponse
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.*

object SubscribeOrderBook : WsSubscriptionBaseExample() {
    private val logger: Logger = LoggerFactory.getLogger(SubscribeOrderBook::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val symbol = "SBERF@RTSX"
        val subscribeRequest = WsRequest.subscribeOrderBookRequest(symbol)
        run(subscribeRequest) { message ->
            val envelope = parseEnv(message) ?: throw RuntimeException("Failed to parse envelope $message")

            when (envelope.type) {
                MessageType.DATA -> {
                    if (envelope.subscriptionType == SubscriptionType.ORDER_BOOK) {
                        val orderBookResponse: SubscribeOrderBookResponse? = parseProto(
                            message,
                            { SubscribeOrderBookResponse.newBuilder() })
                        if (orderBookResponse == null) {
                            logger.error("Failed to deserialize books: ${envelope.payload}")
                        } else {
                            logger.info("Received orderbook: \n {}", orderBookResponse)
                        }
                    }
                }

                MessageType.EVENT -> logger.info("Event received: ${envelope.eventInfo}")
                MessageType.ERROR -> logger.error("Error received: ${envelope.errorInfo}")
            }
        }
    }

}