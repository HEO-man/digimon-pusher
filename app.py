from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from github import Github
import base64
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

@app.route("/push", methods=["POST"])
def push_to_github():
    try:
        data = request.json
        logging.info(f"📨 요청 JSON 키: {list(data.keys())}")

        filename = data.get("filename")
        content_b64 = data.get("content_base64")
        repo_name = data.get("repo")
        folder = data.get("folder", "")  # optional
        path = data.get("path", "")      # 우선 path 사용
        token = os.environ.get("GITHUB_TOKEN")

        if not all([filename, content_b64, repo_name, token]):
            logging.error("❌ 필수 필드 누락됨")
            return jsonify({"error": "Missing required fields"}), 400

        # 경로 설정 (보안 필터 포함)
        if not path:
            path = f"data/digi_illustration/{folder}/{filename}" if folder else filename

        if ".." in path or path.startswith("/"):
            logging.warning(f"🚫 잘못된 경로 감지됨: {path}")
            return jsonify({"error": "Invalid path"}), 400

        logging.info(f"📂 저장 경로: {path}")
        logging.info(f"📄 파일명: {filename}")
        logging.info(f"📦 레포지토리: {repo_name}")

        # 내용 디코딩
        decoded_bytes = base64.b64decode(content_b64)
        if filename.endswith((".json", ".txt")):
            content_to_commit = decoded_bytes.decode("utf-8")
        else:
            content_to_commit = base64.b64encode(decoded_bytes).decode("utf-8")

        # GitHub 업로드
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)

        try:
            existing = repo.get_contents(path)
            repo.update_file(
                path=path,
                message=f"Update {filename}",
                content=content_to_commit,
                sha=existing.sha,
                branch="main"
            )
            logging.info(f"✅ 업데이트 완료: {path}")
        except Exception:
            repo.create_file(
                path=path,
                message=f"Add {filename}",
                content=content_to_commit,
                branch="main"
            )
            logging.info(f"🆕 새 파일 생성: {path}")

        return jsonify({"status": "success"})

    except Exception as e:
        logging.exception("🔥 서버 오류 발생")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
