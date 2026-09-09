// 編集済みHTMLから、カード表・裏を91×55mmの高解像度PNGとして書き出す。
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');const {chromium}=require('playwright');
(async()=>{
 const source=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:1200},deviceScaleFactor:4});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(source).href);await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>{document.activeElement?.blur();document.body.classList.remove('move-mode');document.querySelector('#codex-browser-sidebar-comments-root')?.remove();const c=document.querySelector('#cutLines');if(c)c.checked=false;window.dispatchEvent(new Event('beforeprint'));});
  await page.emulateMedia({media:'print'});
  await page.addStyleTag({content:'.print-cell::after{display:none!important}.card [contenteditable],.card [data-movable]{outline:none!important}'});
  const meta=await page.evaluate(()=>({
   school:(document.querySelector('#schoolFront')?.textContent||'').trim(),
   tagline:(document.querySelector('#taglineFront')?.textContent||'').trim(),
   photoSet:!!document.querySelector('#photo')?.getAttribute('src'),
   qrDetailsSet:!!document.querySelector('#qrDetails')?.getAttribute('src'),
   qrSet:!!document.querySelector('#qr')?.getAttribute('src'),
   front:document.querySelector('.cards .front')?.innerText,
   back:document.querySelector('.cards .back')?.innerText}));
  const missing=[['写真',meta.photoSet],['教室詳細のQR',meta.qrDetailsSet],['申込フォームのQR',meta.qrSet]].filter(([,ok])=>!ok).map(([n])=>n);
  if(missing.length)throw Error('次が未設定です：'+missing.join('・')+'\n編集用テンプレートで設定したあと、「編集済みHTMLを保存」をやり直してください。');
  if(!meta.school||meta.school.includes('○○'))throw Error('教室名が「'+(meta.school||'空欄')+'」のままです。\n編集用テンプレートで教室名を入れ、「編集済みHTMLを保存」をやり直してください。');
  // srcのない枠を読ませるとEncodingErrorになるため、設定済みの画像だけ待つ。
  await page.locator('#printSheets img').evaluateAll(imgs=>Promise.all(imgs.filter(i=>i.getAttribute('src')).map(i=>i.decode())));
  for(const [side,selector] of [['表','.front-sheet .print-cell'],['裏','.back-sheet .print-cell']]){
   const cell=page.locator(selector).first();const box=await cell.boundingBox();
   if(!box||Math.abs(box.width*25.4/96-91)>.05||Math.abs(box.height*25.4/96-55)>.05)throw Error('カード寸法が91×55mmではありません');
   await cell.screenshot({path:path.join(out,side+'.png')});
  }
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(out,'書き出し情報.json'),JSON.stringify({source,sha256:crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),created:new Date().toISOString(),widthMm:91,heightMm:55,dpi:384,...meta},null,2));
  console.log('表・裏の画像を書き出しました: '+out);
 }finally{await browser.close()}
})().catch(e=>{console.error(e&&e.message?e.message:e);process.exit(1)});
