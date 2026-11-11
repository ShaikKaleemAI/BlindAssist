package com.kaleem.blindassist

import org.junit.After
import org.junit.Assert.*
import org.junit.Test

class DemoTest {
    @After fun reset() = Cfg.resetAblation()

    @Test fun scenariosExistAndAreOrdered() {
        val all = DemoScenarios.all()
        assertTrue(all.size >= 4); assertEquals(all.size, all.map { it.id }.toSet().size)
        for (s in all) {
            assertTrue(s.id, s.rows.size > 10)
            assertTrue(s.rows.zipWithNext().all { (a, b) -> a.t < b.t })
            assertTrue(s.rows.all { it.trueZ != null && it.trueZ > 0 })
        }
    }

    @Test fun everyScenarioProducesAnAlertBeforeContact() {
        for (s in DemoScenarios.all()) {
            val r = DemoRunner.run(s); val sum = DemoRunner.summarize(s, r)
            assertTrue("${s.id}: no speech alert", sum.speechCount > 0)
            assertTrue("${s.id}: first alert at true z=${sum.firstAlertTrueZ}", sum.firstAlertTrueZ!! >= 1.0)
        }
    }

    @Test fun scenariosAreDeterministic() {
        val s = DemoScenarios.all()[0]
        assertEquals(DemoRunner.run(s).speech, DemoRunner.run(s).speech)
    }

    @Test fun selfTestReportNeverClaimsSafe() {
        val c = listOf(Check("Camera", CheckStatus.PASS, "ok"), Check("Detector", CheckStatus.FAIL, "no model"), Check("Languages", CheckStatus.WARN, "x"))
        val t = SelfTestReport.spoken(c).lowercase()
        assertTrue(t.contains("1 passed, 1 warnings, 1 failed")); assertTrue(t.contains("detector"))
        assertTrue(t.contains("does not mean the way is safe")); assertFalse(t.contains("ready to walk")); assertFalse(t.contains("path is clear"))
        assertEquals(Triple(1, 1, 1), SelfTestReport.counts(c))
    }
}
