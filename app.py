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
        folder = data.get("folder", "")  # optional
        token = os.environ.get("GITHUB_TOKEN")
        logging.info("디지몬_01 받은 폴더 :: "+data.get("folder", ""))
        logging.info("디지몬_02 받은 폴더 :: "+data.get("folderName", ""))
        
        if not all([filename, content_b64, repo_name, token]):
            logging.error("❌ 필수 필드 누락됨")
            return jsonify({"error": "Missing required fields"}), 400

        # 저장 경로 지정
        if folder:
            path = f"data/digi_illustration/{folder}/{filename}"
        else:
            path = filename

        
        logging.info(f"📂 전달받은 folder: ${folder}")

        logging.info(f"디지몬 폴더명: ${folder}")
        logging.info(f"📄 업로드 파일명: {filename}")
        logging.info(f"📁 저장 경로: {path}")
        logging.info(f"📦 저장할 레포: {repo_name}")

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
            logging.info(f"✅ {path} 업데이트 완료")
        except Exception:
            repo.create_file(
                path=path,
                message=f"Add {filename}",
                content=content_to_commit,
                branch="main"
            )
            logging.info(f"📁 {path} 새로 생성")

        return jsonify({"status": "success"})

    except Exception as e:
        logging.exception("🔥 서버 오류 발생")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
