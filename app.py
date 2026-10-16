import os
import requests
import streamlit as st

API = "https://api.github.com"
st.set_page_config(page_title="GitHub Repo Analyzer", page_icon="🐙", layout="wide")
st.title("🐙 GitHub Repository Analyzer")
st.write("Enter a public repository in `owner/repository` format.")

repo_input = st.text_input("Repository", value="pallets/flask", placeholder="owner/repository")
token = os.getenv("GITHUB_TOKEN", "").strip()

def api_get(path, params=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(f"{API}{path}", headers=headers, params=params, timeout=15)
    if response.status_code == 404:
        raise ValueError("Repository not found, or it is private.")
    if response.status_code == 403:
        raise ValueError("GitHub API rate limit reached. Wait or set GITHUB_TOKEN in your environment.")
    response.raise_for_status()
    return response.json()

if st.button("Analyze repository", type="primary"):
    repo = repo_input.strip().strip("/")
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        st.error("Use the format `owner/repository`.")
        st.stop()
    owner, name = parts
    try:
        data = api_get(f"/repos/{owner}/{name}")
        commits = api_get(f"/repos/{owner}/{name}/commits", {"per_page": 8})
    except (requests.RequestException, ValueError) as exc:
        st.error(str(exc))
        st.stop()

    st.subheader(data.get("full_name", repo))
    st.write(data.get("description") or "No description provided.")
    cols = st.columns(4)
    cols[0].metric("⭐ Stars", f"{data.get('stargazers_count', 0):,}")
    cols[1].metric("🍴 Forks", f"{data.get('forks_count', 0):,}")
    cols[2].metric("Open issues", f"{data.get('open_issues_count', 0):,}")
    cols[3].metric("Language", data.get("language") or "Not specified")
    st.write(f"**Default branch:** `{data.get('default_branch', 'unknown')}`")
    st.write(f"**Created:** {data.get('created_at', '')[:10]}  |  **Last updated:** {data.get('updated_at', '')[:10]}")
    st.link_button("Open repository on GitHub", data.get("html_url", f"https://github.com/{repo}"))
    st.subheader("Recent commits")
    for item in commits:
        message = item.get("commit", {}).get("message", "").splitlines()[0]
        author = item.get("commit", {}).get("author", {}).get("name", "Unknown")
        date = item.get("commit", {}).get("author", {}).get("date", "")[:10]
        st.markdown(f"- **{date} · {author}** — {message}")
