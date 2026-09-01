package il.co.offlinehealth

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.io.BufferedReader
import java.io.InputStreamReader
import java.time.LocalDate
import kotlin.math.roundToInt

class HealthDb(private val ctx: Context) : SQLiteOpenHelper(ctx, DB_NAME, null, DB_VERSION) {
    companion object {
        const val DB_NAME = "health_offline.db"
        const val DB_VERSION = 2
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE profile(id INTEGER PRIMARY KEY CHECK(id=1), name TEXT, age INTEGER, sex TEXT, height_cm REAL, weight_kg REAL, target_weight REAL, activity_level INTEGER, goal TEXT, calorie_goal INTEGER, protein_goal INTEGER, carb_goal INTEGER, fat_goal INTEGER, water_goal_ml INTEGER, steps_goal INTEGER)")
        db.execSQL("CREATE TABLE food_catalog(id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT UNIQUE, name TEXT NOT NULL, kcal REAL NOT NULL DEFAULT 0, protein REAL NOT NULL DEFAULT 0, carbs REAL NOT NULL DEFAULT 0, fat REAL NOT NULL DEFAULT 0, source TEXT NOT NULL DEFAULT 'USDA')")
        db.execSQL("CREATE INDEX idx_food_name ON food_catalog(name)")
        db.execSQL("CREATE TABLE food_log(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, meal TEXT NOT NULL, food_id INTEGER, name TEXT NOT NULL, grams REAL NOT NULL, kcal REAL NOT NULL, protein REAL NOT NULL, carbs REAL NOT NULL, fat REAL NOT NULL, created_at INTEGER NOT NULL)")
        db.execSQL("CREATE INDEX idx_food_log_day ON food_log(day)")
        db.execSQL("CREATE TABLE weight_log(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, weight REAL NOT NULL, note TEXT, created_at INTEGER NOT NULL)")
        db.execSQL("CREATE TABLE water_log(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, ml INTEGER NOT NULL, created_at INTEGER NOT NULL)")
        db.execSQL("CREATE TABLE steps_log(day TEXT PRIMARY KEY, auto_steps INTEGER NOT NULL DEFAULT 0, manual_steps INTEGER NOT NULL DEFAULT 0, updated_at INTEGER NOT NULL)")
        db.execSQL("CREATE TABLE vitals_log(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, heart_rate INTEGER, systolic INTEGER, diastolic INTEGER, stress INTEGER, source TEXT, created_at INTEGER NOT NULL)")
        db.execSQL("CREATE TABLE favorite_food(food_id INTEGER PRIMARY KEY)")
        seedBuiltInFoods(db)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        if (oldVersion < 2) seedNationalFoods(db)
    }

    private fun seedBuiltInFoods(db: SQLiteDatabase) {
        val fallback = listOf(
            arrayOf("local-rice","אורז לבן מבושל","130","2.69","28.17","0.28"),
            arrayOf("local-egg","ביצה שלמה","143","12.56","0.72","9.51"),
            arrayOf("local-chicken","חזה עוף מבושל","165","31.02","0","3.57"),
            arrayOf("local-banana","בננה","89","1.09","22.84","0.33"),
            arrayOf("local-apple","תפוח עם קליפה","52","0.26","13.81","0.17"),
            arrayOf("local-oats","שיבולת שועל יבשה","379","13.15","67.70","6.52"),
            arrayOf("local-milk","חלב 3% בקירוב","61","3.15","4.80","3.25"),
            arrayOf("local-yogurt","יוגורט טבעי","61","3.47","4.66","3.25")
        )
        db.beginTransaction()
        try {
            for (r in fallback) insertFood(db, r[0], r[1], r[2].toDouble(), r[3].toDouble(), r[4].toDouble(), r[5].toDouble(), "USDA common reference")
            seedNationalFoods(db)
            db.setTransactionSuccessful()
        } finally { db.endTransaction() }
    }

