# 열피쌤 피드백 대시보드

Streamlit + Supabase로 만든, 링크만 있으면 로그인 없이 누구나 등록/조회 가능한
카페 운영 피드백 대시보드입니다. 좌측 사이드바에 3개 탭(긴급 확인 요청 / 일반 문의 건 / 해결 완료 건)이 있습니다.

## 1. Supabase 준비

1. https://supabase.com 에서 무료 프로젝트 생성
2. 좌측 메뉴 **SQL Editor** 에서 `supabase_schema.sql` 내용을 그대로 붙여넣고 실행
   - `urgent_requests`, `general_inquiries`, `resolved_issues` 3개 테이블 + 공개 read/write 정책 생성
3. 좌측 메뉴 **Storage** 에서 `resolved-photos` 라는 이름의 **Public** 버킷 생성 (해결 완료 건 사진 첨부용)
4. 좌측 메뉴 **Project Settings > API** 에서 `Project URL`과 `anon public` 키 복사

## 2. 로컬 실행

```bash
cd yeolpi-dashboard
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml을 열어 Supabase URL / anon key 입력
streamlit run app.py
```

## 3. GitHub 푸시 + Streamlit Cloud 배포

```bash
git init
git add .
git commit -m "init: 열피쌤 피드백 대시보드"
git remote add origin <레포 URL>
git push -u origin main
```

1. https://share.streamlit.io 에서 New app → 방금 만든 레포 선택, `app.py` 지정
2. 앱 설정(Settings) > **Secrets** 에 `.streamlit/secrets.toml.example`과 동일한 형식으로
   실제 Supabase URL/anon key 입력 (로컬 secrets.toml은 git에 올라가지 않으므로 여기서 별도 등록 필요)
3. 배포 완료 후 나오는 URL을 팀에 공유하면, 로그인 없이 링크만으로 누구나 접근 가능

## 참고 / 알려진 제약

- **접근 제어 없음**: 링크를 아는 사람은 누구나 등록·삭제까지 가능합니다. 필요해지면 공용 PIN이나
  Supabase Auth를 추가로 붙일 수 있습니다.
- **달력 인터랙션**: 기획 시 검토했던 HTML 목업의 "날짜에 마우스 오버 시 + 버튼" 같은 hover 인터랙션은
  Streamlit 네이티브 위젯 한계로 그대로 구현하지 않았습니다. 대신 각 날짜 칸에 항상 보이는
  `＋ 등록` 버튼과, 등록된 항목을 누르면 뜨는 읽기 전용(수정 불가) 상세 모달로 동일한 사용 흐름
  (등록 → 조회 → 조회는 읽기 전용)을 구현했습니다.
- **긴급 확인 요청 건수**는 전체 등록 건수 기준입니다. 처리 완료 개념이 필요해지면
  `urgent_requests`에 `resolved boolean` 컬럼을 추가하는 식으로 확장하면 됩니다.
