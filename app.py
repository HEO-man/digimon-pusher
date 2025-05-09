from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from github import Github
from base64 import b64decode

app = Flask(__name__)
CORS(app)  # CORS 허용

@app.route("/push", methods=["POST"])
def push_to_github():
    try:
        data = request.json
        filename = data.get("filename")
        content_b64 = data.get("content_base64")
        repo_name = data.get("repo")
        path = data.get("path", filename)
        token = os.environ.get("GITHUB_TOKEN")

        if not all([filename, content_b64, repo_name, token]):
            return jsonify({"error": "Missing required fields"}), 400

        # GitHub 인증
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        # Base64 디코드 → 텍스트로 복원
        decoded_content = b64decode(content_b64).decode()

        try:
            # 기존 파일 업데이트
            contents = repo.get_contents(path)
            repo.update_file(
                path=contents.path,
                message=f"Update {filename}",
                content=decoded_content,
                sha=contents.sha,
                branch="main"
            )
        except Exception:
            # 신규 파일 생성
            repo.create_file(
                path=path,
                message=f"Add {filename}",
                content=decoded_content,
                branch="main"
            )

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