    private fun seedNationalFoods(db: SQLiteDatabase) {
        try {
            ctx.assets.open("israel_foods.csv").use { input ->
                BufferedReader(InputStreamReader(input)).useLines { lines ->
                    lines.drop(1).forEach { line ->
                        val cols = parseCsv(line)
                        if (cols.size >= 7) {
                            insertFood(
                                db,
                                "israel:${cols[0]}",
                                cols[1],
                                cols[2].toDoubleOrNull() ?: 0.0,
                                cols[3].toDoubleOrNull() ?: 0.0,
                                cols[4].toDoubleOrNull() ?: 0.0,
                                cols[5].toDoubleOrNull() ?: 0.0,
                                cols[6].ifBlank { "מאגר התזונה הלאומי הישראלי · משרד הבריאות" }
                            )
                        }
                    }
                }
            }
        } catch (_: Exception) { }
    }

    fun foodCatalogCount(): Int = readableDatabase.rawQuery("SELECT COUNT(*) FROM food_catalog", null).use { c -> c.moveToFirst(); c.getInt(0) }

    private fun insertFood(db: SQLiteDatabase, sourceId: String, name: String, kcal: Double, protein: Double, carbs: Double, fat: Double, source: String) {
        val v = ContentValues().apply { put("source_id", sourceId); put("name", name); put("kcal", kcal); put("protein", protein); put("carbs", carbs); put("fat", fat); put("source", source) }
        db.insertWithOnConflict("food_catalog", null, v, SQLiteDatabase.CONFLICT_IGNORE)
    }

    private fun parseCsv(line: String): List<String> {
        val out = mutableListOf<String>(); val sb = StringBuilder(); var quote = false; var i = 0
        while (i < line.length) {
            val c = line[i]
            when {
                c == '"' && quote && i + 1 < line.length && line[i+1] == '"' -> { sb.append('"'); i++ }
                c == '"' -> quote = !quote
                c == ',' && !quote -> { out.add(sb.toString()); sb.clear() }
                else -> sb.append(c)
            }; i++
        }
        out.add(sb.toString()); return out
    }

    data class Profile(val name:String,val age:Int,val sex:String,val height:Double,val weight:Double,val targetWeight:Double,val activity:Int,val goal:String,val calories:Int,val protein:Int,val carbs:Int,val fat:Int,val water:Int,val steps:Int)
    data class Food(val id:Long,val name:String,val kcal:Double,val protein:Double,val carbs:Double,val fat:Double,val source:String)
    data class FoodLog(val id:Long,val meal:String,val name:String,val grams:Double,val kcal:Double,val protein:Double,val carbs:Double,val fat:Double)
    data class DayTotals(val kcal:Int,val protein:Int,val carbs:Int,val fat:Int,val water:Int,val steps:Int)

    fun getProfile(): Profile? = readableDatabase.rawQuery("SELECT name,age,sex,height_cm,weight_kg,target_weight,activity_level,goal,calorie_goal,protein_goal,carb_goal,fat_goal,water_goal_ml,steps_goal FROM profile WHERE id=1", null).use { c ->
        if (!c.moveToFirst()) null else Profile(c.getString(0),c.getInt(1),c.getString(2),c.getDouble(3),c.getDouble(4),c.getDouble(5),c.getInt(6),c.getString(7),c.getInt(8),c.getInt(9),c.getInt(10),c.getInt(11),c.getInt(12),c.getInt(13))
    }

    fun saveProfile(p: Profile) {
        writableDatabase.insertWithOnConflict("profile", null, ContentValues().apply { put("id",1);put("name",p.name);put("age",p.age);put("sex",p.sex);put("height_cm",p.height);put("weight_kg",p.weight);put("target_weight",p.targetWeight);put("activity_level",p.activity);put("goal",p.goal);put("calorie_goal",p.calories);put("protein_goal",p.protein);put("carb_goal",p.carbs);put("fat_goal",p.fat);put("water_goal_ml",p.water);put("steps_goal",p.steps) }, SQLiteDatabase.CONFLICT_REPLACE)
    }

