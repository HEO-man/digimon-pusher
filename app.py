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

        logging.info(f"요청 JSON 키 목록: {list(data.keys())}")

        filename = data.get("filename")
        content_b64 = data.get("content_base64")
        repo_name = data.get("repo")
        folder = data.get("folder", "")
        path_param = data.get("path", "")
        token = os.environ.get("GITHUB_TOKEN")

        if not all([filename, content_b64, repo_name, token]):
            logging.error("❌ 필수 필드 누락됨")
            return jsonify({"error": "Missing required fields"}), 400

        # 저장 경로 결정
        if path_param:
            if path_param.startswith("data/digi_illustration/"):
                path = path_param
            else:
                path = f"data/digi_illustration/{path_param}"
        elif folder:
            path = f"data/digi_illustration/{folder}/{filename}"
        else:
            logging.error("❌ 저장 경로를 지정할 수 없음 (folder도 path도 없음)")
            return jsonify({"error": "Missing folder or path"}), 400

        logging.info(f"📂 저장 경로: {path}")
        logging.info(f"📄 파일명: {filename}")
        logging.info(f"📦 레포지토리: {repo_name}")

        # GitHub 연결
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)

        # 파일 형식에 따라 커밋할 내용 결정
        is_text = filename.endswith(".json") or filename.endswith(".txt")

        if is_text:
            decoded_bytes = base64.b64decode(content_b64)
            content_to_commit = decoded_bytes.decode("utf-8")
        else:
            content_to_commit = content_b64  # 이미지나 바이너리는 base64 그대로

        # 파일 업데이트 또는 생성
        try:
            existing = repo.get_contents(path)
            repo.update_file(
                path=existing.path,
                message=f"Update {filename}",
                content=content_to_commit,
                sha=existing.sha,
                branch="main",
                encoding="base64" if not is_text else None
            )
            logging.info(f"✅ 업데이트 완료: {path}")
        except Exception as e:
            logging.warning(f"🆕 기존 파일 없음 또는 오류 → 새 파일 생성: {e}")
            repo.create_file(
                path=path,
                message=f"Add {filename}",
                content=content_to_commit,
                branch="main",
                encoding="base64" if not is_text else None
            )
            logging.info(f"🆕 새 파일 생성: {path}")

        return jsonify({"status": "success"})

    except Exception as e:
        logging.exception("🔥 서버 오류 발생")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
