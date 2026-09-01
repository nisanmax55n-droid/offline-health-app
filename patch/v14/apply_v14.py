from pathlib import Path


root = Path("health-offline-android")
src = root / "app/src/main/java/il/co/offlinehealth"
main_path = src / "MainActivity.kt"
reminders_path = src / "ReminderSettingsActivity.kt"
ppg_path = src / "PpgActivity.kt"
theme_path = root / "app/src/main/res/values/themes.xml"
gradle_path = root / "app/build.gradle.kts"


def replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"v1.4 design anchor missing: {label}")
    return text.replace(old, new, 1)


s = main_path.read_text()
s = replace(s, "private val teal = Color.rgb(16,124,111)", "private val teal = Color.rgb(0,91,73)", "teal")
s = replace(s, "private val tealDark = Color.rgb(7,86,79)", "private val tealDark = Color.rgb(0,55,45)", "tealDark")
s = replace(s, "private val mint = Color.rgb(230,247,242)", "private val mint = Color.rgb(244,238,218)", "mint")
s = replace(s, "private val bg = Color.rgb(247,249,248)", "private val bg = Color.rgb(247,244,235)", "background")
s = replace(s, "private val gold = Color.rgb(236,173,64)", "private val gold = Color.rgb(216,174,90)", "gold")
s = replace(s, "private val textColor = Color.rgb(28,37,36)", "private val textColor = Color.rgb(15,48,41)", "text")
s = replace(s, "private val muted = Color.rgb(102,116,113)", "private val muted = Color.rgb(91,105,99)\n    private val ivory = Color.rgb(255,252,244)\n    private val paleGold = Color.rgb(246,232,194)", "premium palette")
s = replace(s, "window.statusBarColor=bg; window.navigationBarColor=Color.WHITE", "window.statusBarColor=tealDark; window.navigationBarColor=tealDark; window.decorView.systemUiVisibility=0", "system bars")

s = replace(
    s,
    "nav=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL;gravity=Gravity.CENTER;setPadding(6.dp,4.dp,6.dp,5.dp);setBackgroundColor(Color.WHITE);elevation=10f}",
    "nav=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL;gravity=Gravity.CENTER;setPadding(8.dp,7.dp,8.dp,7.dp);background=rounded(tealDark,0f);elevation=14f}",
    "navigation shell",
)
s = replace(s, "root.addView(content,LinearLayout.LayoutParams(-1,0,1f));root.addView(nav,LinearLayout.LayoutParams(-1,74.dp))", "root.addView(content,LinearLayout.LayoutParams(-1,0,1f));root.addView(nav,LinearLayout.LayoutParams(-1,82.dp))", "navigation height")
s = replace(
    s,
    "text=label;textSize=11.5f;isAllCaps=false;setTextColor(if(index==0)teal else muted);setBackgroundColor(Color.TRANSPARENT);setPadding(1.dp,2.dp,1.dp,1.dp);gravity=Gravity.CENTER",
    "text=label;textSize=11.5f;isAllCaps=false;setTextColor(if(index==0)gold else Color.WHITE);background=if(index==0)rounded(Color.rgb(18,75,63),15f) else ColorDrawable(Color.TRANSPARENT);setPadding(2.dp,4.dp,2.dp,4.dp);gravity=Gravity.CENTER;typeface=Typeface.DEFAULT_BOLD",
    "navigation button",
)
s = replace(s, "private fun refreshNav(){for(i in 0 until nav.childCount)(nav.getChildAt(i) as Button).setTextColor(if(i==screen)teal else muted)}", "private fun refreshNav(){for(i in 0 until nav.childCount)(nav.getChildAt(i) as Button).apply{setTextColor(if(i==screen)gold else Color.WHITE);background=if(i==screen)rounded(Color.rgb(18,75,63),15f) else ColorDrawable(Color.TRANSPARENT)}}", "navigation refresh")

