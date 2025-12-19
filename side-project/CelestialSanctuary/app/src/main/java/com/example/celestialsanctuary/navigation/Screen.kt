package com.example.celestialsanctuary.navigation

sealed class Screen(val route: String) {
    data object Opening : Screen("opening")
    data object Onboarding : Screen("onboarding")
    data object Hall : Screen("hall")
    data object House : Screen("house/{houseIndex}") {
        fun createRoute(houseIndex: Int) = "house/$houseIndex"
    }
    data object Fortune : Screen("fortune")
    data object WeeklyFortune : Screen("weekly_fortune")
    data object MonthlyFortune : Screen("monthly_fortune")
    data object Settings : Screen("settings")
}
