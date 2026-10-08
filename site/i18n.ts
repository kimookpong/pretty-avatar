export type Lang = 'th' | 'en'

type Row = readonly [string, string, string]

export const TEXT = {
  en: {
    nav: { cast: 'Cast', play: 'Playground', how: 'How it works', install: 'Install' },
    eyebrow: 'React component + AI agent skill',
    title: ['Avatars that ', 'look back', '.'],
    lead: 'Drop a little character on your page. It turns its head to follow the reader’s cursor, and reacts when they poke it.',
    tabs: { npm: 'npm', skill: 'agent skill' },
    facts: ['zero dependencies', '~10 kB', 'SSR-safe', "'use client'"],
    bubble: {
      looking: 'looking',
      feeling: 'feeling',
      idle: 'move your cursor around me',
      touch: 'tap me',
    },
    castTitle: 'Class photo',
    castLead: 'Everyone is watching your cursor. Pick one — the page takes on their colour.',
    picked: 'picked',
    download: 'download',
    howTitle: 'Under the hood',
    howLead: 'Two 3×3 sprite sheets. The highlighted cell is the one on screen right now — move the cursor or click the avatar above and watch it change.',
    directionsSheet: 'directions',
    reactionsSheet: 'reactions',
    steps: [
      ['Draw', 'An image model draws nine head turns, then nine expressions using the first sheet as a reference.'],
      ['Align', 'A build step lines up the shoulders in all eighteen cells and measures how far the body would move on screen.'],
      ['Track', 'The component picks a cell from the angle to the cursor. Only background-position changes — no canvas, no animation library.'],
    ],
    playTitle: 'Playground',
    playLead: 'Every prop, live. The snippet writes itself.',
    never: 'never',
    lastBoop: 'last boop',
    copy: 'Copy',
    copied: 'Copied!',
    installTitle: 'Install',
    installSteps: [
      ['Add the package', ''],
      ['Put two sheets in public/avatars', 'Download them from the class photo above, or draw your own.'],
      ['Render it', ''],
    ],
    propsTitle: 'Props',
    props: [
      ['name', '—', 'reads /avatars/<name>-directions.webp and -reactions.webp'],
      ['basePath', "'/avatars'", 'where the sheets live, with name'],
      ['directions · reactions', '—', 'the two sheets as paths or imports, instead of name'],
      ['size', '140', 'px, square'],
      ['label', "'avatar'", 'what a screen reader calls it'],
      ['tracking', 'true', 'turn the head toward the pointer'],
      ['deadZone', '70', 'px around the centre where it looks straight ahead'],
      ['interactive', 'true', 'react to clicks; false renders a plain image'],
      ['sleepAfter', '20000', 'ms of stillness before it dozes off; 0 never'],
      ['onBoop', '—', '(reaction) => void, on every click'],
    ] as readonly Row[],
    makeTitle: 'Draw your own with /pretty-avatar',
    makeLead: 'One command installs the skill into every coding agent on your machine.',
    makeAsk: 'Then just ask:',
    asks: [
      '/pretty-avatar put mochi on my homepage',
      '/pretty-avatar a chibi shiba with a red scarf',
      '/pretty-avatar make one that looks like me  📎 photo.jpg',
      '/pretty-avatar a brown owl, pastel style',
    ],
    makeNote: 'It draws, aligns, checks the character never jumps, and puts <Pavatar /> on your page. Drawing uses your agent’s own image tool, or the OpenAI Images API.',
    worksWith: 'Works with',
    andMore: '+ ~70 more',
    prompts: 'No agent? Paste the prompts into any chat app',
    footer: 'MIT licensed · made with care · inspired by page-mascot',
    lang: 'ไทย',
  },
  th: {
    nav: { cast: 'ตัวละคร', play: 'ลองเล่น', how: 'ทำงานอย่างไร', install: 'ติดตั้ง' },
    eyebrow: 'React component + skill สำหรับ AI agent',
    title: ['อวตาร์ที่', 'มองกลับ', 'มาหาคุณ'],
    lead: 'วางตัวละครน่ารักไว้บนหน้าเว็บ มันจะหันหัวมองตามเคอร์เซอร์ของผู้อ่าน และมีปฏิกิริยาเมื่อถูกจิ้ม',
    tabs: { npm: 'npm', skill: 'agent skill' },
    facts: ['ไม่มี dependency', '~10 kB', 'รองรับ SSR', "'use client'"],
    bubble: {
      looking: 'กำลังมอง',
      feeling: 'รู้สึก',
      idle: 'ลองขยับเมาส์รอบ ๆ ตัวฉันสิ',
      touch: 'แตะฉันดูสิ',
    },
    castTitle: 'รูปหมู่',
    castLead: 'ทุกตัวกำลังมองเคอร์เซอร์ของคุณ เลือกตัวที่ชอบ แล้วทั้งหน้าจะเปลี่ยนเป็นสีของตัวนั้น',
    picked: 'เลือกอยู่',
    download: 'ดาวน์โหลด',
    howTitle: 'เบื้องหลัง',
    howLead: 'sprite sheet ขนาด 3×3 สองแผ่น ช่องที่ไฮไลต์คือภาพที่กำลังแสดงอยู่ตอนนี้ ลองขยับเมาส์หรือคลิกอวตาร์ด้านบนแล้วดูมันเปลี่ยน',
    directionsSheet: 'ทิศทาง',
    reactionsSheet: 'สีหน้า',
    steps: [
      ['วาด', 'โมเดลสร้างภาพวาดการหันหัว 9 ทิศ แล้ววาดสีหน้า 9 แบบโดยใช้แผ่นแรกเป็นภาพอ้างอิง'],
      ['จัดเรียง', 'ขั้นตอน build จัดไหล่ให้ตรงกันทั้ง 18 ช่อง และวัดว่าตัวละครจะขยับบนจอกี่พิกเซล'],
      ['ติดตาม', 'component เลือกช่องจากมุมที่เคอร์เซอร์อยู่ เปลี่ยนแค่ background-position ไม่มี canvas ไม่มีไลบรารีแอนิเมชัน'],
    ],
    playTitle: 'ลองเล่น',
    playLead: 'ปรับทุก prop ได้สด ๆ โค้ดเขียนตัวเองให้',
    never: 'ไม่หลับ',
    lastBoop: 'จิ้มล่าสุด',
    copy: 'คัดลอก',
    copied: 'คัดลอกแล้ว!',
    installTitle: 'ติดตั้ง',
    installSteps: [
      ['เพิ่ม package', ''],
      ['วางชีตสองไฟล์ไว้ที่ public/avatars', 'ดาวน์โหลดจากรูปหมู่ด้านบน หรือวาดตัวละครของคุณเอง'],
      ['แสดงผล', ''],
    ],
    propsTitle: 'Props',
    props: [
      ['name', '—', 'อ่าน /avatars/<name>-directions.webp และ -reactions.webp'],
      ['basePath', "'/avatars'", 'โฟลเดอร์ที่เก็บชีต ใช้คู่กับ name'],
      ['directions · reactions', '—', 'ชีตสองไฟล์ (path หรือ import) ใช้แทน name'],
      ['size', '140', 'ขนาด px (สี่เหลี่ยมจัตุรัส)'],
      ['label', "'avatar'", 'ชื่อที่โปรแกรมอ่านหน้าจอใช้เรียก'],
      ['tracking', 'true', 'หันหัวตามเคอร์เซอร์'],
      ['deadZone', '70', 'รัศมี px รอบกึ่งกลางที่จะมองตรง'],
      ['interactive', 'true', 'มีปฏิกิริยาเมื่อคลิก; false แสดงเป็นรูปเฉย ๆ'],
      ['sleepAfter', '20000', 'มิลลิวินาทีที่นิ่งก่อนจะหลับ; 0 คือไม่หลับ'],
      ['onBoop', '—', '(reaction) => void เรียกทุกครั้งที่คลิก'],
    ] as readonly Row[],
    makeTitle: 'วาดตัวละครของคุณเองด้วย /pretty-avatar',
    makeLead: 'คำสั่งเดียว ติดตั้ง skill ให้ coding agent ทุกตัวในเครื่องของคุณ',
    makeAsk: 'แล้วสั่งได้เลย:',
    asks: [
      '/pretty-avatar ใส่ mochi ไว้บนหน้าแรก',
      '/pretty-avatar สุนัขชิบะใส่ผ้าพันคอสีแดง',
      '/pretty-avatar วาดให้เหมือนฉัน  📎 photo.jpg',
      '/pretty-avatar นกฮูกสีน้ำตาล สไตล์ pastel',
    ],
    makeNote: 'agent จะวาด จัดเรียง ตรวจว่าตัวละครไม่กระโดด แล้ววาง <Pavatar /> ลงหน้าเว็บให้ การวาดใช้เครื่องมือสร้างภาพของ agent เอง หรือ OpenAI Images API',
    worksWith: 'ใช้ได้กับ',
    andMore: '+ อีกราว 70 ตัว',
    prompts: 'ไม่มี agent? นำ prompt ไปวางในแอปแชตใดก็ได้',
    footer: 'สัญญาอนุญาต MIT · ได้แรงบันดาลใจจาก page-mascot',
    lang: 'EN',
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
