package com.example.celestialsanctuary

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import com.example.celestialsanctuary.navigation.NavGraph
import com.example.celestialsanctuary.ui.theme.CelestialSanctuaryTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            CelestialSanctuaryTheme {
                val navController = rememberNavController()
                NavGraph(navController = navController)
            }
        }
    }
}
