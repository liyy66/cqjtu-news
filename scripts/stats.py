# -*- coding: utf-8 -*-
"""统计 news.json 质量"""
import json, os, collections
p = r"C:\Users\td\WorkBuddy\2026-10-12-22-31-04\data\news.json"
news = json.load(open(p, encoding="utf-8"))
print("total:", len(news))
no_body = [n for n in news if len(n.get("content", "")) < 100]
print("short/empty body:", len(no_body))
nodate = [n for n in news if not n.get("date")]
print("no date:", len(nodate))
print("channels:", dict(collections.Counter(n["channelName"] for n in news)))
dates = sorted(n["date"] for n in news if n.get("date"))
print("date range:", dates[0], "->", dates[-1])
print("with images:", sum(1 for n in news if n.get("images")))
import statistics
lens = [len(n.get("content", "")) for n in news]
print("body len avg/median/max:", int(statistics.mean(lens)), int(statistics.median(lens)), max(lens))
print("\n--- newest 5---")
for n in news[:5]:
    print(n.get("date"), "|", n["channelName"], "|", n["title"][:45], "| body", len(n.get("content","")))
print("\n--- longest 3---")
for n in sorted(news, key=lambda x: -len(x.get("content","")))[:3]:
    print(n.get("date"), "|", n["title"][:40], "|", len(n["content"]), "|", n["url"])