s = replace(s, "val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;layoutDirection=View.LAYOUT_DIRECTION_RTL;setPadding(18.dp,18.dp,18.dp,32.dp)}", "val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;layoutDirection=View.LAYOUT_DIRECTION_RTL;setPadding(16.dp,16.dp,16.dp,34.dp)}", "page padding")
s = replace(s, "val header=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL;gravity=Gravity.CENTER_VERTICAL;layoutDirection=View.LAYOUT_DIRECTION_RTL}", "val header=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL;gravity=Gravity.CENTER_VERTICAL;layoutDirection=View.LAYOUT_DIRECTION_RTL;setPadding(18.dp,17.dp,18.dp,17.dp);background=premium(tealDark,26f);elevation=7f}", "page header")
s = replace(s, "text=title;textSize=29f;setTextColor(textColor)", "text=title;textSize=27f;setTextColor(Color.WHITE)", "page title")
s = replace(s, "text=subtitle;textSize=14f;setTextColor(muted)", "text=subtitle;textSize=13.5f;setTextColor(paleGold)", "page subtitle")
s = replace(s, "text=emoji;textSize=34f;gravity=Gravity.CENTER;background=rounded(mint,18f)", "text=emoji;textSize=32f;gravity=Gravity.CENTER;background=premium(Color.rgb(16,78,65),18f)", "page emoji")
s = replace(s, "setMargins(0,0,0,14.dp)", "setMargins(0,0,0,18.dp)", "header margin")

s = replace(s, "background=rounded(if(accent)mint else Color.WHITE);elevation=3f", "background=premium(if(accent)Color.rgb(232,241,228) else ivory,20f);elevation=4f", "card background")
s = replace(s, "setTextColor(if(accent)tealDark else textColor)", "setTextColor(tealDark)", "card title")
s = replace(s, "text=body;textSize=14.5f;setTextColor(muted)", "text=body;textSize=14f;setTextColor(if(accent)tealDark else muted)", "card body")
s = replace(s, "text=title;textSize=20f;typeface=Typeface.DEFAULT_BOLD;setTextColor(textColor)", "text=title;textSize=19f;typeface=Typeface.DEFAULT_BOLD;setTextColor(tealDark)", "section title")
s = replace(s, "text=subtitle;textSize=13.5f;setTextColor(muted)", "text=subtitle;textSize=12.5f;setTextColor(muted)", "section subtitle")
s = replace(s, "background=rounded(Color.WHITE,16f)", "background=premium(ivory,16f)", "progress card")
s = replace(s, "background=rounded(Color.WHITE,18f);elevation=2f", "background=premium(tealDark,20f);elevation=5f", "quick tile")
s = replace(s, "text=title;textSize=14f;typeface=Typeface.DEFAULT_BOLD;setTextColor(textColor)", "text=title;textSize=14f;typeface=Typeface.DEFAULT_BOLD;setTextColor(Color.WHITE)", "quick tile title")
s = replace(s, "text=sub;textSize=11.5f;setTextColor(color)", "text=sub;textSize=11.5f;setTextColor(gold)", "quick tile subtitle")
s = replace(s, "private fun rounded(color:Int,radius:Float=18f)=GradientDrawable().apply{shape=GradientDrawable.RECTANGLE;setColor(color);cornerRadius=radius.dp}", "private fun rounded(color:Int,radius:Float=18f)=GradientDrawable().apply{shape=GradientDrawable.RECTANGLE;setColor(color);cornerRadius=radius.dp}\n    private fun premium(color:Int,radius:Float=18f)=GradientDrawable().apply{shape=GradientDrawable.RECTANGLE;setColor(color);cornerRadius=radius.dp;setStroke(1.dp,gold)}", "premium drawable")

