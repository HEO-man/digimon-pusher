from flask import Flask, request, jsonify
import os
from github import Github
import base64

app = Flask(__name__)

@app.route("/push", methods=["POST"])
def push_to_github():
    data = request.json
    filename = data.get("filename")
    content_b64 = data.get("content_base64")  # base64 인코딩된 문자열
    repo_name = data.get("repo")
    path = data.get("path", filename)
    token = os.environ.get("GITHUB_TOKEN")

    if not all([filename, content_b64, repo_name, token]):
        return jsonify({"error": "Missing data"}), 400

    decoded_content = base64.b64decode(content_b64).decode('utf-8')

    g = Github(token)
    user = g.get_user()
    repo = user.get_repo(repo_name)

    try:
        contents = repo.get_contents(path)
        repo.update_file(
            contents.path,
            f"Update {filename}",
            decoded_content,
            contents.sha,
            branch="main"
        )
    except Exception:
        repo.create_file(
            path,
            f"Add {filename}",
            decoded_content,
            branch="main"
        )

    return jsonify({"status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render가 지정한 포트를 사용
    app.run(host="0.0.0.0", port=port)
