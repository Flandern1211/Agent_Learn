import os
from http.client import responses

import export
import httpx
from mcp.server.fastmcp import FastMCP



#创建mcp实例
mcp = FastMCP("github",host="0.0.0.0", port=8000)

#从环境变量中获取token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN","")

HEADERS = {
    "Accept" : "application/vnd.github+json",
    "User_Agent": "github-mcp-server",
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

@mcp.tool()
async def search_repos(query: str, max_results: int = 5) -> str:
    """搜索 GitHub 仓库。

      Args:
          query: 搜索关键词，支持 GitHub 搜索语法
                （如 language:python stars:>100）
          max_results: 返回结果数量，默认 5
      """
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "per_page": max_results, "sort": "starts"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, headers=HEADERS, params= params
        )

        response.raise_for_status()
        data = response.json()

    if not data["items"]:
        return "未找到匹配的仓库"

    results = []

    for repo in data["items"]:
        results.append(
            f"{repo['full_name']}(Star{repo['stargazers_count']})\n"
            f"{repo['description'] or "无描述"} \n"
            f"语言:{repo['language'] or "未知"}"
            f"最近更新:{repo['updated_at'][:10]}"

        )
    return "\n\n".join(results)

@mcp.tool()

async def get_repo_info(owner: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

    license_name = "无"
    if data.get("license"):
        license_name = data["license"].get("name", "无")

    return (
        f"仓库: {data['full_name']}\n"
        f"描述: {data['description'] or '无描述'}\n"
        f"语言: {data['language'] or '未知'}\n"
        f"Star: {data['stargazers_count']}  "
        f"Fork: {data['forks_count']}\n"
        f"创建时间: {data['created_at'][:10]}\n"
        f"最近更新: {data['updated_at'][:10]}\n"
        f"默认分支: {data['default_branch']}\n"
        f"开源协议: {license_name}"
    )

if __name__ == "__main__":
    mcp.run(transport="streamable-http")