s = replace(s, "val body=page(\"שלום ${p.name} 👋\",dayName,\"🥑\")", "val body=page(\"שלום ${p.name}\",dayName,\"ER\")", "dashboard header")
s = replace(s, "background=rounded(mint,24f);elevation=4f", "background=premium(tealDark,26f);elevation=8f", "dashboard hero")
s = replace(s, 'info.addView(TextView(this).apply{text=if(remain>=0)"נשארו $remain קק״ל" else "חריגה של ${-remain} קק״ל";textSize=22f;typeface=Typeface.DEFAULT_BOLD;setTextColor(tealDark);gravity=Gravity.RIGHT})', 'info.addView(TextView(this).apply{text=if(remain>=0)"נשארו $remain קק״ל" else "חריגה של ${-remain} קק״ל";textSize=22f;typeface=Typeface.DEFAULT_BOLD;setTextColor(gold);gravity=Gravity.RIGHT})', "hero headline")
s = replace(s, "setTextColor(muted);gravity=Gravity.RIGHT;setPadding(0,7.dp,0,8.dp)", "setTextColor(Color.WHITE);gravity=Gravity.RIGHT;setPadding(0,7.dp,0,8.dp)", "hero summary")
s = replace(s, "setTextColor(Color.WHITE);textSize=14f;background=rounded(teal,16f)", "setTextColor(tealDark);textSize=14f;background=rounded(gold,16f);typeface=Typeface.DEFAULT_BOLD", "hero action")

long_goal = '        card(body,"🎯 איך חושב היעד?","BMR משוער ${rmr.toInt()} קק״ל → תחזוקה משוערת $maintenance קק״ל → התאמה למטרת $goalDirection $adjText קק״ל → יעד יומי ${p.calories} קק״ל.\\nהמספרים הם הערכה אישית לפי גיל, מין, גובה, משקל ורמת פעילות — לא מדידה מטבולית ישירה.")\n\n'
s = replace(s, long_goal, "", "long calorie explanation")
s = replace(s, 'sectionTitle(body,"אבות המזון","התקדמות מול היעד היומי")', 'sectionTitle(body,"אבות המזון")', "macro caption")
s = replace(s, 'sectionTitle(body,"BMI","מיקום נוכחי על סרגל המבוסס על טווחי CDC למבוגרים")', 'sectionTitle(body,"BMI")', "BMI caption")
s = replace(s, 'card(body,"המשקל והיעד","BMI נוכחי ${"%.1f".format(currentBmi)} · ${HealthCalculations.bmiCategoryAdult(currentBmi)}\\nמשקל ${"%.1f".format(p.weight)} ק״ג → יעד ${"%.1f".format(p.targetWeight)} ק״ג (BMI יעד ${"%.1f".format(targetBmi)}).\\nBMI הוא כלי סקר בלבד ויש לפרש אותו לצד מדדים נוספים.")', 'card(body,"המשקל והיעד","${"%.1f".format(p.weight)} ק״ג  ←  ${"%.1f".format(p.targetWeight)} ק״ג · BMI ${"%.1f".format(currentBmi)}")', "BMI detail")
s = replace(s, 'card(body,"🧠 התוכנית שלי להיום",plan.headline+"\\n\\n"+plan.calorieText+"\\n"+plan.proteinText+"\\n"+plan.waterText+"\\n"+plan.activityText+"\\n\\n"+plan.nextAction,true)', 'card(body,"התוכנית שלי",plan.headline+"\\n"+plan.nextAction,true)', "daily plan")

