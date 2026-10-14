# 重庆交通大学资讯助手 —云端自动更新

这个仓库包含站点源码和抓取脚本。配好之后，**GitHub 云端每6 小时自动抓一次官网并重新发布**，你的电脑可以关机、不需要开着 WorkBuddy。

## 原理

```
官网 news.cqjtu.edu.cn
      ↓每 6 小时
GitHub Actions 定时任务（云端执行）
      ↓
抓取新增文章 → 重新打包 site/data 分片 → 提交回仓库
      ↓
GitHub Pages 自动发布
      ↓
任何人访问都是最新数据
```

## 为什么必须换到这个方案

站点是**纯静态 HTML**（`index.html` 里全是 `fetch('data/xxx.json')`）。静态托管没有定时器也没有执行环境，
数据是「谁抓了、谁推上去」才更新。想做到不开电脑也能更新，抓取任务必须放到云端去跑。

好消息是站点本身几乎不用改：全站 9.4MB、`data/` 是纯 JSON 分片、无后端、全部相对路径。

## 首次部署步骤

需要你先注册 GitHub 账号（github.com）。以下几步是一次性的。

### 1. 建仓库

在 github.com 新建一个仓库，例如 `cqjtu-news`，**选 Public**（Pages 私有仓库要收付费）。

### 2. 把代码推上去

在本机项目目录执行（已安装 git，仓库内文件已就绪）：

```bash
cd C:\Users\td\WorkBuddy\2026-10-12-22-31-04
git init
git add .
git commit -m "init: 重庆交通大学资讯助手"
git branch -M main
git remote add origin https://github.com/<你的用户名>/cqjtu-news.git
git push -u origin main
```

推送时会要求登录，用 GitHub 网页授权即可。

### 3. 开启 Pages

仓库页面 → **Settings** → **Pages**：
- Source 选 **GitHub Actions**

### 4. 手动触发一次验证

仓库页面 → **Actions** 标签 → 左侧选「抓取重庆交通大学新闻网」→ 点**Run workflow**。

首次运行是**全量抓取**（约 2400 篇），需要 10～30 分钟，属正常。
之后每轮只抓新增，通常 1～2 分钟。

成功后访问 `https://<你的用户名>.github.io/cqjtu-news/` 即可看到站点。

## 日常

之后**什么都不用做**。定时任务每 6 小时自动运行：

| 时刻（北京时间） | 说明 |
|---|---|
| 03:23 | 凌晨发稿（若学校夜间发文） |
| 09:23 | 早间发稿 |
| 15:23 | 午后发稿 |
| 21:23 | 傍晚/晚间发稿 |

- 有新文章 → 抓取、提交、重新发布
- 没有新文章 → 直接跳过，不产生无意义的部署

## 目录说明

```
.github/workflows/update.yml   定时任务定义
scripts/crawl_news.py          列表页 + 正文抓取
scripts/daily_update.py        增量更新 + 打包（断点续传）
scripts/build_site.py          生成分片
scripts/repo_state.py          状态文件转换（见下）
state/news.jsonl               增量基线（已入库文章）
site/                          站点成品，Pages 发布的就是它
```

### 关于 state/news.jsonl

`news.json` 是 7MB 的**单行** JSON。如果直接提交，git 每次都会认为整行被替换，
等于每轮往历史里塞一份完整快照，每天 4 次会把仓库撑到 GB 级。

所以改成每篇文章一行（JSONL）存进`state/news.jsonl`，git 只记录新增的那几行，
仓库体积维持在 MB 级。`repo_state.py` 负责两者互转，已验证 2495 篇往返完全一致。

## 排错

| 现象 | 处理 |
|---|---|
| Actions 里任务失败 | 点进去看红色步骤的日志，多数是网络抖动，重跑即可 |
| 首次运行超时 | 全量抓取确实久；可在 `workflow_dispatch` 里重跑，或调大 `timeout-minutes` |
| Pages 404 | 确认 Settings → Pages 的 Source 选的是 GitHub Actions |
| 定时任务没跑 | GitHub 会延迟定时任务（尤其整点繁忙时段），相差几十分钟属正常 |
| 想要更快更新 | 改 `update.yml` 里 `cron`，最小间隔 5 分钟；过于频繁可能被 GitHub 限流 |

## 相比原静态链接

原来那个 `cqjtu-news.app.workbuddy.host` 链接仍能访问，但它的数据停在最后一次手动发布。
需要两边都保持最新的话，用本方案即可——原来那条链路可以停掉了。
