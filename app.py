
from flask import Flask, request, jsonify
import os
from github import Github
from base64 import b64decode

app = Flask(__name__)

@app.route("/push", methods=["POST"])
def push_to_github():
    data = request.json
    filename = data.get("filename")
    content = b64decode(data.get("content_base64"))
    repo_name = data.get("repo")
    path = data.get("path", filename)
    token = os.environ.get("GITHUB_TOKEN")

    if not all([filename, content, repo_name, token]):
        return jsonify({"error": "Missing data"}), 400

    g = Github(token)
    repo = g.get_user().get_repo(repo_name)
    try:
        contents = repo.get_contents(path)
        repo.update_file(contents.path, f"Update {filename}", content.decode(), contents.sha)
    except:
        repo.create_file(path, f"Add {filename}", content.decode())

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
