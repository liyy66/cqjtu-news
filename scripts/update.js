// 重庆交通大学官方资讯助手 - 每日自动更新
// 用法: node update.js
// 需先执行 python crawl_news.py front 与 build_site.py
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SCRIPTS = path.join(ROOT, 'scripts');
const PY = process.env.PY || 'C:\\Users\\td\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python.exe';

function sh(args, cwd) {
  console.log('[RUN]', args.join(' '));
  try {
    const out = execSync(args.map(a => `"${a}"`).join(' '), {
      cwd, encoding: 'utf8', timeout: 15 * 60 * 1000, stdio: ['ignore', 'pipe', 'pipe']
    });
    console.log(out.slice(-800));
    return true;
  } catch (e) {
    console.error('[ERR]', (e.stdout || '') + (e.stderr || e.message));
    return false;
  }
}

console.log('== 重庆交通大学资讯助手 · 每日更新 ' + new Date().toLocaleString('zh-CN') + ' ==');
const ok1 = sh([PY, path.join(SCRIPTS, 'crawl_news.py'), 'front'], SCRIPTS);
if (!ok1) { console.error('列表抓取失败，终止'); process.exit(1); }
const ok2 = sh([PY, path.join(SCRIPTS, 'daily_update.py')], SCRIPTS);
console.log(ok2 ? '== 更新完成 ==' : '== 更新部分失败 ==');
process.exit(ok2 ? 0 : 1);