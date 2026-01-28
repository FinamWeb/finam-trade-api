package example.ws

import grpc.tradeapi.v1.marketdata.SubscribeQuoteResponse
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.*

object SubscribeQuotes : WsSubscriptionBaseExample() {
    private val logger: Logger = LoggerFactory.getLogger(SubscribeQuotes::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val symbols = listOf("SBERF@RTSX", "OKEY@MISX")

        val subscribeRequest = WsRequest.subscribeQuotesRequest(symbols)

        run(subscribeRequest) { message ->
            val envelope = parseEnv(message) ?: throw RuntimeException("Failed to parse envelope $message")

            when (envelope.type) {
                MessageType.DATA -> {
                    if (envelope.subscriptionType == SubscriptionType.QUOTES) {
                        val quotesResponse: SubscribeQuoteResponse? = parseProto(
                            message,
                            { SubscribeQuoteResponse.newBuilder() })
                        if (quotesResponse == null) {
                            logger.error("Failed to deserialize quotes: ${envelope.payload}")
                        } else {
                            logger.info("Received quotes: \n {}", quotesResponse)
                        }
                    }
                }

                MessageType.EVENT -> logger.info("Event received: ${envelope.eventInfo}")
                MessageType.ERROR -> logger.error("Error received: ${envelope.errorInfo}")
            }
        }
    }

}