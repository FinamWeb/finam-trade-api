package example.ws

import grpc.tradeapi.v1.marketdata.SubscribeLatestTradesResponse
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.*

object SubscribeLatestTrades : WsSubscriptionBaseExample() {
    private val logger: Logger = LoggerFactory.getLogger(SubscribeLatestTrades::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val symbol = "SBERF@RTSX"
        val subscribeRequest = WsRequest.subscribeLatestTradesRequest(symbol)
        run(subscribeRequest) { message ->
            val envelope = parseEnv(message) ?: throw RuntimeException("Failed to parse envelope $message")

            when (envelope.type) {
                MessageType.DATA -> {
                    if (envelope.subscriptionType == SubscriptionType.INSTRUMENT_TRADES) {
                        val latestTradesResponse: SubscribeLatestTradesResponse? = parseProto(
                            message,
                            { SubscribeLatestTradesResponse.newBuilder() })
                        if (latestTradesResponse == null) {
                            logger.error("Failed to deserialize trades: ${envelope.payload}")
                        } else {
                            logger.info("Received latest trades response: \n {}", latestTradesResponse)
                        }
                    }
                }

                MessageType.EVENT -> logger.info("Event received: ${envelope.eventInfo}")
                MessageType.ERROR -> logger.error("Error received: ${envelope.errorInfo}")
            }
        }
    }

}