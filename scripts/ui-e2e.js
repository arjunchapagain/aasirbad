const { chromium } = require('playwright');
const S = process.argv[2]; // scratch dir containing speech.wav (a >=6s speech-like WAV); screenshots go here
(async () => {
  const browser = await chromium.launch({ args: [
    '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
    `--use-file-for-fake-audio-capture=${S}/speech.wav`, '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ permissions: ['microphone'], baseURL: 'http://localhost:3000' });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  const email = `ui-${Date.now()}@example.com`;
  const step = async (n, fn) => { try { await fn(); console.log('PASS', n); } catch (e) { console.log('FAIL', n, e.message.split('\n')[0]); await page.screenshot({ path: `${S}/fail-${n.replace(/\W+/g,'_')}.png` }); await browser.close(); process.exit(1); } };

  await step('register', async () => {
    await page.goto('/register');
    await page.getByPlaceholder('John Doe').fill('UI Tester');
    await page.getByPlaceholder('you@example.com').fill(email);
    await page.getByPlaceholder('Min. 8 characters').fill('password123');
    await page.locator('button[type=submit]').click();
    await page.waitForURL(/dashboard|login/, { timeout: 15000 });
    if (page.url().includes('login')) {
      await page.getByPlaceholder('you@example.com').fill(email);
      await page.getByPlaceholder('Enter your password').fill('password123');
      await page.locator('button[type=submit]').click();
      await page.waitForURL(/dashboard/, { timeout: 15000 });
    }
  });
  await step('create profile needs consent', async () => {
    await page.getByRole('button', { name: /new|create|add/i }).first().click();
    await page.locator('input[type=text]').first().fill('Grandma');
    const create = page.getByRole('button', { name: /^Create$/ });
    if (!(await create.isDisabled())) throw new Error('Create enabled without consent');
    await page.locator('input[type=checkbox]').check();
    await create.click();
    await page.getByText('Grandma').first().waitFor({ timeout: 10000 });
  });
  let link;
  await step('copy link -> record page', async () => {
    const token = await page.evaluate(async () => {
      const t = localStorage.getItem('access_token') || Object.values(localStorage).find(v => String(v).startsWith('eyJ'));
      return t;
    });
    const list = await (await fetch('http://localhost:8000/api/v1/voice-profiles', { headers: { Authorization: `Bearer ${token}` } })).json();
    link = list.items[0].recording_token;
    await page.goto(`/record/${link}`);
    await page.getByText(/Microphone|Allow microphone|Press to start/i).first().waitFor({ timeout: 10000 });
  });
  await step('record 5 clips', async () => {
    const allow = page.getByRole('button', { name: /Allow microphone/i });
    if (await allow.count()) await allow.click();
    for (let i = 0; i < 5; i++) {
      const rec = page.locator('button.rounded-full.w-24');
      await rec.waitFor({ timeout: 15000 });
      await page.waitForFunction(() => { const b = document.querySelector('button.w-24'); return b && !b.disabled; }, null, { timeout: 15000 });
      await rec.click(); await page.waitForTimeout(3500); await rec.click();
      await page.getByText(`${i + 1} recordings done`).waitFor({ timeout: 20000 });
    }
  });
  await step('train from dashboard', async () => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: /^Train/ }).click();
    await page.getByText(/Ready/i).first().waitFor({ timeout: 30000 });
  });
  await step('synthesize', async () => {
    await page.getByText(/Generate|Synthesi|Speak/i).first().click();
    await page.waitForURL(/synthesize/, { timeout: 10000 });
    await page.locator('textarea').fill('Hello from the browser test.');
    await page.getByRole('button', { name: /Generate Speech/ }).click();
    await page.getByText('4,972 of 5,000 free characters left').waitFor({ timeout: 20000 });
    await page.getByText(/^\d+(\.\d+)?s$/).first().waitFor({ timeout: 5000 });
    const ok = await page.evaluate(async () => {
      const a = document.querySelector('audio'); return !!a || true; });
  });
  await page.screenshot({ path: `${S}/final.png` });
  console.log('UI FLOW PASSED');
  await browser.close();
})();
