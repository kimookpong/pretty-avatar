# รูปแบบสร้าง avatar และแค็ตตาล็อก 60 แบบ

## แนวทางภาพ

ใช้ภาพตัวอย่างเป็นแนวทางสไตล์: chibi หัวโต คอและไหล่เล็ก เส้นขอบสีน้ำตาลเข้ม ตาโตมีประกาย สีอบอุ่น เงานุ่มและแก้มชมพู อ่านรูปทรงออกที่ 112–140 px ภาพกริดเลือกตัวละครเป็น gallery ไม่ใช่ sprite sheet สำหรับ runtime ห้ามใส่ปุ่ม ชื่อ กรอบ หรือพื้นหลัง gallery ลงในภาพต้นฉบับ

สัตว์ต่างกันด้วยหู จมูก ลายขน และสีหลัก ส่วนคนต่างกันด้วยทรงผม สีผิว อายุ เสื้อผ้า และอุปกรณ์ขนาดเล็ก ให้การแสดงสีหน้าใช้มาตรฐานเดียวกัน คนทุกแบบปรับสีผิว เพศ อายุ และเสื้อผ้าได้ อาชีพไม่ผูกกับเพศหรือชาติพันธุ์ แบบเหล่านี้เป็นจุดเริ่มต้น ไม่ใช่ภาพที่สร้างเสร็จแล้ว

## คำขอที่ skill รับ

```text
/pretty-avatar สร้าง animal-tiger ชื่อ tora style colour ขนาด 140 วางใน hero
/pretty-avatar สร้าง human-curly-glasses ชื่อ mali เปลี่ยนเสื้อเป็นสีชมพู
/pretty-avatar วางแผนสัตว์ 30 แบบและคน 30 แบบ ยังไม่สร้างภาพ
```

แปลงคำขอเป็น record ก่อนสร้าง:

```json
{
  "name": "tora",
  "category": "animal",
  "preset": "animal-tiger",
  "description": "",
  "style": "colour",
  "reference": null,
  "size": 140,
  "placement": "hero"
}
```

`name` ใช้ lowercase kebab-case ไม่ซ้ำในโปรเจกต์; category เป็น animal หรือ human; preset ใช้ id ใน catalog หรือ null สำหรับ custom; description เพิ่มหรือแทนรายละเอียดตามคำขอ; reference เป็น path ภาพที่ผู้ใช้ให้หรือ null; style ใช้ค่าที่ prompts.py รองรับ ถ้ารายละเอียดใหม่ขัดกับ preset ให้แก้ description ที่รวมแล้วและใช้ --describe โดยไม่ส่ง --preset ห้ามเดาคุณลักษณะจากภาพที่มองไม่ชัด

## ฟอร์แมตไฟล์

ต่อหนึ่งตัวละคร สร้างสอง PNG แบบ RGBA ขนาดจัตุรัสเท่ากัน หารสามลงตัว แนะนำ 1536×1536 (ช่องละ 512 px) หากเครื่องมือส่งขนาดอื่นกลับมาให้เก็บ alpha และสัดส่วนเดิมไว้ build.py แบ่งช่องด้วยการปัดเศษขอบกริดและประกอบเป็น atlas จัตุรัสให้อัตโนมัติ ไม่ยืดทั้งภาพจนตัวละครผิดสัดส่วน ทุกช่องมีขอบว่างและตัวละครครบ

Directions เรียงตามมุมของผู้ชม:

| up-left | up | up-right |
| --- | --- | --- |
| left | center | right |
| down-left | down | down-right |

Reactions เรียงดังนี้:

| blink | heart | sparkle |
| --- | --- | --- |
| surprised | starstruck | bashful |
| sleepy | dizzy | grin |

ลำตัวหันตรงและอยู่ตำแหน่งเดิมทุกช่อง เปลี่ยนเฉพาะหัวใน directions และสีหน้าใน reactions ใช้ directions ของตัวเดียวกันเป็น reference เมื่อสร้าง reactions สีผิว ลายขน เสื้อ และสเกลต้องตรงกัน หูสูง หมวก จมูกยาว และผมต้องอยู่ในช่องครบ; ถ้าไม่พอให้ย่อทั้งตัวอย่างเท่ากัน ไม่ตัดเฉพาะอวัยวะ

```text
characters/<name>/directions.png
characters/<name>/reactions.png
public/avatars/<name>-directions.webp
public/avatars/<name>-reactions.webp
```

Build เดิมใช้ tile 320 จึงได้ WebP 960×960 สองแผ่น ตรวจ alpha, shoulder spread, jump ≤2 px ที่ขนาดแสดงผล 140, palette ≥0.25 และ width change ≤10% ตรวจด้วยตาเพิ่มว่าหันถูกทิศ ตัวตนเหมือนกันและไม่มีช่องถูกตัด ตัวเลขไม่ยืนยันคุณภาพศิลป์หรือความถูกต้องของสีหน้า หากใช้ขนาดแสดงผลใหญ่กว่า 140 ให้รัน verify.py --size ตามขนาดจริงด้วย

