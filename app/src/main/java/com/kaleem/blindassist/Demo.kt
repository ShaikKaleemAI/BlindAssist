package com.kaleem.blindassist

import kotlin.math.abs

/**
 * SIMULATED scenarios for demonstrations and regression tests. They feed synthetic detections (with known true distance)
 * through the REAL ranging -> tracking -> alert pipeline, so a committee can hear what the app says without a trained model,
 * a street, or a phone in a pocket. Everything here is simulation: it shows behaviour, NOT real-world accuracy.
 */
class DemoScenario(val id: String, val title: String, val rows: List<TapeRow>) {
    val durationS: Double get() = rows.maxOfOrNull { it.t } ?: 0.0
}

class DemoSummary(val speechCount: Int, val firstAlertT: Double?, val firstAlertTrueZ: Double?,
                  val firstCriticalT: Double?, val firstCriticalTrueZ: Double?)

object DemoScenarios {
    private const val FW = 640.0
    private const val FH = 480.0
    private val cam = Cam(60.0, 1.10, 0.0)

    private fun row(t: Double, label: String, z: Double, x: Double, w: Double, h: Double): TapeRow {
        val fx = cam.fx(FW)
        val bw = fx * w / z; val bh = fx * h / z
        val y2 = FH / 2 + fx * cam.heightM / z                      // ground contact row for a camera at 1.10 m, pitch 0
        val cx = FW / 2 + fx * x / z
        return TapeRow(t, FW, FH, 0.0, label, doubleArrayOf(cx - bw / 2, y2 - bh, cx + bw / 2, y2), 0.9, z)
    }

    private fun approach(label: String, z0: Double, z1: Double, speed: Double, x: Double, w: Double, h: Double): List<TapeRow> {
        val out = ArrayList<TapeRow>(); var i = 0
        while (true) {
            val t = i * 0.1; val z = z0 - speed * t
            if (z < z1) break
            out += row(t, label, z, x, w, h); i++
        }
        return out
    }

    fun all(): List<DemoScenario> {
        val p = Cfg.DIMS["person"]!!; val c = Cfg.DIMS["car"]!!; val pole = Cfg.DIMS["pole"]!!
        return listOf(
            DemoScenario("person", "Person walking toward you", approach("person", 6.0, 0.9, 1.1, 0.0, p.w, p.h)),
            DemoScenario("car", "Car approaching fast", approach("car", 14.0, 2.0, 4.0, 0.0, c.w, c.h)),
            DemoScenario("pole", "Pole just ahead on the left", approach("pole", 5.0, 1.3, 1.0, -0.2, pole.w, pole.h)),
            DemoScenario("stairs", "Stairs ahead (ground hazard)", approach("stairs", 6.0, 1.8, 1.1, 0.0, 1.2, 0.25)))
    }
}

object DemoRunner {
    fun run(s: DemoScenario, lang: String = "en"): ReplayResult = ReplayRunner.run(s.rows, 60.0, 1.10, lang)

    fun summarize(s: DemoScenario, r: ReplayResult): DemoSummary {
        fun trueZAt(t: Double) = s.rows.minByOrNull { abs(it.t - t) }?.trueZ
        val first = r.events.firstOrNull { it.second is Ev.Speech }
        val crit = r.events.firstOrNull { (it.second as? Ev.Speech)?.pri == P_CRITICAL }
        return DemoSummary(r.speech, first?.first, first?.let { trueZAt(it.first) }, crit?.first, crit?.let { trueZAt(it.first) })
    }
}

enum class CheckStatus { PASS, WARN, FAIL }
class Check(val name: String, val status: CheckStatus, val detail: String)

/** Pure formatting of the on-device readiness check. Never says the user or route is "safe" or "ready to walk". */
object SelfTestReport {
    fun counts(c: List<Check>) = Triple(c.count { it.status == CheckStatus.PASS }, c.count { it.status == CheckStatus.WARN }, c.count { it.status == CheckStatus.FAIL })

    fun text(c: List<Check>): String = c.joinToString("\n") { "[${it.status}] ${it.name}: ${it.detail}" }

    fun spoken(c: List<Check>): String {
        val (p, w, f) = counts(c)
        val worst = c.firstOrNull { it.status == CheckStatus.FAIL } ?: c.firstOrNull { it.status == CheckStatus.WARN }
        return "Check finished. $p passed, $w warnings, $f failed." + (worst?.let { " First issue: ${it.name}. ${it.detail}" } ?: "") +
            " This check does not mean the way is safe. Keep using your cane."
    }
}
