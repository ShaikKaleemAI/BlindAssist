package com.kaleem.blindassist

import android.content.Context
import android.view.View
import androidx.test.core.app.ActivityScenario
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

/** Runs on an emulator in CI (.github/workflows/evidence.yml). Smoke level only: it does NOT test vision, audio quality or walking. */
@RunWith(AndroidJUnit4::class)
class SmokeTest {
    private val ctx: Context get() = ApplicationProvider.getApplicationContext()

    @Test fun mainActivityLaunchesAndShowsContent() {
        ActivityScenario.launch(MainActivity::class.java).use {
            it.onActivity { a -> assertNotNull(a.findViewById<View>(android.R.id.content)) }
        }
    }

    @Test fun readinessCheckRunsAndNeverClaimsSafe() {
        val checks = SelfTest.run(ctx)
        assertTrue("expected at least 8 checks, got ${checks.size}", checks.size >= 8)
        val spoken = SelfTestReport.spoken(checks).lowercase()
        assertTrue(spoken.contains("does not mean the way is safe"))
        assertFalse(spoken.contains("path is clear"))
    }

    @Test fun detectorFactoryNeverThrowsAndReportsLimitedModeHonestly() {
        val d = createDetector(ctx)
        val hasModel = ctx.assets.list("models")?.any { it.endsWith(".tflite") } == true
        assertEquals(!hasModel, d.limited)             // no model asset in CI => must be limited mode
        d.close()
    }

    @Test fun everyDemoScenarioProducesAlertsOnDevice() {
        for (s in DemoScenarios.all()) assertTrue(s.id, DemoRunner.summarize(s, DemoRunner.run(s)).speechCount > 0)
    }
}