    fun searchFood(q: String, limit: Int = 30): List<Food> {
        val term = "%${q.trim()}%"; val out = mutableListOf<Food>()
        readableDatabase.rawQuery("SELECT id,name,kcal,protein,carbs,fat,source FROM food_catalog WHERE name LIKE ? ORDER BY CASE WHEN name LIKE ? THEN 0 ELSE 1 END,name LIMIT ?", arrayOf(term,"${q.trim()}%",limit.toString())).use { c ->
            while(c.moveToNext()) out.add(Food(c.getLong(0),c.getString(1),c.getDouble(2),c.getDouble(3),c.getDouble(4),c.getDouble(5),c.getString(6)))
        }; return out
    }

    fun addCustomFood(name:String,kcal:Double,protein:Double,carbs:Double,fat:Double) {
        insertFood(writableDatabase, "user:${System.currentTimeMillis()}", name, kcal, protein, carbs, fat, "המשתמש")
    }

    fun logFood(food: Food, grams: Double, meal: String, day: String = LocalDate.now().toString()) {
        val f = grams / 100.0
        writableDatabase.insert("food_log", null, ContentValues().apply { put("day",day);put("meal",meal);put("food_id",food.id);put("name",food.name);put("grams",grams);put("kcal",food.kcal*f);put("protein",food.protein*f);put("carbs",food.carbs*f);put("fat",food.fat*f);put("created_at",System.currentTimeMillis()) })
    }

    fun deleteFoodLog(id:Long) { writableDatabase.delete("food_log","id=?", arrayOf(id.toString())) }
    fun todayFoodLogs(day:String=LocalDate.now().toString()): List<Pair<Long,String>> {
        val out = mutableListOf<Pair<Long,String>>()
        readableDatabase.rawQuery("SELECT id,name,grams,kcal FROM food_log WHERE day=? ORDER BY created_at DESC", arrayOf(day)).use { c ->
            while (c.moveToNext()) {
                val id = c.getLong(0); val name = c.getString(1); val grams = c.getDouble(2).roundToInt(); val kcal = c.getDouble(3).roundToInt()
                out.add(id to "$name · $grams גרם · $kcal קק״ל")
            }
        }
        return out
    }

    fun todayFoodLogsDetailed(day:String=LocalDate.now().toString()): List<FoodLog> {
        val out=mutableListOf<FoodLog>()
        readableDatabase.rawQuery("SELECT id,meal,name,grams,kcal,protein,carbs,fat FROM food_log WHERE day=? ORDER BY created_at ASC", arrayOf(day)).use { c -> while(c.moveToNext()) out.add(FoodLog(c.getLong(0),c.getString(1),c.getString(2),c.getDouble(3),c.getDouble(4),c.getDouble(5),c.getDouble(6),c.getDouble(7))) }
        return out
    }

    fun recentFoods(limit:Int=8): List<Food> {
        val out=mutableListOf<Food>()
        readableDatabase.rawQuery("SELECT f.id,f.name,f.kcal,f.protein,f.carbs,f.fat,f.source FROM food_catalog f JOIN (SELECT food_id,MAX(created_at) mx FROM food_log WHERE food_id IS NOT NULL GROUP BY food_id ORDER BY mx DESC LIMIT ?) x ON x.food_id=f.id ORDER BY x.mx DESC", arrayOf(limit.toString())).use { c -> while(c.moveToNext()) out.add(Food(c.getLong(0),c.getString(1),c.getDouble(2),c.getDouble(3),c.getDouble(4),c.getDouble(5),c.getString(6))) }
        return out
    }

