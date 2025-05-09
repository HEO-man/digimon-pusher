from flask import Flask, request, jsonify
from github import Github
import os
import base64

app = Flask(__name__)

@app.route("/push", methods=["POST"])
def push_to_github():
    data = request.json
    filename = data.get("filename")
    content_b64 = data.get("content_base64")
    repo_name = data.get("repo")
    path = data.get("path", filename)
    token = os.environ.get("GITHUB_TOKEN")

    if not all([filename, content_b64, repo_name, path, token]):
        return jsonify({"error": "Missing required data"}), 400

    try:
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)

        is_text_file = filename.endswith(".json") or filename.endswith(".txt")
        content_bytes = base64.b64decode(content_b64)
        content_str = content_bytes.decode("utf-8") if is_text_file else content_bytes

        try:
            existing_file = repo.get_contents(path)
            repo.update_file(
                path,
                f"Update {filename}",
                content_str,
                existing_file.sha,
                branch="main"
            )
        except Exception as e:
            repo.create_file(
                path,
                f"Add {filename}",
                content_str,
                branch="main"
            )

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
