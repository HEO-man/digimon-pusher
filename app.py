from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from github import Github
import base64

app = Flask(__name__)
CORS(app)

@app.route("/push", methods=["POST"])
def push_to_github():
    try:
        data = request.json
        filename = data.get("filename")
        content_b64 = data.get("content_base64")
        repo_name = data.get("repo")
        folder = data.get("folder", "")  # optional
        token = os.environ.get("GITHUB_TOKEN")

        if not all([filename, content_b64, repo_name, token]):
            return jsonify({"error": "Missing required fields"}), 400

        # 저장 경로 지정
        if folder:
            path = f"data/digi_illustration/{folder}/{filename}"
        else:
            path = filename

        # content 처리: 텍스트 or 바이너리
        decoded_bytes = base64.b64decode(content_b64)
        if filename.endswith(".json") or filename.endswith(".txt"):
            content_to_commit = decoded_bytes.decode("utf-8")
        else:
            # 바이너리 파일은 base64 문자열로 저장
            content_to_commit = base64.b64encode(decoded_bytes).decode("utf-8")

        g = Github(token)
        repo = g.get_user().get_repo(repo_name)

        try:
            existing = repo.get_contents(path)
            repo.update_file(
                path=existing.path,
                message=f"Update {filename}",
                content=content_to_commit,
                sha=existing.sha,
                branch="main"
            )
            print(f"✅ {path} 업데이트 완료")
        except Exception:
            repo.create_file(
                path=path,
                message=f"Add {filename}",
                content=content_to_commit,
                branch="main"
            )
            print(f"📁 {path} 새로 생성")

        return jsonify({"status": "success"})

    except Exception as e:
        print("🔥 서버 오류:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
