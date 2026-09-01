package il.co.offlinehealth

import android.Manifest
import android.app.TimePickerDialog
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class ReminderSettingsActivity : AppCompatActivity() {
    private val prefs by lazy { getSharedPreferences(ReminderScheduler.PREFS, Context.MODE_PRIVATE) }
    private val mealRows = mutableListOf<MealRow>()
    private lateinit var master: Switch
    private lateinit var waterEnabled: Switch
    private lateinit var waterInterval: Spinner
    private lateinit var waterStart: Button
    private lateinit var waterEnd: Button

    data class MealRow(val reminder: ReminderScheduler.DailyReminder, val enabled: Switch, val time: Button)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        title = "תזכורות אישיות"
        val scroll = ScrollView(this)
        val body = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = View.LAYOUT_DIRECTION_RTL
            setPadding(dp(20), dp(20), dp(20), dp(32))
            setBackgroundColor(Color.rgb(247,250,248))
        }
        scroll.addView(body)

        body.addView(titleText("🔔 תזכורות אישיות"))
        body.addView(subText("בחרו מתי אפרת רביבו תזכיר לאכול ולשתות. ההתראות מקומיות, עם צליל ורטט, ועובדות גם בלי אינטרנט."))

        master = Switch(this).apply {
            text = "הפעלת תזכורות"
            textSize = 18f
            isChecked = prefs.getBoolean("master_enabled", false)
            gravity = Gravity.RIGHT
            setPadding(0, dp(14), 0, dp(14))
        }
        body.addView(master)

        body.addView(section("תזכורות לארוחות"))
        ReminderScheduler.meals.forEach { item ->
            val label = when(item.type){"breakfast"->"☀️ ארוחת בוקר";"lunch"->"🥗 ארוחת צהריים";"dinner"->"🌙 ארוחת ערב";else->"🍎 נשנוש"}
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                layoutDirection = View.LAYOUT_DIRECTION_RTL
                setPadding(dp(12), dp(10), dp(12), dp(10))
                setBackgroundColor(Color.WHITE)
            }
            val sw = Switch(this).apply {
                text = label
                textSize = 16f
                isChecked = prefs.getBoolean(item.enabledKey, false)
                gravity = Gravity.RIGHT
            }
            val b = Button(this).apply {
                isAllCaps = false
                text = formatTime(prefs.getInt(item.hourKey,item.defHour), prefs.getInt(item.minuteKey,item.defMinute))
                setOnClickListener { pickTime(item.hourKey,item.minuteKey,this,item.defHour,item.defMinute) }
            }
            row.addView(sw, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
            row.addView(b, LinearLayout.LayoutParams(dp(110), LinearLayout.LayoutParams.WRAP_CONTENT))
            body.addView(row, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply{setMargins(0,0,0,dp(8))})
            mealRows.add(MealRow(item, sw, b))
        }

        body.addView(section("תזכורות לשתייה"))
        waterEnabled = Switch(this).apply {
            text = "💧 תזכורות מים"
            textSize = 16f
            isChecked = prefs.getBoolean("water_enabled", false)
            gravity = Gravity.RIGHT
        }
        body.addView(waterEnabled)
        body.addView(TextView(this).apply { text = "מרווח בין תזכורות"; textSize=15f; gravity=Gravity.RIGHT; setPadding(0,dp(12),0,dp(6)) })
        waterInterval = Spinner(this)
        val intervalValues = listOf("כל 30 דקות","כל 60 דקות","כל 90 דקות","כל 120 דקות")
        waterInterval.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, intervalValues)
        val current = prefs.getInt("water_interval",60)
        waterInterval.setSelection(when(current){30->0;60->1;90->2;else->3})
        body.addView(waterInterval)

        val window = LinearLayout(this).apply { orientation=LinearLayout.HORIZONTAL; gravity=Gravity.CENTER; layoutDirection=View.LAYOUT_DIRECTION_RTL; setPadding(0,dp(12),0,0) }
        waterStart = Button(this).apply {
            isAllCaps=false
            text="התחלה ${formatTime(prefs.getInt("water_start_hour",8),prefs.getInt("water_start_min",0))}"
            setOnClickListener { pickTime("water_start_hour","water_start_min",this,8,0,"התחלה ") }
        }
        waterEnd = Button(this).apply {
            isAllCaps=false
            text="סיום ${formatTime(prefs.getInt("water_end_hour",22),prefs.getInt("water_end_min",0))}"
            setOnClickListener { pickTime("water_end_hour","water_end_min",this,22,0,"סיום ") }
        }
        window.addView(waterStart, LinearLayout.LayoutParams(0,LinearLayout.LayoutParams.WRAP_CONTENT,1f))
        window.addView(waterEnd, LinearLayout.LayoutParams(0,LinearLayout.LayoutParams.WRAP_CONTENT,1f))
        body.addView(window)

        val save = Button(this).apply {
            text = "שמירת התזכורות"
            isAllCaps = false
            textSize = 17f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.rgb(13,126,104))
            setPadding(dp(12),dp(14),dp(12),dp(14))
            setOnClickListener { saveAll() }
        }
        body.addView(save, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT).apply{setMargins(0,dp(24),0,0)})

        val test = Button(this).apply {
            text = "🔔 בדיקת התראה עכשיו"
            isAllCaps = false
            textSize = 16f
            setOnClickListener {
                requestNotificationPermissionIfNeeded()
                if (Build.VERSION.SDK_INT < 33 || ContextCompat.checkSelfPermission(this@ReminderSettingsActivity, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
                    ReminderReceiver.sendTest(this@ReminderSettingsActivity)
                } else Toast.makeText(this@ReminderSettingsActivity,"יש לאשר התראות ואז ללחוץ שוב על הבדיקה",Toast.LENGTH_LONG).show()
            }
        }
        body.addView(test, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT).apply{setMargins(0,dp(10),0,0)})

        body.addView(subText("Android עשוי להזיז תזכורת בכמה דקות כדי לחסוך בסוללה. אין צורך בחיבור לאינטרנט. התזכורות נשמרות במכשיר ונטענות מחדש אחרי אתחול."))
        setContentView(scroll)
    }

    private fun saveAll() {
        val e = prefs.edit().putBoolean("configured", true).putBoolean("master_enabled", master.isChecked).putBoolean("water_enabled", waterEnabled.isChecked)
        mealRows.forEach { e.putBoolean(it.reminder.enabledKey, it.enabled.isChecked) }
        val mins = when(waterInterval.selectedItemPosition){0->30;1->60;2->90;else->120}
        e.putInt("water_interval", mins).apply()
        requestNotificationPermissionIfNeeded()
        ReminderScheduler.scheduleAll(this)
        Toast.makeText(this,"התזכורות נשמרו",Toast.LENGTH_SHORT).show()
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 7001)
        }
    }

    private fun pickTime(hourKey:String, minKey:String, button:Button, defHour:Int, defMin:Int, prefix:String="") {
        val h=prefs.getInt(hourKey,defHour); val m=prefs.getInt(minKey,defMin)
        TimePickerDialog(this,{_,hh,mm-> prefs.edit().putInt(hourKey,hh).putInt(minKey,mm).apply(); button.text=prefix+formatTime(hh,mm)},h,m,true).show()
    }

    private fun formatTime(h:Int,m:Int)=String.format("%02d:%02d",h,m)
    private fun section(t:String)=TextView(this).apply{text=t;textSize=20f;setTextColor(Color.rgb(20,56,49));gravity=Gravity.RIGHT;setPadding(0,dp(22),0,dp(10));setTypeface(typeface,1)}
    private fun titleText(t:String)=TextView(this).apply{text=t;textSize=28f;setTextColor(Color.rgb(18,44,39));gravity=Gravity.RIGHT;setTypeface(typeface,1)}
    private fun subText(t:String)=TextView(this).apply{text=t;textSize=14f;setTextColor(Color.rgb(92,108,104));gravity=Gravity.RIGHT;setPadding(0,dp(8),0,dp(8))}
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
}
