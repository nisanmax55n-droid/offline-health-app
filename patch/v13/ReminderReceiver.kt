package il.co.offlinehealth

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val type = intent.getStringExtra(ReminderScheduler.EXTRA_TYPE) ?: return
        showNotification(context, type)
        if (type != "test") ReminderScheduler.rescheduleAfterFire(context, type)
    }

    companion object {
        fun sendTest(context: Context) = showNotification(context, "test")

        fun showNotification(context: Context, type: String) {
            if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val channelId = "nutrition_reminders"
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val channel = NotificationChannel(channelId, "אפרת רביבו – תזכורות תזונה", NotificationManager.IMPORTANCE_HIGH).apply {
                    description = "תזכורות אישיות לאוכל ולשתייה"
                    enableVibration(true)
                    setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION), null)
                }
                nm.createNotificationChannel(channel)
            }
            val openIntent = Intent(context, MainActivity::class.java)
            val contentIntent = PendingIntent.getActivity(context, 9001, openIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val pair = when(type) {
                "breakfast" -> "☀️ הגיע הזמן לארוחת בוקר" to "כדאי לעצור, לאכול בצורה מסודרת ולרשום את הארוחה ביומן."
                "lunch" -> "🥗 הגיע הזמן לארוחת צהריים" to "הגיע הזמן לארוחה שתעזור לך להתקדם ליעד היומי שלך."
                "dinner" -> "🌙 הגיע הזמן לארוחת ערב" to "אפשר לסגור את היום עם ארוחה מסודרת שמתאימה ליעדים שלך."
                "snack" -> "🍎 זמן לנשנוש שתכננת" to "אם זה מתאים לתוכנית שלך, זה הזמן לנשנוש מתוכנן."
                "test" -> "🔔 בדיקת התראה – אפרת רביבו" to "הכול עובד. ההתראות האישיות מוכנות לפעולה."
                else -> "💧 הגיע הזמן לשתות מים" to "שתו עכשיו מים וסמנו אותם באפליקציה כדי להמשיך לעקוב."
            }
            val n = NotificationCompat.Builder(context, channelId)
                .setSmallIcon(android.R.drawable.ic_popup_reminder)
                .setContentTitle(pair.first)
                .setContentText(pair.second)
                .setStyle(NotificationCompat.BigTextStyle().bigText(pair.second))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_REMINDER)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setAutoCancel(true)
                .setVibrate(longArrayOf(0, 250, 120, 250))
                .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
                .setContentIntent(contentIntent)
                .build()
            nm.notify(type.hashCode(), n)
        }
    }
}

class ReminderBootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if ((intent.action == Intent.ACTION_BOOT_COMPLETED || intent.action == Intent.ACTION_MY_PACKAGE_REPLACED) && ReminderScheduler.isConfigured(context)) {
            ReminderScheduler.scheduleAll(context)
        }
    }
}
