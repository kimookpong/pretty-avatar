export type Lang = 'th' | 'en'

export const TEXT = {
  en: {
    tagline: 'A cute avatar for the top of your page. It follows the reader’s cursor and reacts when they poke it.',
    useOne: (count: number) => `Use one of the ${count}`,
    makeOwn: 'Make your own',
    hint: 'Move your cursor around. Click it. Click it a lot.',
    touchHint: 'Tap it.',
    playground: 'Playground',
    playgroundLead: 'Every prop, live. The code below updates as you go.',
    size: 'size',
    tracking: 'tracking',
    deadZone: 'deadZone',
    interactive: 'interactive',
    sleepAfter: 'sleepAfter',
    never: 'never',
    copy: 'Copy',
    copied: 'Copied',
    lastBoop: 'last boop',
    cast: 'The cast',
    castLead: 'Pick one to try it above. Each is two small WebP files.',
    use: 'Try it',
    download: 'Download sheets',
    how: 'How it works',
    howLead:
      'Each character is two 3×3 sprite sheets: nine head directions, and nine expressions. The angle to the cursor picks a cell on the first; a click shows cells from the second for half a second.',
    howDetails: [
      ['No animation library', 'The component only moves background-position. No canvas, no per-frame JavaScript.'],
      ['Steady head', 'A dead zone and a little hysteresis stop the head flickering when the cursor rests near an edge.'],
      ['Aligned sheets', 'The build pipeline lines up the shoulders in all eighteen cells, so it never jumps when clicked.'],
      ['Polite', 'Tracking turns off on touch screens, the squash honours reduced motion, and it is a real button.'],
    ],
    directionsSheet: 'directions sheet',
    reactionsSheet: 'reactions sheet',
    install: 'Install',
    installLead: 'Put the sheets in public/avatars, then:',
    makeTitle: 'Draw your own',
    makeLead: 'Install the skill for your coding agent:',
    makeAsk: 'Then ask it:',
    makeNote:
      'It draws the nine directions and nine expressions, builds and aligns the two sheets, checks the character does not jump, and puts <Pavatar /> on your page. Drawing goes through the OpenAI Images API (set OPENAI_API_KEY), or any agent with its own image tool.',
    promptsLink: 'Or paste the prompts into any chat app',
    props: 'Props',
    propsRows: [
      ['name', '—', 'reads /avatars/<name>-directions.webp and -reactions.webp'],
      ['basePath', "'/avatars'", 'where the sheets are served from, with name'],
      ['directions, reactions', '—', 'the two sheet paths or imported images, instead of name'],
      ['size', '140', 'px, square'],
      ['label', "'avatar'", 'what a screen reader calls it'],
      ['tracking', 'true', 'turn the head toward the pointer'],
      ['deadZone', '70', 'px around the centre where it looks straight ahead'],
      ['interactive', 'true', 'react to clicks; false renders a plain image'],
      ['sleepAfter', '20000', 'ms without the pointer moving before it dozes; 0 never'],
      ['onBoop', '—', '(reaction) => void, on every click'],
    ],
    footer: 'MIT licensed. Inspired by page-mascot.',
    lang: 'ภาษาไทย',
  },
  th: {
    tagline: 'อวตาร์น่ารักสำหรับหัวเว็บของคุณ หันหน้าตามเคอร์เซอร์ของผู้อ่าน และมีปฏิกิริยาเมื่อถูกจิ้ม',
    useOne: (count: number) => `เลือกจาก ${count} ตัว`,
    makeOwn: 'สร้างตัวเอง',
    hint: 'ลองขยับเมาส์ไปรอบ ๆ คลิกดู คลิกรัว ๆ ก็ได้',
    touchHint: 'ลองแตะดู',
    playground: 'ลองเล่น',
    playgroundLead: 'ปรับทุก prop ได้สด ๆ โค้ดด้านล่างจะอัปเดตตาม',
    size: 'size',
    tracking: 'tracking',
    deadZone: 'deadZone',
    interactive: 'interactive',
    sleepAfter: 'sleepAfter',
    never: 'ไม่หลับ',
    copy: 'คัดลอก',
    copied: 'คัดลอกแล้ว',
    lastBoop: 'จิ้มล่าสุด',
    cast: 'ตัวละคร',
    castLead: 'เลือกตัวที่ชอบเพื่อลองด้านบน แต่ละตัวคือไฟล์ WebP เล็ก ๆ สองไฟล์',
    use: 'ลองตัวนี้',
    download: 'ดาวน์โหลดชีต',
    how: 'ทำงานอย่างไร',
    howLead:
      'ตัวละครหนึ่งตัวคือ sprite sheet ขนาด 3×3 สองแผ่น: ทิศทางหัว 9 ทิศ และสีหน้า 9 แบบ มุมระหว่างตัวละครกับเคอร์เซอร์จะเลือกช่องจากแผ่นแรก เมื่อคลิกจะแสดงช่องจากแผ่นที่สองครู่หนึ่ง',
    howDetails: [
      ['ไม่ใช้ไลบรารีแอนิเมชัน', 'component แค่เลื่อน background-position ไม่มี canvas ไม่มี JavaScript ทำงานทุกเฟรม'],
      ['หัวไม่สั่น', 'มี dead zone และ hysteresis เล็กน้อย หัวจึงไม่กระพริบไปมาเมื่อเคอร์เซอร์อยู่ตรงรอยต่อ'],
      ['ชีตตรงกันเป๊ะ', 'pipeline จัดไหล่ให้ตรงกันทั้ง 18 ช่อง ตัวละครจึงไม่กระโดดเวลาคลิก'],
      ['สุภาพกับผู้ใช้', 'ปิดการติดตามบนจอสัมผัส เคารพการตั้งค่าลดการเคลื่อนไหว และเป็นปุ่มจริงที่กดด้วยคีย์บอร์ดได้'],
    ],
    directionsSheet: 'ชีตทิศทาง',
    reactionsSheet: 'ชีตสีหน้า',
    install: 'ติดตั้ง',
    installLead: 'วางชีตไว้ที่ public/avatars แล้ว:',
    makeTitle: 'วาดตัวละครของคุณเอง',
    makeLead: 'ติดตั้ง skill ให้ coding agent ของคุณ:',
    makeAsk: 'แล้วสั่งว่า:',
    makeNote:
      'มันจะวาดทิศทาง 9 แบบและสีหน้า 9 แบบ ประกอบและจัดสองชีตให้ตรงกัน ตรวจว่าตัวละครไม่กระโดด แล้ววาง <Pavatar /> ลงหน้าเว็บให้ การวาดใช้ OpenAI Images API (ตั้งค่า OPENAI_API_KEY) หรือ agent ที่มีเครื่องมือสร้างภาพในตัว',
    promptsLink: 'หรือนำ prompt ไปวางในแอปแชตใดก็ได้',
    props: 'Props',
    propsRows: [
      ['name', '—', 'อ่าน /avatars/<name>-directions.webp และ -reactions.webp'],
      ['basePath', "'/avatars'", 'โฟลเดอร์ที่เก็บชีต ใช้คู่กับ name'],
      ['directions, reactions', '—', 'path ของสองชีตหรือรูปที่ import มา ใช้แทน name'],
      ['size', '140', 'ขนาดเป็น px (สี่เหลี่ยมจัตุรัส)'],
      ['label', "'avatar'", 'ชื่อที่โปรแกรมอ่านหน้าจอใช้เรียก'],
      ['tracking', 'true', 'หันหัวตามเคอร์เซอร์'],
      ['deadZone', '70', 'รัศมี px รอบกึ่งกลางที่จะมองตรง'],
      ['interactive', 'true', 'มีปฏิกิริยาเมื่อคลิก; false จะแสดงเป็นรูปเฉย ๆ'],
      ['sleepAfter', '20000', 'มิลลิวินาทีที่เมาส์ไม่ขยับก่อนจะหลับ; 0 คือไม่หลับ'],
      ['onBoop', '—', '(reaction) => void เรียกทุกครั้งที่คลิก'],
    ],
    footer: 'สัญญาอนุญาต MIT ได้แรงบันดาลใจจาก page-mascot',
    lang: 'English',
  },
} as const

export type Text = (typeof TEXT)[Lang]

export function initialLang(): Lang {
  try {
    const saved = localStorage.getItem('pretty-avatar-lang')
    if (saved === 'th' || saved === 'en') {
      return saved
    }
  } catch {}
  return navigator.language?.toLowerCase().startsWith('th') ? 'th' : 'en'
}

export function saveLang(lang: Lang) {
  try {
    localStorage.setItem('pretty-avatar-lang', lang)
  } catch {}
}
