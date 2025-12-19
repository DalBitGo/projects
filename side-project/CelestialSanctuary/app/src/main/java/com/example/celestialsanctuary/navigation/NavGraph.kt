package com.example.celestialsanctuary.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.example.celestialsanctuary.ui.screen.fortune.DailyFortuneScreen
import com.example.celestialsanctuary.ui.screen.hall.HouseHallScreen
import com.example.celestialsanctuary.ui.screen.house.HouseRoomScreen
import com.example.celestialsanctuary.ui.screen.onboarding.OnboardingScreen
import com.example.celestialsanctuary.ui.screen.opening.OpeningScreen
import com.example.celestialsanctuary.ui.screen.monthly.MonthlyFortuneScreen
import com.example.celestialsanctuary.ui.screen.settings.SettingsScreen
import com.example.celestialsanctuary.ui.screen.weekly.WeeklyFortuneScreen

@Composable
fun NavGraph(
    navController: NavHostController,
    startDestination: String = Screen.Opening.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(route = Screen.Opening.route) {
            OpeningScreen(
                onNavigateToHall = {
                    navController.navigate(Screen.Hall.route) {
                        popUpTo(Screen.Opening.route) { inclusive = true }
                    }
                },
                onNavigateToOnboarding = {
                    navController.navigate(Screen.Onboarding.route) {
                        popUpTo(Screen.Opening.route) { inclusive = true }
                    }
                }
            )
        }

        composable(route = Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = {
                    navController.navigate(Screen.Hall.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }

        composable(route = Screen.Hall.route) {
            HouseHallScreen(
                onHouseClick = { houseIndex ->
                    navController.navigate(Screen.House.createRoute(houseIndex))
                },
                onFortuneClick = {
                    navController.navigate(Screen.Fortune.route)
                },
                onWeeklyFortuneClick = {
                    navController.navigate(Screen.WeeklyFortune.route)
                },
                onMonthlyFortuneClick = {
                    navController.navigate(Screen.MonthlyFortune.route)
                },
                onSettingsClick = {
                    navController.navigate(Screen.Settings.route)
                }
            )
        }

        composable(route = Screen.Fortune.route) {
            DailyFortuneScreen(
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(route = Screen.Settings.route) {
            SettingsScreen(
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(route = Screen.WeeklyFortune.route) {
            WeeklyFortuneScreen(
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(route = Screen.MonthlyFortune.route) {
            MonthlyFortuneScreen(
                onBackClick = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.House.route,
            arguments = listOf(
                navArgument("houseIndex") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val houseIndex = backStackEntry.arguments?.getInt("houseIndex") ?: 1
            HouseRoomScreen(
                houseIndex = houseIndex,
                onBackClick = { navController.popBackStack() }
            )
        }
    }
}