s = replace(s, "background=rounded(Color.WHITE,20f);elevation=2f", "background=premium(ivory,20f);elevation=4f", "stat card")
s = replace(s, 'val body=page("יומן תזונה","כל מה שאכלת היום, מסודר לפי ארוחות","🍓")', 'val body=page("יומן תזונה",null,"🍓")', "food caption")
s = replace(s, 'sectionTitle(body,"אכלת לאחרונה","לחיצה מוסיפה שוב עם כמות לבחירה")', 'sectionTitle(body,"אכלת לאחרונה")', "recent caption")
s = replace(s, 'hint="🔎 חיפוש מזון במאגר Offline…"', 'hint="חיפוש מזון…"', "search hint")
s = s.replace('search.hint="🔎 חיפוש מזון במאגר Offline…"', 'search.hint="חיפוש מזון…"')
s = replace(s, 'background=rounded(Color.WHITE,18f);isSingleLine=true', 'background=premium(ivory,18f);isSingleLine=true', "premium search")
s = replace(s, "background=rounded(Color.WHITE,20f);elevation=2f", "background=premium(ivory,20f);elevation=4f", "meal card")
s = replace(s, 'body.addView(actionButton("＋ יצירת מזון אישי"){showCustomFoodDialog()},2)', 'body.addView(actionButton("＋ מזון אישי"){showCustomFoodDialog()},2)', "custom food label")

s = replace(s, 'val body=page("הוספה מהירה","כל הנתונים נשמרים מקומית בלבד","✨")', 'val body=page("הוספה",null,"＋")', "quick add caption")
s = replace(s, 'body.addView(actionButton("💧 הוספת מים"){addWaterDialog()});body.addView(actionButton("⚖ הוספת משקל"){addWeightDialog()});body.addView(actionButton("👟 עדכון צעדים ידני"){manualStepsDialog()});body.addView(actionButton("❤ דופק / לחץ דם"){showVitalsDialog()});body.addView(actionButton("📷 הערכת דופק במצלמה"){startPpg()});body.addView(actionButton("🍽 מעבר ליומן תזונה"){showFoodLog()})', 'body.addView(actionButton("💧 מים"){addWaterDialog()});body.addView(actionButton("⚖ משקל"){addWeightDialog()});body.addView(actionButton("👟 צעדים"){manualStepsDialog()});body.addView(actionButton("❤ מדדים"){showVitalsDialog()});body.addView(actionButton("📷 דופק במצלמה"){startPpg()})', "quick add actions")
s = replace(s, '        card(body,"חשוב","הערכת הדופק במצלמה מבוססת שינויי אור (PPG) ונועדה למעקב כללי בלבד. לחץ דם אינו נמדד מהמצלמה באפליקציה; הוא מוזן ידנית.")\n', "", "duplicate PPG explanation")
s = replace(s, 'private fun actionButton(title:String,click:()->Unit)=Button(this).apply{text=title;textSize=17f;isAllCaps=false;gravity=Gravity.RIGHT;setTextColor(textColor);setPadding(16.dp,16.dp,16.dp,16.dp);background=rounded(Color.WHITE);setOnClickListener{click()};layoutParams=LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,0,0,9.dp)}}', 'private fun actionButton(title:String,click:()->Unit)=Button(this).apply{text=title;textSize=17f;isAllCaps=false;gravity=Gravity.RIGHT;setTextColor(Color.WHITE);typeface=Typeface.DEFAULT_BOLD;setPadding(18.dp,17.dp,18.dp,17.dp);background=premium(tealDark,20f);elevation=5f;setOnClickListener{click()};layoutParams=LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,0,0,10.dp)}}', "premium action button")
s = replace(s, 'val body=page("התקדמות","מגמות מקומיות מהמכשיר","📈")', 'val body=page("התקדמות",null,"📈")', "progress caption")
s = replace(s, 'val body=page("הגדרות ופרטיות","גרסה 1.3.2 · Offline","⚙️")', 'val body=page("הגדרות","גרסה 1.4.0","⚙️")', "settings header")
s = replace(s, 'card(body,"פרופיל","${p.name} · גיל ${p.age} · ${p.height.toInt()} ס״מ · ${"%.1f".format(p.weight)} ק״ג · יעד: ${p.goal}"){showOnboarding(true)}\n        card(body,"יעדים","${p.calories} קק״ל · חלבון ${p.protein} ג׳ · מים ${p.water} מ״ל · ${p.steps} צעדים"){showOnboarding(true)}', 'card(body,"פרופיל ויעדים","${p.name} · ${"%.1f".format(p.weight)} ק״ג · ${p.calories} קק״ל · ${p.steps} צעדים"){showOnboarding(true)}', "duplicate profile cards")
s = replace(s, '        card(body,"פרטיות","אין באפליקציה הרשאת INTERNET. יומן האוכל, המשקל, הצעדים והמדדים נשמרים במסד SQLite פנימי במכשיר.")\n        card(body,"מקורות נתונים","מאגר המזון המובנה: מאגר התזונה הלאומי הישראלי של משרד הבריאות (מעל 4,500 פריטי מזון ומתכונים, נתונים ל־100 גרם) שמוטמע ב־APK בזמן הבנייה. BMI: טווחי מבוגרים של CDC. פעילות: CDC Physical Activity Guidelines. מים: ערכי DRI של National Academies מתייחסים לסך המים מכל המזון והמשקאות; יעד השתייה באפליקציה נשאר יעד אישי. מנוע ההכוונה הוא כלי Wellness Offline ואינו תחליף לייעוץ רפואי.")\n        card(body,"מאגר מזון מקומי","${db.foodCatalogCount()} פריטים זמינים לחיפוש ללא אינטרנט")\n', '        card(body,"פרטיות ומידע","Offline לחלוטין · ${db.foodCatalogCount()} פריטי מזון · הנתונים נשמרים רק במכשיר")\n', "settings explanations")
s = replace(s, 'actionButton("מחיקת כל המידע המקומי")', 'actionButton("מחיקת כל הנתונים")', "delete label")
main_path.write_text(s)


