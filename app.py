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
        folder = data.get("folder")  # ✅ folder 값 받기
        token = os.environ.get("GITHUB_TOKEN")

        if not all([filename, content_b64, repo_name, token]):
            return jsonify({"error": "Missing data"}), 400

        # path 구성
        if folder:
            path = f"data/digi_illustration/{folder}/{filename}"
        else:
            path = data.get("path", filename)

        # 디코딩
        decoded_content = base64.b64decode(content_b64).decode("utf-8")

        # GitHub 객체
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)

        try:
            # 기존 파일 여부 확인
            existing = repo.get_contents(path)
            repo.update_file(
                path=existing.path,
                message=f"Update {filename}",
                content=decoded_content,
                sha=existing.sha,
                branch="main"
            )
            print(f"✅ {filename} 업데이트 완료")
        except Exception as e:
            # 파일이 없으면 새로 생성
            repo.create_file(
                path=path,
                message=f"Add {filename}",
                content=decoded_content,
                branch="main"
            )
            print(f"📁 {filename} 새로 생성")

        return jsonify({"status": "success"})

    except Exception as e:
        print("🔥 서버 오류:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
