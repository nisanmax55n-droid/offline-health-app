package il.co.offlinehealth

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import java.util.Calendar

object ReminderScheduler {
    const val PREFS = "nutrition_reminders"
    const val EXTRA_TYPE = "reminder_type"

    data class DailyReminder(val type:String, val enabledKey:String, val hourKey:String, val minuteKey:String, val defHour:Int, val defMinute:Int)

    val meals = listOf(
        DailyReminder("breakfast", "breakfast_enabled", "breakfast_hour", "breakfast_min", 8, 30),
        DailyReminder("lunch", "lunch_enabled", "lunch_hour", "lunch_min", 13, 0),
        DailyReminder("dinner", "dinner_enabled", "dinner_hour", "dinner_min", 19, 0),
        DailyReminder("snack", "snack_enabled", "snack_hour", "snack_min", 16, 30)
    )

    fun isConfigured(context: Context): Boolean = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean("configured", false)

    fun scheduleAll(context: Context) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (!prefs.getBoolean("configured", false) || !prefs.getBoolean("master_enabled", false)) {
            cancelAll(context)
            return
        }
        meals.forEach { item ->
            if (prefs.getBoolean(item.enabledKey, false)) scheduleDaily(context, item)
            else cancel(context, item.type)
        }
        if (prefs.getBoolean("water_enabled", false)) scheduleNextWater(context)
        else cancel(context, "water")
    }

    fun scheduleDaily(context: Context, item: DailyReminder) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val hour = prefs.getInt(item.hourKey, item.defHour)
        val minute = prefs.getInt(item.minuteKey, item.defMinute)
        val now = Calendar.getInstance()
        val trigger = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
            if (!after(now)) add(Calendar.DAY_OF_YEAR, 1)
        }
        setAlarm(context, item.type, trigger.timeInMillis)
    }

    fun scheduleNextWater(context: Context) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (!prefs.getBoolean("configured", false) || !prefs.getBoolean("master_enabled", false) || !prefs.getBoolean("water_enabled", false)) {
            cancel(context, "water")
            return
        }
        val intervalMin = prefs.getInt("water_interval", 60).coerceIn(30, 240)
        val startHour = prefs.getInt("water_start_hour", 8)
        val startMinute = prefs.getInt("water_start_min", 0)
        val endHour = prefs.getInt("water_end_hour", 22)
        val endMinute = prefs.getInt("water_end_min", 0)
        val now = Calendar.getInstance()
        val candidate = (now.clone() as Calendar).apply { add(Calendar.MINUTE, intervalMin) }
        val startToday = (candidate.clone() as Calendar).apply {
            set(Calendar.HOUR_OF_DAY, startHour); set(Calendar.MINUTE, startMinute); set(Calendar.SECOND,0); set(Calendar.MILLISECOND,0)
        }
        val endToday = (candidate.clone() as Calendar).apply {
            set(Calendar.HOUR_OF_DAY, endHour); set(Calendar.MINUTE, endMinute); set(Calendar.SECOND,0); set(Calendar.MILLISECOND,0)
        }
        if (candidate.before(startToday)) candidate.timeInMillis = startToday.timeInMillis
        if (candidate.after(endToday)) {
            candidate.timeInMillis = startToday.timeInMillis
            candidate.add(Calendar.DAY_OF_YEAR, 1)
        }
        setAlarm(context, "water", candidate.timeInMillis)
    }

    fun rescheduleAfterFire(context: Context, type: String) {
        if (type == "water") scheduleNextWater(context)
        else meals.firstOrNull { it.type == type }?.let { scheduleDaily(context, it) }
    }

    private fun setAlarm(context: Context, type: String, atMillis: Long) {
        val am = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val pi = pending(context, type)
        am.cancel(pi)
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, atMillis, pi)
    }

    fun cancelAll(context: Context) {
        meals.forEach { cancel(context, it.type) }
        cancel(context, "water")
    }

    fun cancel(context: Context, type: String) {
        val am = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        am.cancel(pending(context, type))
    }

    private fun pending(context: Context, type: String): PendingIntent {
        val intent = Intent(context, ReminderReceiver::class.java).putExtra(EXTRA_TYPE, type)
        return PendingIntent.getBroadcast(
            context,
            type.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }
}