    fun addWater(ml:Int, day:String=LocalDate.now().toString()) { writableDatabase.insert("water_log",null,ContentValues().apply {put("day",day);put("ml",ml);put("created_at",System.currentTimeMillis())}) }
    fun addWeight(weight:Double,note:String="", day:String=LocalDate.now().toString()) { writableDatabase.insert("weight_log",null,ContentValues().apply {put("day",day);put("weight",weight);put("note",note);put("created_at",System.currentTimeMillis())}); val p=getProfile(); if(p!=null) saveProfile(p.copy(weight=weight)) }
    fun setManualSteps(steps:Int, day:String=LocalDate.now().toString()) = upsertSteps(day,null,steps)
    fun setAutoSteps(steps:Int, day:String=LocalDate.now().toString()) = upsertSteps(day,steps,null)
    private fun upsertSteps(day:String, auto:Int?, manual:Int?) {
        writableDatabase.execSQL("INSERT INTO steps_log(day,auto_steps,manual_steps,updated_at) VALUES(?,?,?,?) ON CONFLICT(day) DO UPDATE SET auto_steps=COALESCE(?,auto_steps),manual_steps=COALESCE(?,manual_steps),updated_at=?", arrayOf(day,auto?:0,manual?:0,System.currentTimeMillis(),auto,manual,System.currentTimeMillis()))
    }
    fun addVitals(hr:Int?,sys:Int?,dia:Int?,stress:Int?,source:String, day:String=LocalDate.now().toString()) { writableDatabase.insert("vitals_log",null,ContentValues().apply {put("day",day); if(hr!=null)put("heart_rate",hr);if(sys!=null)put("systolic",sys);if(dia!=null)put("diastolic",dia);if(stress!=null)put("stress",stress);put("source",source);put("created_at",System.currentTimeMillis())}) }

    fun dayTotals(day:String=LocalDate.now().toString()): DayTotals {
        val food = readableDatabase.rawQuery("SELECT COALESCE(SUM(kcal),0),COALESCE(SUM(protein),0),COALESCE(SUM(carbs),0),COALESCE(SUM(fat),0) FROM food_log WHERE day=?",arrayOf(day)).use{c->c.moveToFirst(); intArrayOf(c.getInt(0),c.getInt(1),c.getInt(2),c.getInt(3))}
        val water=readableDatabase.rawQuery("SELECT COALESCE(SUM(ml),0) FROM water_log WHERE day=?",arrayOf(day)).use{c->c.moveToFirst();c.getInt(0)}
        val steps=readableDatabase.rawQuery("SELECT COALESCE(MAX(auto_steps,manual_steps),0) FROM steps_log WHERE day=?",arrayOf(day)).use{c->if(c.moveToFirst())c.getInt(0) else 0}
        return DayTotals(food[0],food[1],food[2],food[3],water,steps)
    }

    fun latestVitals(): String? = readableDatabase.rawQuery("SELECT heart_rate,systolic,diastolic,source FROM vitals_log ORDER BY created_at DESC LIMIT 1",null).use { c -> if(!c.moveToFirst()) null else buildString { if(!c.isNull(0)) append("דופק ${c.getInt(0)} BPM"); if(!c.isNull(1)&&!c.isNull(2)){if(isNotEmpty())append(" · ");append("לחץ דם ${c.getInt(1)}/${c.getInt(2)}")}; if(isNotEmpty())append(" · ${c.getString(3)}") } }

    fun recentWeights(limit:Int=30): List<Pair<String,Double>> { val out=mutableListOf<Pair<String,Double>>(); readableDatabase.rawQuery("SELECT day,weight FROM weight_log ORDER BY created_at DESC LIMIT ?",arrayOf(limit.toString())).use{c->while(c.moveToNext())out.add(c.getString(0) to c.getDouble(1))}; return out.reversed() }
    fun lastSevenDays(): List<Pair<String,DayTotals>> = (6 downTo 0).map { d -> val day=LocalDate.now().minusDays(d.toLong()).toString(); day to dayTotals(day) }
}
