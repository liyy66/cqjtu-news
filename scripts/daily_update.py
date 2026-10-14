# -*- coding: utf-8 -*-
"""
每日增量更新：只抓首页最新列表 -> 合并进 news.json -> 重新打包前端分片。
用法: python daily_update.py
可被自动化任务（每天早上调用）触发。
"""
import json, os, sys, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
LIST = os.path.join(DATA, "_list.json")
NEWS = os.path.join(DATA, "news.json")
PY = sys.executable


def run(args):
    print("RUN:", " ".join(args), flush=True)
    r = subprocess.run(args, cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-1500:] or r.stderr[-1500:], flush=True)
    return r.returncode


def main():
    today = datetime.date.today()

    # 1) 列表页第一页（每个栏目最新）
    print("== step1: fetch channel front pages ==", flush=True)
    run([PY, os.path.join(HERE, "crawl_news.py"), "front"])

    if not os.path.exists(LIST):
        print("no _list.json, abort", flush=True)
        return 1

    items = json.load(open(LIST, encoding="utf-8"))
    print("list items: %d" % len(items), flush=True)

    # 2) 新增的（不在已有 news 里）抓正文
    done = {}
    if os.path.exists(NEWS):
        for n in json.load(open(NEWS, encoding="utf-8")):
            if n.get("content"):
                done[n["url"]] = n
    todo = [it for it in items if it["url"] not in done]
    n_before = len(done)
    print("new items to fetch: %d" % len(todo), flush=True)

    if todo:
        # 复用 body 阶段的解析逻辑
        sys.path.insert(0, HERE)
        from crawl_news import parse_article
        import concurrent.futures as cf
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(parse_article, it["url"]): it for it in todo}
            for f in cf.as_completed(futs):
                it = futs[f]
                try:
                    a = f.result()
                except Exception:
                    a = None
                if a and len(a["text"]) > 80:
                    it.update({
                        "title": a["title"] or it["title"],
                        "content": a["text"],
                        "images": a["images"],
                        "date": a["date"] or it.get("date", ""),
                        "source": "重庆交通大学新闻网",
                    })
                    done[it["url"]] = it

    # 真实成功入库数（不是计划抓取数）—— 网络失败时不会误报为有新增
    new_ok = len(done) - n_before
    failed = len(todo) - new_ok
    if failed:
        # 失败项不写盘，下次运行会自动重试（断点续传）
        print("WARNING: %d items failed to fetch, will retry next run"
              % failed, flush=True)

    news = list(done.values())
    news.sort(key=lambda x: x.get("date", ""), reverse=True)
    json.dump(news, open(NEWS, "w", encoding="utf-8"), ensure_ascii=False)
    print("news.json: %d articles" % len(news), flush=True)

    # 3) 重新打包
    print("== step2: rebuild site data ==", flush=True)
    run([PY, os.path.join(HERE, "build_site.py")])

    # 4) 写运行报告
    # total 取打包后的**线上真实条数**（已去重），与站点展示保持一致；
    # rawTotal 为抓取库原始条数，仅供排查差异用。
    live_total, newest = len(news), (news[0].get("date", "") if news else "")
    try:
        idx = json.load(open(os.path.join(ROOT, "site", "data", "index.json"),
                             encoding="utf-8"))
        live_total = idx.get("total", live_total)
        newest = idx.get("dateTo", newest)
    except Exception:
        pass
    rep = {
        "runAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": live_total,
        "rawTotal": len(news),
        "newFetched": new_ok,
        "failed": failed,
        "newestDate": newest,
    }
    json.dump(rep, open(os.path.join(DATA, "_last_update.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
    print("UPDATE DONE", rep, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())