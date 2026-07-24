# 열피쌤 피드백 대시보드 (Vercel 버전)

Streamlit 대신 순수 HTML/CSS/JS + Supabase로 다시 만든 버전입니다.
디자인은 처음 보여드린 목업과 동일하고, Supabase 프로젝트는 기존에 만들어둔 것을 그대로 씁니다.

## 배포 방법 (Vercel)

1. https://vercel.com 접속 → GitHub 계정으로 로그인
2. **Add New... → Project**
3. `allin_piano_teacher` 저장소 선택 → **Import**
4. **Root Directory**를 `web`으로 지정 (매우 중요 — 안 하면 빈 화면이 뜹니다)
5. Framework Preset은 자동으로 "Other" 또는 "Static"으로 잡힘 — 별도 설정 없이 **Deploy** 클릭
6. 1분 이내 배포 완료, 나오는 URL이 실제 서비스 주소

배포된 URL은 로그인 없이 링크만 있으면 누구나 접근 가능합니다.

## 필요한 Supabase 설정 (이미 되어 있어야 함)

- `urgent_requests`, `general_inquiries`, `resolved_issues` 테이블 + 공개 read/write 정책 (`supabase_schema.sql` 참고)
- `resolved-photos` Storage 버킷 (Public)
- 아래 Storage 업로드 권한 정책 (SQL Editor에서 실행, 안 했다면 꼭 실행)

```sql
create policy "resolved_photos_public_insert"
on storage.objects for insert
to public
with check (bucket_id = 'resolved-photos');
```

## 로컬에서 미리 보기

별도 서버 없이 `index.html`을 브라우저로 바로 열어도 동작합니다 (Supabase URL/키가 파일에 직접 들어있음).
