<img src=".github/assets/cast.png" width="480" alt="ตัวละครสำเร็จรูปทั้ง 6 ตัว">

# pretty-avatar

อวตาร์น่ารักสำหรับหัวเว็บของคุณ หันหน้าตามเคอร์เซอร์ของผู้อ่าน และมีปฏิกิริยาเมื่อถูกจิ้ม

**[ดูตัวอย่างจริง &rarr;](https://kimookpong.github.io/pretty-avatar/)** · [English](README.md)

## ติดตั้ง

```bash
npm i pretty-avatar
```

## ใช้ตัวละครสำเร็จรูป

ดาวน์โหลดชีตสองไฟล์ของตัวละครที่ชอบจาก[หน้าตัวอย่าง](https://kimookpong.github.io/pretty-avatar/#cast)
ไปไว้ที่ `public/avatars` แล้ว:

```tsx
import { Pavatar } from 'pretty-avatar'

<Pavatar name="mochi" />
```

`name` จะอ่านไฟล์ `/avatars/mochi-directions.webp` และ `/avatars/mochi-reactions.webp`
ถ้าเก็บไว้ที่อื่นให้ใส่ `basePath` หรือส่งชีตสองไฟล์เองก็ได้ (เป็น path หรือรูปที่ import มา):

```tsx
<Pavatar name="mochi" basePath="/static/avatars" />
<Pavatar directions={directionsUrl} reactions={reactionsUrl} />
```

component ประกาศ `'use client'` ไว้แล้ว จึงใช้ใน Next.js App Router ได้ทันที

## Props

| prop | ค่าเริ่มต้น | |
| --- | --- | --- |
| `name` | | อ่าน `${basePath}/${name}-directions.webp` และ `-reactions.webp` |
| `basePath` | `'/avatars'` | โฟลเดอร์ที่เก็บชีต ใช้คู่กับ `name` |
| `directions`, `reactions` | | ชีตสองไฟล์ ใช้แทน `name` |
| `size` | `140` | ขนาดเป็น px (สี่เหลี่ยมจัตุรัส) |
| `label` | `'avatar'` | ชื่อที่โปรแกรมอ่านหน้าจอใช้เรียก |
| `tracking` | `true` | หันหัวตามเคอร์เซอร์ |
| `deadZone` | `70` | รัศมี px รอบกึ่งกลางที่จะมองตรง |
| `interactive` | `true` | มีปฏิกิริยาเมื่อคลิก; `false` จะแสดงเป็นรูปเฉย ๆ |
| `sleepAfter` | `20000` | มิลลิวินาทีที่เมาส์ไม่ขยับก่อนจะหลับ; `0` คือไม่หลับ |
| `onBoop` | | `(reaction) => void` เรียกทุกครั้งที่คลิก |
| `className`, `style` | | ใส่ที่ element ชั้นนอกสุด |

คลิกแล้วจะกะพริบตา ตามด้วยหัวใจ ประกายดาว ตาเป็นดาว ยิ้มกว้าง หรือเขินอาย
จิ้มรัว ๆ สี่ครั้งจะมึนหัว ปล่อยไว้นาน ๆ จะหลับ

ปิดการติดตามอัตโนมัติบนอุปกรณ์ที่ไม่มีเมาส์ (และเปิดกลับเมื่อเสียบเมาส์) แอนิเมชันตอนคลิกเคารพ
`prefers-reduced-motion` และเป็น `<button>` จริงที่กดด้วยคีย์บอร์ดได้

## วาดตัวละครของคุณเองด้วย `/pretty-avatar`

ติดตั้ง skill ให้ coding agent ทุกตัวที่ CLI [skills](https://github.com/vercel-labs/skills) รองรับ
ทั้ง Claude Code, Codex, Windsurf, Cline, Roo Code, Kiro, Qwen Code, Goose, Amp, Continue
และอีกราวเจ็ดสิบตัว:

```bash
npx skills add kimookpong/pretty-avatar --skill pretty-avatar --agent '*' --global --yes
```

แล้วสั่ง agent ได้เลย:

```
/pretty-avatar ใส่แมว mochi ไว้บนหัวเว็บ
/pretty-avatar สุนัขชิบะสีส้มใส่ผ้าพันคอสีแดง
/pretty-avatar วาดให้เหมือนฉัน        [แนบรูป]
/pretty-avatar นกฮูกสีน้ำตาล สไตล์ pastel
```

`--agent '*'` คือติดตั้งให้ทุกตัว ถ้าต้องการเฉพาะบางตัวให้ระบุชื่อแทน (`--agent claude-code codex`)
และถ้าไม่ใส่ `--global` จะติดตั้งเฉพาะในโปรเจกต์ปัจจุบัน

agent จะวาดทิศทางหัว 9 แบบและสีหน้า 9 แบบ ประกอบเป็นชีตสองแผ่นที่จัดให้ตรงกัน
ตรวจว่าตัวละครไม่กระโดดเวลาสลับภาพ แล้ววาง `<Pavatar />` ลงในหน้าเว็บให้

การวาดต้องใช้โมเดลสร้างภาพ agent ที่มีเครื่องมือสร้างภาพในตัวจะใช้ของตัวเอง
ส่วน agent อื่นทั้งหมดจะวาดผ่าน OpenAI Images API:

```bash
export OPENAI_API_KEY=sk-...
pip install pillow numpy scipy openai
```

ถ้า agent ของคุณไม่รองรับ skill ใช้ `npx skills use kimookpong/pretty-avatar@pretty-avatar`
เพื่อพิมพ์ skill ออกมาเป็น prompt แล้วนำไปวางได้ หรือนำ[prompt](skills/pretty-avatar/reference/prompts.md)
ไปวางในแอปแชตใดก็ได้โดยไม่ต้องใช้ agent เลย

สไตล์ที่มี: `colour` (ค่าเริ่มต้น), `pastel`, `ink`, `watercolour`, `pixel`, `clay`

## ทำงานอย่างไร

ตัวละครหนึ่งตัวคือ sprite sheet ขนาด 3×3 สองแผ่น: ทิศทางหัว 9 ทิศ และสีหน้า 9 แบบ

![ชีตสองแผ่นของตัวละครหนึ่งตัว](.github/assets/sheets.png)

มุมจากอวตาร์ไปยังเคอร์เซอร์จะเลือกช่องจากชีตทิศทาง มี dead zone ให้หัวหันตรงเมื่อเคอร์เซอร์อยู่ใกล้
และมี hysteresis เล็กน้อยกันหัวกระพริบไปมาตรงรอยต่อ เมื่อคลิกจะแสดงช่องจากชีตสีหน้าครึ่งวินาที
component แค่เลื่อน `background-position` ไม่มี canvas ไม่มีไลบรารีแอนิเมชัน

โมเดลสร้างภาพไม่เคยวาดสองชีตออกมาเหมือนกันเป๊ะ ขั้นตอน build
(`skills/pretty-avatar/scripts/build.py`) จึงจัดไหล่ให้ตรงกันทั้ง 18 ช่อง ปรับสเกลชีตที่สองให้เท่าชีตแรก
และ `verify.py` วัดว่าตัวละครจะขยับบนจอกี่พิกเซลก่อนนำไปใช้จริง ดูความหมายของแต่ละการตรวจได้ที่
[troubleshooting](skills/pretty-avatar/reference/troubleshooting.md)

## พัฒนาต่อ

```bash
npm install
npm run dev            # เว็บตัวอย่าง
npm test               # ทดสอบ component
npm run test:pipeline  # ทดสอบ pipeline Python (ต้องมี pillow, numpy, scipy)
npm run samples        # วาดตัวละครตัวอย่างใหม่ลง public/avatars
```

`src/` คือตัว package ส่วน `skills/pretty-avatar/Pavatar.tsx` เป็นสำเนาไฟล์เดียวสำหรับโปรเจกต์ที่
คัดลอกไฟล์แทนการติดตั้ง สร้างด้วย `npm run sync:skill`

เว็บตัวอย่าง deploy ขึ้น GitHub Pages อัตโนมัติจาก branch `main` (`.github/workflows/pages.yml`)

## สัญญาอนุญาต

MIT © kimookpong ได้แรงบันดาลใจจาก [page-mascot](https://github.com/nilbuild/page-mascot)