r = reminders_path.read_text()
r = replace(r, "import android.graphics.Color", "import android.graphics.Color\nimport android.graphics.drawable.GradientDrawable", "reminder drawable import")
r = replace(r, "setPadding(dp(20), dp(20), dp(20), dp(32))", "setPadding(dp(16), dp(16), dp(16), dp(32))", "reminder padding")
r = replace(r, "setBackgroundColor(Color.rgb(247,250,248))", "setBackgroundColor(Color.rgb(247,244,235))", "reminder background")
r = replace(r, 'body.addView(subText("בחרו מתי אפרת רביבו תזכיר לאכול ולשתות. ההתראות מקומיות, עם צליל ורטט, ועובדות גם בלי אינטרנט."))', "", "reminder intro")
r = r.replace("setBackgroundColor(Color.WHITE)", "background=premium(Color.rgb(255,252,244),18f)")
r = replace(r, "setBackgroundColor(Color.rgb(13,126,104))", "background=premium(Color.rgb(0,55,45),20f)", "reminder save")
r = replace(r, 'body.addView(subText("Android עשוי להזיז תזכורת בכמה דקות כדי לחסוך בסוללה. אין צורך בחיבור לאינטרנט. התזכורות נשמרות במכשיר ונטענות מחדש אחרי אתחול."))', "", "reminder footer")
r = replace(r, "private fun section(t:String)=TextView(this).apply{text=t;textSize=20f;setTextColor(Color.rgb(20,56,49));gravity=Gravity.RIGHT;setPadding(0,dp(22),0,dp(10));setTypeface(typeface,1)}", "private fun section(t:String)=TextView(this).apply{text=t;textSize=19f;setTextColor(Color.rgb(0,55,45));gravity=Gravity.RIGHT;setPadding(2.dp,22.dp,2.dp,10.dp);setTypeface(typeface,1)}", "reminder section")
r = replace(r, "private fun titleText(t:String)=TextView(this).apply{text=t;textSize=28f;setTextColor(Color.rgb(18,44,39));gravity=Gravity.RIGHT;setTypeface(typeface,1)}", "private fun titleText(t:String)=TextView(this).apply{text=t;textSize=27f;setTextColor(Color.WHITE);gravity=Gravity.RIGHT;setTypeface(typeface,1);background=premium(Color.rgb(0,55,45),24f);setPadding(18.dp,18.dp,18.dp,18.dp)}", "reminder title")
r = replace(r, "private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()", "private fun premium(color:Int,radius:Float)=GradientDrawable().apply{setColor(color);cornerRadius=dp(radius.toInt()).toFloat();setStroke(dp(1),Color.rgb(216,174,90))}\n    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()\n    private val Int.dp:Int get()=dp(this)", "reminder premium helper")
reminders_path.write_text(r)


