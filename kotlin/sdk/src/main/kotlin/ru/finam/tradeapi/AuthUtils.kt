package ru.finam.tradeapi

import grpc.tradeapi.v1.auth.*
import io.grpc.ManagedChannel


fun authServiceStub(channel: ManagedChannel): AuthServiceGrpcKt.AuthServiceCoroutineStub =
    AuthServiceGrpcKt.AuthServiceCoroutineStub(channel)

suspend fun AuthServiceGrpcKt.AuthServiceCoroutineStub.auth(secret: String): AuthResponse =
    auth(AuthRequest.newBuilder().setSecret(secret).build())

suspend fun AuthServiceGrpcKt.AuthServiceCoroutineStub.tokenDetails(token: String): TokenDetailsResponse =
    tokenDetails(
        TokenDetailsRequest.newBuilder()
            .setToken(token)
            .build()
    )

fun AuthServiceGrpcKt.AuthServiceCoroutineStub.subscribeJwtRenewal(secret: String) =
    subscribeJwtRenewal(
        SubscribeJwtRenewalRequest.newBuilder()
            .setSecret(secret)
            .build()
    )

