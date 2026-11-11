package com.kaleem.blindassist

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import androidx.core.content.ContextCompat

/** Plays a simulated scenario through the real audio path (speech + stereo beeps + vibration). Not live sensing. */
class DemoPlayer(private val ctx: Context, private val lang: String, private val onDone: () -> Unit) {
    private val main = Handler(Looper.getMainLooper())
    private var speech: Speech? = null
    private var ear: Earcons? = null

    fun play(s: DemoScenario) {
        val res = DemoRunner.run(s, lang)
        speech = Speech(ctx, lang); ear = Earcons()
        speech?.say("Simulated scenario. ${s.title}. This is not live sensing.", P_ANSWER, 30.0, "demo-intro")
        val lead = 5000L
        for ((t, e) in res.events) main.postDelayed({
            when (e) {
                is Ev.Speech -> speech?.say(e.text, e.pri, e.ttl, e.key)
                is Ev.Beep -> ear?.beep(e.pan, e.freq, e.dur)
                Ev.Vibrate -> vibrateOnce(ctx)
            }
        }, lead + (t * 1000).toLong())
        main.postDelayed({ stop(); onDone() }, lead + ((s.durationS + 4.0) * 1000).toLong())
    }

    fun stop() { main.removeCallbacksAndMessages(null); speech?.shutdown(); ear?.shutdown(); speech = null; ear = null }
}

/** Collects real facts about this phone/app for the readiness check. Every status here is a measurement of THIS install. */
object SelfTest {
    @Suppress("DEPRECATION")
    fun run(ctx: Context): List<Check> {
        val out = ArrayList<Check>()
        val pm = ctx.packageManager
        out += if (pm.hasSystemFeature(PackageManager.FEATURE_CAMERA_ANY)) Check("Camera", CheckStatus.PASS, "camera hardware present")
               else Check("Camera", CheckStatus.FAIL, "no camera")
        out += if (ContextCompat.checkSelfPermission(ctx, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED)
            Check("Camera permission", CheckStatus.PASS, "granted") else Check("Camera permission", CheckStatus.WARN, "not granted yet; it is requested when you press Start")
        val sm = ctx.getSystemService(Context.SENSOR_SERVICE) as SensorManager
        val hasTilt = sm.getDefaultSensor(Sensor.TYPE_GRAVITY) != null || sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER) != null
        out += if (hasTilt) Check("Tilt sensor", CheckStatus.PASS, "gravity/accelerometer present") else Check("Tilt sensor", CheckStatus.FAIL, "no tilt sensor: distance cannot be estimated")
        val files = try { ctx.assets.list("models")?.toSet() ?: emptySet() } catch (e: Exception) { emptySet() }
        out += when {
            "hazard_yolo_int8.tflite" in files && "hazard_labels.txt" in files -> Check("Detector", CheckStatus.PASS, "custom hazard model present (accuracy depends on its evaluation report)")
            "efficientdet_lite0.tflite" in files -> Check("Detector", CheckStatus.WARN, "COCO model only: no stairs, drops, potholes, drains or glass detection")
            else -> Check("Detector", CheckStatus.FAIL, "no model: limited mode, the app cannot see obstacles")
        }
        val pw = ctx.getSystemService(Context.POWER_SERVICE) as PowerManager
        out += if (pw.isIgnoringBatteryOptimizations(ctx.packageName)) Check("Battery optimisation", CheckStatus.PASS, "exempt")
               else Check("Battery optimisation", CheckStatus.WARN, "not exempt: the phone may stop the app with the screen off")
        if (Build.VERSION.SDK_INT >= 33) out += if (ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED)
            Check("Notifications", CheckStatus.PASS, "granted") else Check("Notifications", CheckStatus.WARN, "not granted: the running notice may be hidden")
        val perms = try { pm.getPackageInfo(ctx.packageName, PackageManager.GET_PERMISSIONS).requestedPermissions?.toSet() ?: emptySet() } catch (e: Exception) { emptySet() }
        out += if ("android.permission.INTERNET" in perms) Check("Offline claim", CheckStatus.WARN, "this build declares INTERNET (added by a library); verify no data leaves the phone")
               else Check("Offline claim", CheckStatus.PASS, "no INTERNET permission declared in this build")
        out += Check("Languages", CheckStatus.WARN, "Hindi and Telugu are machine-drafted: need native review")
        return out
    }
}
