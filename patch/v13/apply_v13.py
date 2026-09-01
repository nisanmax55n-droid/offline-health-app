from pathlib import Path
import base64
import re
import shutil
import xml.etree.ElementTree as ET

root = Path('health-offline-android')
src = root / 'app/src/main/java/il/co/offlinehealth'
res = root / 'app/src/main/res'
main = src / 'MainActivity.kt'
gradle = root / 'app/build.gradle.kts'
manifest = root / 'app/src/main/AndroidManifest.xml'
strings = res / 'values/strings.xml'
patch = Path('patch/v13')

for name in ['ReminderScheduler.kt', 'ReminderReceiver.kt', 'ReminderSettingsActivity.kt']:
    shutil.copy2(patch / name, src / name)

g = gradle.read_text()
g = g.replace('versionName = "1.2.1"', 'versionName = "1.3.2"')
g = re.sub(r'versionCode\s*=\s*(\d+)', 'versionCode = 8', g, count=1)
gradle.write_text(g)

ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
tree = ET.parse(strings)
r = tree.getroot()
app_name = None
for child in r.findall('string'):
    if child.attrib.get('name') == 'app_name':
        app_name = child
        break
if app_name is None:
    app_name = ET.SubElement(r, 'string', {'name':'app_name'})
app_name.text = 'אפרת רביבו – ניהול תזונה אישית'
tree.write(strings, encoding='utf-8', xml_declaration=True)

(res / 'drawable').mkdir(parents=True, exist_ok=True)
(res / 'mipmap-anydpi-v26').mkdir(parents=True, exist_ok=True)
(res / 'values').mkdir(parents=True, exist_ok=True)

(res / 'drawable/ic_efrat_foreground.png').write_bytes(
    base64.b64decode((patch / 'ic_efrat_foreground.png.b64').read_text())
)

(res / 'drawable/ic_efrat_logo.xml').write_text('''<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item><shape android:shape="rectangle"><solid android:color="#073D34"/><corners android:radius="24dp"/></shape></item>
    <item android:drawable="@drawable/ic_efrat_foreground"/>
</layer-list>''')

(res / 'mipmap-anydpi-v26/ic_launcher.xml').write_text('''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/efrat_icon_bg"/>
    <foreground android:drawable="@drawable/ic_efrat_foreground"/>
</adaptive-icon>''')
(res / 'mipmap-anydpi-v26/ic_launcher_round.xml').write_text('''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/efrat_icon_bg"/>
    <foreground android:drawable="@drawable/ic_efrat_foreground"/>
</adaptive-icon>''')

colors_tree = ET.parse(res / 'values/colors.xml')
colors_root = colors_tree.getroot()
found = False
for child in colors_root.findall('color'):
    if child.attrib.get('name') == 'efrat_icon_bg':
        child.text = '#073D34'; found = True
if not found:
    ET.SubElement(colors_root, 'color', {'name':'efrat_icon_bg'}).text = '#073D34'
colors_tree.write(res / 'values/colors.xml', encoding='utf-8', xml_declaration=True)

ANDROID = '{http://schemas.android.com/apk/res/android}'
mt = ET.parse(manifest)
mr = mt.getroot()
existing_permissions = {p.attrib.get(ANDROID+'name') for p in mr.findall('uses-permission')}
for perm in ['android.permission.POST_NOTIFICATIONS','android.permission.RECEIVE_BOOT_COMPLETED','android.permission.VIBRATE']:
    if perm not in existing_permissions:
        ET.SubElement(mr, 'uses-permission', {ANDROID+'name':perm})
application = mr.find('application')
if application is None:
    raise SystemExit('application element missing')
application.set(ANDROID+'label', '@string/app_name')
application.set(ANDROID+'icon', '@mipmap/ic_launcher')
application.set(ANDROID+'roundIcon', '@mipmap/ic_launcher_round')

def has_component(tag, name):
    return any(x.attrib.get(ANDROID+'name') == name for x in application.findall(tag))

if not has_component('activity', '.ReminderSettingsActivity'):
    ET.SubElement(application, 'activity', {ANDROID+'name':'.ReminderSettingsActivity', ANDROID+'exported':'false', ANDROID+'label':'תזכורות אישיות'})
if not has_component('receiver', '.ReminderReceiver'):
    ET.SubElement(application, 'receiver', {ANDROID+'name':'.ReminderReceiver', ANDROID+'exported':'false'})
if not has_component('receiver', '.ReminderBootReceiver'):
    boot = ET.SubElement(application, 'receiver', {ANDROID+'name':'.ReminderBootReceiver', ANDROID+'enabled':'true', ANDROID+'exported':'true'})
    filt = ET.SubElement(boot, 'intent-filter')
    ET.SubElement(filt, 'action', {ANDROID+'name':'android.intent.action.BOOT_COMPLETED'})
    ET.SubElement(filt, 'action', {ANDROID+'name':'android.intent.action.MY_PACKAGE_REPLACED'})
mt.write(manifest, encoding='utf-8', xml_declaration=True)

s = main.read_text()
s = s.replace('val body=page("הגדרות ופרטיות","גרסה 1.2.0 · Offline","⚙️")', 'val body=page("הגדרות ופרטיות","גרסה 1.3.2 · Offline","⚙️")', 1)
anchor = 'body.addView(actionButton("⚡ עריכת פעולות מהירות"){showQuickActionsSettings()})'
insert = anchor + '\n        body.addView(actionButton("🔔 תזכורות לאוכל ולשתייה"){startActivity(Intent(this,ReminderSettingsActivity::class.java))})'
if anchor not in s:
    raise SystemExit('settings quick actions anchor not found')
s = s.replace(anchor, insert, 1)
s = s.replace('"ברוכים הבאים לבריאות שלי"', '"ברוכים הבאים לאפרת רביבו – ניהול תזונה אישית"')
old_delete = 'private fun deleteAllLocalData(){db.close();deleteDatabase(HealthDb.DB_NAME);getSharedPreferences("steps",MODE_PRIVATE).edit().clear().apply();getSharedPreferences("ui_prefs",MODE_PRIVATE).edit().clear().apply();db=HealthDb(this);showOnboarding()}'
new_delete = 'private fun deleteAllLocalData(){ReminderScheduler.cancelAll(this);db.close();deleteDatabase(HealthDb.DB_NAME);getSharedPreferences("steps",MODE_PRIVATE).edit().clear().apply();getSharedPreferences("ui_prefs",MODE_PRIVATE).edit().clear().apply();getSharedPreferences(ReminderScheduler.PREFS,MODE_PRIVATE).edit().clear().apply();db=HealthDb(this);showOnboarding()}'
if old_delete in s:
    s = s.replace(old_delete, new_delete, 1)
main.write_text(s)

print('Applied OfflineHealth 1.3.2 branding + reminder integration')