## การเรียกใช้

```bash
python3 <skill-dir>/scripts/catalog.py --list --category animal
python3 <skill-dir>/scripts/catalog.py human-curly-glasses
python3 <skill-dir>/scripts/avatar.py tora --preset animal-tiger --style colour
python3 <skill-dir>/scripts/avatar.py mali --preset human-curly-glasses --describe "wearing a pink top"
```

คำสั่ง avatar.py ใช้ API ส่วน built-in image tool ให้ใช้ description จาก catalog กับ prompts.py และ workflow เดิม `--skip-generate` ไม่เรียก API สำหรับคำขอ catalog/วางแผนให้ส่งแผนเท่านั้น สำหรับ batch ให้ทำตัวอย่างสัตว์หนึ่งและคนหนึ่งก่อนเพื่อเช็คสไตล์ จากนั้นทำทีละตัวพร้อม checkpoint ไม่สร้างภาพ 120 แผ่นเพียงเพราะผู้ใช้ขอออกแบบรายการ 60 แบบ แสดงรายการที่ผ่านและรายการที่ต้องแก้ตามจริง

## Batch workflow

```bash
python3 <skill-dir>/scripts/collection.py prepare
python3 <skill-dir>/scripts/collection.py status
python3 <skill-dir>/scripts/collection.py build --id animal-tiger
# After inspecting both atlases visually:
python3 <skill-dir>/scripts/collection.py build --id animal-tiger --visual-reviewed
```

`prepare` writes prompts under `characters/<id>/` and a manifest under
`characters/collection/manifest.json`, preserving previous review and build state.
Generate one image per prompt with the built-in tool and copy its result to
`directions.png` or `reactions.png`. Reactions must reference that character's actual
directions PNG. Build failures are recorded without replacing the public atlases.
Only `verified` characters should enter the ready-made gallery. Keep source files
and the manifest locally; they are ignored by Git. Do not claim an ignored manifest
is shared with other developers. Commit a delivery summary and built assets instead.

## รายการแบบสำหรับสร้างใหม่

แหล่งข้อมูลที่สคริปต์อ่านคือ `catalog.json` แบบในตารางยังไม่มี atlases พร้อมดาวน์โหลด ใช้ `characters.md` สำหรับหกตัวที่มีไฟล์อยู่จริง