p = ppg_path.read_text()
p = replace(p, "window.statusBarColor = Color.rgb(246,248,247)", "window.statusBarColor = Color.rgb(0,55,45)", "PPG status bar")
p = replace(p, "setBackgroundColor(Color.rgb(246,248,247))", "setBackgroundColor(Color.rgb(247,244,235))", "PPG background")
p = replace(p, 'root.addView(TextView(this).apply { text="❤️ מדידת דופק במצלמה"; textSize=28f; setTextColor(Color.rgb(28,37,36)); typeface=Typeface.DEFAULT_BOLD; gravity=Gravity.RIGHT })', 'root.addView(TextView(this).apply { text="❤️ דופק במצלמה"; textSize=27f; setTextColor(Color.WHITE); typeface=Typeface.DEFAULT_BOLD; gravity=Gravity.RIGHT; background=GradientDrawable().apply{setColor(Color.rgb(0,55,45));cornerRadius=24.dp.toFloat();setStroke(1.dp,Color.rgb(216,174,90))};setPadding(18.dp,18.dp,18.dp,18.dp) })', "PPG title")
p = replace(p, 'root.addView(TextView(this).apply { text="כסו בעדינות את המצלמה האחורית והפלאש באצבע. התמונה והתקדמות המדידה מוצגות בזמן אמת."; textSize=15f; setTextColor(Color.rgb(95,109,106)); gravity=Gravity.RIGHT; setPadding(0,6.dp,0,14.dp) })', 'root.addView(TextView(this).apply { text="כסו את המצלמה והפלאש באצבע"; textSize=14f; setTextColor(Color.rgb(91,105,99)); gravity=Gravity.RIGHT; setPadding(4.dp,10.dp,4.dp,14.dp) })', "PPG intro")
p = replace(p, 'root.addView(TextView(this).apply { text="המדידה נמשכת כ־20 שניות. נסו להישאר בלי תנועה ולכסות את העדשה והפלאש באופן מלא, ללא לחץ חזק."; textSize=14f; gravity=Gravity.RIGHT; setTextColor(Color.DKGRAY); setPadding(0,8.dp,0,8.dp) })', "", "PPG duplicate guide")
p = replace(p, 'text="חשוב: זו הערכת PPG לצורכי Wellness ומעקב כללי בלבד. היא אינה ECG, אינה מודדת לחץ דם ואינה מחליפה מכשור רפואי."', 'text="הערכת Wellness בלבד · אינה מדידה רפואית"', "PPG safety")
ppg_path.write_text(p)


theme_path.write_text('''<resources>
    <style name="Theme.OfflineHealth" parent="android:style/Theme.Material.Light.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:statusBarColor">#00372D</item>
        <item name="android:navigationBarColor">#00372D</item>
        <item name="android:colorAccent">#D8AE5A</item>
        <item name="android:windowActionModeOverlay">true</item>
        <item name="android:windowNoTitle">true</item>
    </style>
</resources>
''')

g = gradle_path.read_text()
g = replace(g, 'versionCode = 8', 'versionCode = 9', "version code")
g = replace(g, 'versionName = "1.3.2"', 'versionName = "1.4.0"', "version name")
gradle_path.write_text(g)

print("Applied OfflineHealth 1.4.0 premium ER redesign")
