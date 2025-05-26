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

        # 텍스트(json/txt) 파일은 디코딩 → 문자열로 커밋
        if filename.endswith(".json") or filename.endswith(".txt"):
            decoded_bytes = base64.b64decode(content_b64)
            content_to_commit = decoded_bytes.decode("utf-8")
        else:
            # 바이너리는 base64 인코딩 문자열 그대로 사용 (Github API 규격)
            content_to_commit = content_b64

        # 업로드 또는 업데이트
        try:
            existing = repo.get_contents(path)
            repo.update_file(
                path=existing.path,
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
