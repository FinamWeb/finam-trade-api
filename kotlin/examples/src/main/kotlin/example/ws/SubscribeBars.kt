package example.ws

import grpc.tradeapi.v1.marketdata.SubscribeBarsResponse
import grpc.tradeapi.v1.marketdata.TimeFrame
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import ru.finam.tradeapi.*

object SubscribeBars : WsSubscriptionBaseExample() {
    private val logger: Logger = LoggerFactory.getLogger(SubscribeBars::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val symbol = "SBERF@RTSX"
        val subscribeRequest = WsRequest.subscribeBarsRequest(symbol, TimeFrame.TIME_FRAME_D)

        run(subscribeRequest) { message ->
            val envelope = parseEnv(message) ?: throw RuntimeException("Failed to parse envelope $message")

            when (envelope.type) {
                MessageType.DATA -> {
                    if (envelope.subscriptionType == SubscriptionType.BARS) {
                        val barsResponse: SubscribeBarsResponse? = parseProto(
                            message,
                            { SubscribeBarsResponse.newBuilder() })
                        if (barsResponse == null) {
                            logger.error("Failed to deserialize bars: ${envelope.payload}")
                        } else {
                            logger.info("Received bars: \n {}", barsResponse)
                        }
                    }
                }

                MessageType.EVENT -> logger.info("Event received: ${envelope.eventInfo}")
                MessageType.ERROR -> logger.error("Error received: ${envelope.errorInfo}")
            }
        }
    }

}