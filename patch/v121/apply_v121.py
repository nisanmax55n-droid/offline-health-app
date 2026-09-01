from pathlib import Path
import re

root = Path('health-offline-android')
main = root / 'app/src/main/java/il/co/offlinehealth/MainActivity.kt'
calc = root / 'app/src/main/java/il/co/offlinehealth/HealthCalculations.kt'
gradle = root / 'app/build.gradle.kts'
tests = root / 'app/src/test/java/il/co/offlinehealth'

s = main.read_text()
old = 'else->"🥗"}\n        }\n    }\n\n    private fun addFoodDialog'
new = 'else->"🥗"}\n        }\n\n    private fun addFoodDialog'
if old not in s:
    raise SystemExit('expected foodEmoji extra-brace pattern not found')
s = s.replace(old, new, 1)

c = calc.read_text().replace('"טווח משקל תקין"', '"משקל תקין"')
old_goal = '''    fun goalCalories(maintenance: Int, goal: String, manualAdjustment: Int? = null): Int {
        val adj = manualAdjustment ?: when (goal) {
            "ירידה" -> -300
            "עלייה" -> 300
            else -> 0
        }
        return max(1200, maintenance + adj)
    }
'''
new_goal = '''    fun goalAdjustment(goal: String): Int = when (goal) {
        "ירידה" -> -300
        "עלייה" -> 300
        else -> 0
    }

    fun goalFromWeights(currentWeightKg: Double, targetWeightKg: Double, fallback: String = "שמירה"): String = when {
        targetWeightKg > currentWeightKg + 0.5 -> "עלייה"
        targetWeightKg < currentWeightKg - 0.5 -> "ירידה"
        fallback in setOf("עלייה", "ירידה", "שמירה") -> fallback
        else -> "שמירה"
    }

    fun goalCalories(maintenance: Int, goal: String, manualAdjustment: Int? = null): Int {
        val adj = manualAdjustment ?: goalAdjustment(goal)
        return max(1200, maintenance + adj)
    }
'''
if old_goal not in c:
    raise SystemExit('goalCalories block not found')
c = c.replace(old_goal, new_goal, 1)

old_direction = '''        val direction = when {
            profile.targetWeight > profile.weight + 0.5 -> "עלייה"
            profile.targetWeight < profile.weight - 0.5 -> "ירידה"
            else -> "שמירה"
        }
'''
new_direction = '''        val direction = goalFromWeights(profile.weight, profile.targetWeight, profile.goal)
        val rmr = mifflinStJeor(profile.weight, profile.height, profile.age, profile.sex == "זכר")
        val maintenance = estimatedMaintenance(rmr, profile.activity)
        val adjustment = profile.calories - maintenance
'''
if old_direction not in c:
    raise SystemExit('guidance direction block not found')
c = c.replace(old_direction, new_direction, 1)

old_cal_text = '''        val calorieText = if (remaining >= 0)
            "נותרו כ־$remaining קק״ל במסגרת היעד היומי (${profile.calories} קק״ל בסיס + פעילות שנמדדה)."
        else "נרשמה חריגה של ${-remaining} קק״ל מהמאזן היומי המחושב. יום אחד לא קובע מגמה."
'''
new_cal_text = '''        val adjustmentLabel = when {
            adjustment > 0 -> "+$adjustment"
            adjustment < 0 -> "$adjustment"
            else -> "0"
        }
        val calorieText = if (remaining >= 0)
            "נותרו כ־$remaining קק״ל. תחזוקה משוערת: $maintenance קק״ל; התאמה למטרת $direction: $adjustmentLabel; יעד בסיס: ${profile.calories} קק״ל, לפני פעילות שנמדדה."
        else "נרשמה חריגה של ${-remaining} קק״ל מהמאזן היומי המחושב. תחזוקה משוערת: $maintenance קק״ל; התאמה למטרת $direction: $adjustmentLabel. יום אחד לא קובע מגמה."
'''
if old_cal_text not in c:
    raise SystemExit('guidance calorie text block not found')
c = c.replace(old_cal_text, new_cal_text, 1)
calc.write_text(c)

old_dash_start = 'screen=0;refreshNav();val p=db.getProfile()?:return;val t=db.dayTotals();val activity=HealthCalculations.walkingCalories(t.steps,p.height,p.weight);val remain=HealthCalculations.remainingCalories(p.calories,t.kcal,activity)'
new_dash_start = 'screen=0;refreshNav();val p=db.getProfile()?:return;val t=db.dayTotals();val activity=HealthCalculations.walkingCalories(t.steps,p.height,p.weight);val remain=HealthCalculations.remainingCalories(p.calories,t.kcal,activity);val rmr=HealthCalculations.mifflinStJeor(p.weight,p.height,p.age,p.sex=="זכר");val maintenance=HealthCalculations.estimatedMaintenance(rmr,p.activity);val goalDirection=HealthCalculations.goalFromWeights(p.weight,p.targetWeight,p.goal);val goalAdjustment=p.calories-maintenance'
if old_dash_start not in s:
    raise SystemExit('dashboard start not found')
