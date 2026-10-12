"""Refresh public GitHub profile cards; stdlib only; never replace good data on failure."""
import collections
import datetime
import html
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
USER = os.environ.get("PROFILE_USER", "AmoghxAnubis")
def api(path):
    headers = {"User-Agent": "anubis-profile", "Accept": "application/vnd.github+json"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
        return json.load(response)

def render(profile, repos):
    owned = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in owned)
    languages = collections.Counter(r["language"] for r in owned if r.get("language"))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pieces = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img"><title>Public GitHub snapshot</title><rect width="1000" height="260" rx="18" fill="#0b0b0e"/><rect x="1" y="1" width="998" height="258" rx="17" fill="none" stroke="#303038"/>']
    def text(x,y,value,size=13,color="#9999a5",weight="400"):
        pieces.append(f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(value))}</text>')
    text(30,35,"04 / GITHUB SIGNAL",14,"#ff7a18","700")
    text(680,35,stamp,12)
    for i,(value,label) in enumerate([(profile["public_repos"],"PUBLIC REPOSITORIES"),(stars,"STARS · OWNED ORIGINALS"),(profile["followers"],"FOLLOWERS")]):
        x=30+i*330
        text(x,105,f"{value:02}",45,"#f7f5f2","700")
        text(x,133,label,12)
    pieces.append('<path d="M30 155H970" stroke="#28282f"/>')
    text(30,184,"PRIMARY REPO LANGUAGES",11)
    palette=["#ff7a18","#55d5f5","#b898ff","#ff5e9c","#e5c75b"]
    top=languages.most_common(5)
    total=sum(v for _,v in top) or 1
    cursor=30
    for i,(language,count) in enumerate(top):
        width=940*count/total
        pieces.append(f'<rect x="{cursor}" y="200" width="{max(width-3,1)}" height="8" rx="3" fill="{palette[i]}"/>')
        cursor+=width
    for i,(language,count) in enumerate(top):
        text(30+i*188,238,f"● {language} ({count})",11,palette[i])
    pieces.append("</svg>")
    return "".join(pieces)

def main():
    profile=api("users/"+USER)
    repos=[]
    page=1
    while True:
        batch=api(f"users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos.extend(batch)
        if len(batch)<100: break
        page+=1
    output=ROOT/"assets"/"github-signal.svg"
    result=render(profile,repos)
    temp=output.with_suffix(".tmp")
    temp.write_text(result)
    temp.replace(output)
    print(f"Refreshed public snapshot for {USER}: {len(repos)} repositories")

if __name__=="__main__": main()