| preset | แบบ | รายละเอียดเริ่มต้น |
| --- | --- | --- |
| `animal-cat` | แมว | a chibi orange tabby cat, cream muzzle, short whiskers, teal top |
| `animal-dog` | สุนัข | a chibi golden puppy, floppy ears, cream muzzle, blue top |
| `animal-rabbit` | กระต่าย | a chibi white rabbit, upright pink-lined ears, lilac top |
| `animal-bear` | หมี | a chibi brown bear, round ears, cream muzzle, yellow top |
| `animal-panda` | แพนด้า | a chibi panda, black eye patches, round ears, mint top |
| `animal-frog` | กบ | a chibi green frog, rounded raised eyes, coral top |
| `animal-chick` | ลูกเจี๊ยบ | a chibi yellow chick, tiny orange beak, small tuft, blue top |
| `animal-fox` | จิ้งจอก | a chibi orange fox, cream cheeks, dark ear tips, forest-green top |
| `animal-tiger` | เสือ | a chibi orange tiger, black stripes, white muzzle, green eyes, sage-green top |
| `animal-lion` | สิงโต | a chibi tan lion, compact brown mane, round ears, rust top |
| `animal-hedgehog` | เม่น | a chibi brown hedgehog, compact rounded spines, cream face, olive top |
| `animal-koala` | โคอาลา | a chibi grey koala, fluffy round ears, charcoal nose, sky-blue top |
| `animal-mouse` | หนู | a chibi grey mouse, round pink-lined ears, tiny pink nose, rose top |
| `animal-otter` | นาก | a chibi brown otter, cream muzzle, small round ears, turquoise top |
| `animal-owl` | นกฮูก | a chibi brown owl, cream facial disc, amber eyes, ochre top |
| `animal-penguin` | เพนกวิน | a chibi black and white penguin, small orange beak, pink cheeks, navy top |
| `animal-pug` | ปั๊ก | a chibi fawn pug, dark muzzle, folded ears, mustard top |
| `animal-raccoon` | แรคคูน | a chibi grey raccoon, dark eye mask, pointed ears, teal crew-neck shirt |
| `animal-red-panda` | แพนด้าแดง | a chibi rust-red panda, white eyebrow patches, dark cheek tips, sage top |
| `animal-sheep` | แกะ | a chibi cream sheep, compact wool cap, grey floppy ears, pink top |
| `animal-sloth` | สลอธ | a chibi tan sloth, dark eye patches, rounded shaggy head, sand top |
| `animal-hamster` | แฮมสเตอร์ | a chibi golden hamster, plump cream cheeks, tiny round ears, peach top |
| `animal-squirrel` | กระรอก | a chibi red-brown squirrel, pointed tufted ears, cream cheeks, leaf-green top |
| `animal-deer` | กวาง | a chibi tan deer, white cheek spots, short compact antler buds, sage top |
| `animal-giraffe` | ยีราฟ | a chibi golden giraffe, brown patches, small ossicones, short visible neck, mint top |
| `animal-elephant` | ช้าง | a chibi grey elephant, rounded ears kept inside cell, short curled trunk, blue top |
| `animal-hippo` | ฮิปโป | a chibi lavender-grey hippo, round muzzle, small ears, coral top |
| `animal-cow` | วัว | a chibi white cow, black patches, short horns, pink muzzle, denim-blue top |
| `animal-duck` | เป็ด | a chibi cream duck, rounded orange bill, small head tuft, yellow top |
| `animal-seal` | แมวน้ำ | a chibi silver-grey seal, round dark eyes, short whiskers, ocean-blue top |
| `human-bun` | ผมมวย | a chibi young adult woman, light skin, brown hair in a compact bun, pink ribbon, blush top |
| `human-bearded` | หนวดเครา | a chibi adult man, olive skin, short dark hair, neat beard, mustard top |
| `human-builder` | ช่างก่อสร้าง | a chibi adult woman, brown skin, compact yellow safety helmet, charcoal work top |
| `human-cap` | หมวกแก๊ป | a chibi young adult man, light skin, short chestnut hair, compact red cap, green top |
| `human-chef` | เชฟ | a chibi adult man, medium skin, neat moustache, compact white chef hat, white coat and red collar |
| `human-curly-glasses` | ผมหยิกและแว่น | a chibi adult woman, light skin, short auburn curls above shoulders, round glasses, teal top |
| `human-grandfather` | คุณปู่ | a chibi older man, light skin, short silver hair, round glasses, olive sweater and white collar |
| `human-grandmother` | คุณย่า | a chibi older woman, light skin, silver hair in a low compact bun, round glasses, rose cardigan |
| `human-hijab` | ฮิญาบ | a chibi adult woman, warm brown skin, simple fitted lavender hijab hood ending at the jawline, navy high-neck top, no loose scarf folds over the chest |
| `human-black-glasses` | แว่นดำ | a chibi adult man, medium skin, short black hair, rectangular dark glasses, stubble, black top |
| `human-nurse` | พยาบาล | a chibi adult woman, light skin, short black bob, compact white nurse cap, mint uniform |
| `human-headscarf` | ผ้าโพกศีรษะ | a chibi adult woman, dark skin, fitted red headscarf, navy top with white collar |
| `human-pilot` | นักบิน | a chibi adult woman, dark skin, compact auburn curls, small goggles resting on head, teal jacket |
| `human-turban` | ผ้าโพกแบบเทอร์บัน | a chibi adult man, brown skin, compact burgundy turban, neat black beard, grey top |
| `human-beanie` | หมวกไหมพรม | a chibi young adult woman, light skin, short black hair tucked under sage beanie, charcoal top |
| `human-wizard` | พ่อมด | a chibi older man, light skin, short white beard above chest, compact purple wizard hat, plum top |
| `human-astronaut` | นักบินอวกาศ | a chibi adult woman, dark skin, compact white space helmet with open clear visor, white suit collar |
| `human-bald` | ศีรษะล้าน | a chibi adult man, brown skin, bald head, gentle eyebrows, blue crew-neck top |
| `human-afro` | ผมแอฟโฟร | a chibi adult woman, dark skin, compact rounded afro, small gold stud earrings, yellow top |
| `human-pixie` | ผมพิกซี | a chibi adult woman, fair skin, short black pixie haircut, coral top |
| `human-bob` | ผมบ๊อบ | a chibi adult woman, medium skin, straight chin-length brown bob above shoulders, lavender top |
| `human-ponytail` | ผมหางม้า | a chibi adult woman, tan skin, black ponytail tied behind head away from shoulders, mint top |
| `human-freckles` | กระ | a chibi young adult person, fair skin, short ginger hair, light freckles, sky-blue top |
| `human-silver-bob` | ผมบ๊อบสีเงิน | a chibi older woman, brown skin, short silver bob above shoulders, teal top |
| `human-locs` | ผมล็อกมัดขึ้น | a chibi adult man, dark skin, short locs gathered behind head, cream top |
| `human-doctor` | แพทย์ | a chibi adult man, medium skin, short dark hair, round glasses, white coat over blue collar |
| `human-artist` | ศิลปิน | a chibi adult woman, olive skin, short wavy dark hair, compact navy beret, rust top |
| `human-student` | นักเรียน | a chibi teen person, medium skin, short neat brown hair, round glasses, navy school sweater |
| `human-hoodie` | เสื้อฮู้ด | a chibi young adult person, dark skin, close-cropped black hair, lilac hoodie with hood down |
| `human-blond` | ผมบลอนด์ | a chibi adult man, fair skin, short swept blond hair, clean-shaven face, sage top |