s = s.replace(old_dash_start, new_dash_start, 1)

hero_anchor = 'hero.addView(info,LinearLayout.LayoutParams(0,-2,1f));body.addView(hero,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,0,0,14.dp)})\n\n        sectionTitle(body,"פעולות מהירות")'
hero_insert = '''hero.addView(info,LinearLayout.LayoutParams(0,-2,1f));body.addView(hero,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,0,0,14.dp)})

        val adjText=when{goalAdjustment>0->"+$goalAdjustment";goalAdjustment<0->"$goalAdjustment";else->"0"}
        card(body,"🎯 איך חושב היעד?","BMR משוער ${rmr.toInt()} קק״ל → תחזוקה משוערת $maintenance קק״ל → התאמה למטרת $goalDirection $adjText קק״ל → יעד יומי ${p.calories} קק״ל.\\nהמספרים הם הערכה אישית לפי גיל, מין, גובה, משקל ורמת פעילות — לא מדידה מטבולית ישירה.")

        sectionTitle(body,"פעולות מהירות")'''
if hero_anchor not in s:
    raise SystemExit('hero anchor not found')
s = s.replace(hero_anchor, hero_insert, 1)

macro_anchor = '''        progressRow(body,"💪","חלבון",t.protein,p.protein,teal)
        progressRow(body,"🌾","פחמימות",t.carbs,p.carbs,gold)
        progressRow(body,"🥑","שומן",t.fat,p.fat,coral)

        sectionTitle(body,"היום שלי")'''
macro_insert = '''        progressRow(body,"💪","חלבון",t.protein,p.protein,teal)
        progressRow(body,"🌾","פחמימות",t.carbs,p.carbs,gold)
        progressRow(body,"🥑","שומן",t.fat,p.fat,coral)

        val currentBmi=HealthCalculations.bmi(p.weight,p.height)
        val targetBmi=HealthCalculations.bmi(p.targetWeight,p.height)
        sectionTitle(body,"BMI","מיקום נוכחי על סרגל המבוסס על טווחי CDC למבוגרים")
        body.addView(BmiGaugeView(this,currentBmi),LinearLayout.LayoutParams(-1,150.dp).apply{setMargins(0,0,0,6.dp)})
        card(body,"המשקל והיעד","BMI נוכחי ${"%.1f".format(currentBmi)} · ${HealthCalculations.bmiCategoryAdult(currentBmi)}\\nמשקל ${"%.1f".format(p.weight)} ק״ג → יעד ${"%.1f".format(p.targetWeight)} ק״ג (BMI יעד ${"%.1f".format(targetBmi)}).\\nBMI הוא כלי סקר בלבד ויש לפרש אותו לצד מדדים נוספים.")

        sectionTitle(body,"היום שלי")'''
if macro_anchor not in s:
    raise SystemExit('macro anchor not found')
s = s.replace(macro_anchor, macro_insert, 1)

old_save = 'val g=goal.selectedItem.toString();val rmr=HealthCalculations.mifflinStJeor(w,h,a,sex.selectedItem.toString()=="זכר");val maint=HealthCalculations.estimatedMaintenance(rmr,activity.selectedItemPosition);val cal=HealthCalculations.goalCalories(maint,g);'
new_save = 'val selectedGoal=goal.selectedItem.toString();val g=HealthCalculations.goalFromWeights(w,tw,selectedGoal);val rmr=HealthCalculations.mifflinStJeor(w,h,a,sex.selectedItem.toString()=="זכר");val maint=HealthCalculations.estimatedMaintenance(rmr,activity.selectedItemPosition);val cal=HealthCalculations.goalCalories(maint,g);'
if old_save not in s:
    raise SystemExit('profile save goal calculation not found')
s = s.replace(old_save, new_save, 1)

