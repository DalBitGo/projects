package com.example.celestialsanctuary.domain.model

enum class HouseState {
    EMPTY,       // 빈 방 - 행성 없음
    TENANT,      // 손님 행성 - 주인이 아닌 행성 있음
    OWNER_HOME   // 집주인 귀환 - 주인 행성이 자신의 집에 있음
}
