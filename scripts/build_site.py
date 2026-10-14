# -*- coding: utf-8 -*-
"""
把 data/news.json + data/qa.json 打包成前端可直接 fetch 的分片文件。
输出到 site/data/：
  index.json      概览：统计、最新若干条、栏目、官方链接
  feed-YYYY-MM.json  每日新闻（新闻推送用）
  articles/NNN.json   正文分片（按日期归档，查询时按需加载）
  qa.json         问答库（拷贝）
"""
import json, os, collections, datetime, shutil, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "site")
SITE_DATA = os.path.join(SITE, "data")
ART_DIR = os.path.join(SITE_DATA, "articles")

for d in (SITE, SITE_DATA):
    os.makedirs(d, exist_ok=True)
os.makedirs(ART_DIR, exist_ok=True)

news = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
qa = json.load(open(os.path.join(DATA, "qa.json"), encoding="utf-8"))

# 只保留有正文的
news = [n for n in news if len(n.get("content", "")) > 60]

# 清洗标题尾部站点后缀 + 按 (标题,日期) 去重（同文可能多栏目重复推送）
SITE_SUFFIX = re.compile(r"\s*[-–—|]\s*重庆交通大学(?:新闻网|官网)\s*$")


def clean_title(t):
    prev = None
    while prev != t:
        prev = t
        t = SITE_SUFFIX.sub("", (t or "")).strip()
    return t or prev


for n in news:
    n["title"] = clean_title(n.get("title", ""))
seen_key = set()
uniq = []
for n in news:
    k = (n["title"], n.get("date", ""))
    if not n["title"] or k in seen_key:
        continue
    seen_key.add(k)
    uniq.append(n)
news = uniq

news.sort(key=lambda x: x.get("date", ""), reverse=True)

# 建立 id
for i, n in enumerate(news):
    n["id"] = "a%05d" % i

by_date = collections.defaultdict(list)
for n in news:
    by_date[n.get("date", "unknown")].append(n)


def snippet(n, L=120):
    t = re.sub(r"\s+", " ", n.get("content", "")).strip()
    return t[:L] + ("…" if len(t) > L else "")


# 1. 每日分片
used_feed = set()
for d, arr in by_date.items():
    used_feed.add("feed-%s.json" % d)
    out = [{
        "id": n["id"], "t": n["title"], "d": n.get("date", ""),
        "c": n.get("channelName", ""), "u": n["url"], "s": snippet(n),
        "img": (n.get("images") or [""])[0],
    } for n in arr]
    json.dump(out, open(os.path.join(SITE_DATA, "feed-%s.json" % d), "w",
                        encoding="utf-8"), ensure_ascii=False)

# 2. 正文分片（每 40 篇一包，便于按需加载）
CHUNK = 40
chunks = []
used_chunk_files = set()
for k in range(0, len(news), CHUNK):
    part = news[k:k + CHUNK]
    name = "p%03d.json" % (k // CHUNK)
    used_chunk_files.add(name)
    body = [{
        "id": n["id"], "t": n["title"], "d": n.get("date", ""),
        "c": n.get("channelName", ""), "u": n["url"],
        "body": n.get("content", ""), "img": n.get("images", []),
    } for n in part]
    json.dump(body, open(os.path.join(ART_DIR, name), "w", encoding="utf-8"),
              ensure_ascii=False)
    chunks.append({"f": name, "from": part[0]["id"], "to": part[-1]["id"],
                   "n": len(part)})

# 3. 全量轻量索引（用于搜索，字段尽量短）
index = [{
    "id": n["id"], "t": n["title"], "d": n.get("date", ""),
    "c": n.get("channelName", ""), "u": n["url"], "s": snippet(n, 90),
} for n in news]

# 4. 概览
dates = sorted(by_date.keys(), reverse=True)
chan_stat = collections.Counter(n.get("channelName", "") for n in news)
index_data = {
    "school": "重庆交通大学",
    "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total": len(news),
    "dateFrom": dates[-1] if dates else "",
    "dateTo": dates[0] if dates else "",
    "dates": dates,
    "channels": qa["channels"],
    "officialLinks": qa["officialLinks"],
    "chanStat": [{"name": k, "n": v} for k, v in chan_stat.most_common()],
    "chunks": chunks,
    "latest": [{
        "id": n["id"], "t": n["title"], "d": n.get("date", ""),
        "c": n.get("channelName", ""), "u": n["url"], "s": snippet(n),
        "img": (n.get("images") or [""])[0],
    } for n in news[:60]],
}

json.dump(index_data, open(os.path.join(SITE_DATA, "index.json"), "w",
                           encoding="utf-8"), ensure_ascii=False)
json.dump(index, open(os.path.join(SITE_DATA, "index-all.json"), "w",
                      encoding="utf-8"), ensure_ascii=False)
json.dump(qa, open(os.path.join(SITE_DATA, "qa.json"), "w",
                   encoding="utf-8"), ensure_ascii=False)

sz = lambda p: os.path.getsize(os.path.join(SITE_DATA, p)) // 1024

# 清理上一轮遗留、本轮已不再需要的分片（正常为 0 个）
stale = []
for f in os.listdir(ART_DIR):
    if f.endswith(".json") and f not in used_chunk_files:
        stale.append(os.path.join(ART_DIR, f))
for f in os.listdir(SITE_DATA):
    if f.startswith("feed-") and f.endswith(".json") and f not in used_feed:
        stale.append(os.path.join(SITE_DATA, f))
for p in stale:
    try:
        os.remove(p)
    except OSError:
        pass

print("news:", len(news), "| feed files:", len(by_date), "| chunks:", len(chunks))
print("date:", index_data["dateFrom"], "->", index_data["dateTo"])
print("index.json %dKB | index-all.json %dKB | stale cleaned: %d" %
      (sz("index.json"), sz("index-all.json"), len(stale)))
print("feed sample:", ["feed-%s.json" % d for d in dates[:3]])