old_bmi = '''class BmiGaugeView(ctx:Context, private val bmi:Double):View(ctx){
    private val txt=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=Color.rgb(28,37,36);textSize=42f;typeface=Typeface.DEFAULT_BOLD;textAlign=Paint.Align.CENTER}
    private val sub=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=Color.rgb(90,104,101);textSize=25f;textAlign=Paint.Align.CENTER}
    private val colors=intArrayOf(Color.rgb(224,78,78),Color.rgb(241,171,63),Color.rgb(70,166,103),Color.rgb(241,171,63),Color.rgb(224,78,78))
    override fun onDraw(c:Canvas){super.onDraw(c);val left=28f;val right=width-28f;val y=height*0.63f;val h=26f;val seg=(right-left)/5f
        for(i in 0..4){val r=RectF(left+i*seg,y,left+(i+1)*seg,y+h);val p=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=colors[i]};c.drawRoundRect(r,if(i==0||i==4)13f else 0f,if(i==0||i==4)13f else 0f,p)}
        val normalized=((bmi-15.0)/(40.0-15.0)).coerceIn(0.0,1.0);val x=(left+(right-left)*normalized).toFloat();val marker=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=Color.rgb(20,34,32)};val path=Path().apply{moveTo(x,y-6);lineTo(x-12,y-28);lineTo(x+12,y-28);close()};c.drawPath(path,marker)
        c.drawText(if(bmi>0)"%.1f".format(bmi) else "—",width/2f,50f,txt);c.drawText(if(bmi>0)HealthCalculations.bmiCategoryAdult(bmi) else "אין נתונים",width/2f,84f,sub)
        c.drawText("נמוך",left+seg/2,height-10f,sub);c.drawText("תקין",left+seg*2.5f,height-10f,sub);c.drawText("גבוה",right-seg/2,height-10f,sub)
    }
}
'''
new_bmi = '''class BmiGaugeView(ctx:Context, private val bmi:Double):View(ctx){
    private val txt=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=Color.rgb(28,37,36);textSize=42f;typeface=Typeface.DEFAULT_BOLD;textAlign=Paint.Align.CENTER}
    private val sub=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=Color.rgb(90,104,101);textSize=22f;textAlign=Paint.Align.CENTER}
    private val bounds=floatArrayOf(15f,18.5f,25f,30f,35f,40f)
    private val colors=intArrayOf(Color.rgb(224,78,78),Color.rgb(70,166,103),Color.rgb(241,171,63),Color.rgb(235,132,62),Color.rgb(224,78,78))
    override fun onDraw(c:Canvas){super.onDraw(c);val left=28f;val right=width-28f;val y=height*0.63f;val h=26f;val minB=15f;val maxB=40f
        fun map(v:Float)=left+(right-left)*((v-minB)/(maxB-minB))
        for(i in 0 until colors.size){val x1=map(bounds[i]);val x2=map(bounds[i+1]);val r=RectF(x1,y,x2,y+h);val p=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=colors[i]};c.drawRoundRect(r,if(i==0||i==colors.lastIndex)13f else 0f,if(i==0||i==colors.lastIndex)13f else 0f,p)}
        val x=map(bmi.toFloat().coerceIn(minB,maxB));val marker=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=Color.rgb(20,34,32)};val path=Path().apply{moveTo(x,y-6);lineTo(x-12,y-28);lineTo(x+12,y-28);close()};c.drawPath(path,marker)
        c.drawText(if(bmi>0)"%.1f".format(bmi) else "—",width/2f,48f,txt);c.drawText(if(bmi>0)HealthCalculations.bmiCategoryAdult(bmi) else "אין נתונים",width/2f,82f,sub)
        c.drawText("תת",map(16.75f),height-9f,sub);c.drawText("תקין",map(21.75f),height-9f,sub);c.drawText("עודף",map(27.5f),height-9f,sub);c.drawText("השמנה",map(35f),height-9f,sub)
    }
}
'''
if old_bmi not in s:
    raise SystemExit('BMI gauge class block not found')
s = s.replace(old_bmi, new_bmi, 1)
main.write_text(s)

g = gradle.read_text().replace('versionName = "1.2.0"', 'versionName = "1.2.1"')
g = re.sub(r'versionCode\s*=\s*(\d+)', lambda m: f'versionCode = {int(m.group(1)) + 1}', g, count=1)
gradle.write_text(g)

tests.mkdir(parents=True, exist_ok=True)
test_content = "package il.co.offlinehealth\n\nimport org.junit.Assert.assertEquals\nimport org.junit.Test\n\nclass GoalEngineTest {\n    @Test fun gainAddsControlledSurplus() = assertEquals(2300, HealthCalculations.goalCalories(2000, \"עלייה\"))\n    @Test fun lossUsesControlledDeficit() = assertEquals(1700, HealthCalculations.goalCalories(2000, \"ירידה\"))\n    @Test fun maintenanceStaysAtMaintenance() = assertEquals(2000, HealthCalculations.goalCalories(2000, \"שמירה\"))\n    @Test fun higherTargetInfersGain() = assertEquals(\"עלייה\", HealthCalculations.goalFromWeights(70.0, 80.0, \"שמירה\"))\n    @Test fun lowerTargetInfersLoss() = assertEquals(\"ירידה\", HealthCalculations.goalFromWeights(84.0, 70.0, \"שמירה\"))\n}\n"
(tests / 'GoalEngineTest.kt').write_text(test_content)
