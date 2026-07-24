-- 열피쌤 피드백 대시보드 : Supabase 스키마
-- Supabase 프로젝트 생성 후 SQL Editor에서 그대로 실행하세요.

create table if not exists urgent_requests (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  date text not null,        -- 수기 입력 (예: 2026.07.24)
  owner text not null,
  content text not null
);

create table if not exists general_inquiries (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  date date not null,
  owner text not null,
  type text not null check (type in ('general', 'idea')),  -- general=일반 문의, idea=카페 활용 아이디어
  content text not null
);

create table if not exists resolved_issues (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  date date not null,
  owner text not null,
  status text not null check (status in ('도배', '불건전', '무단광고')),
  content text not null,
  photo_url text
);

-- 링크만 있으면 로그인 없이 접근하는 구조이므로,
-- RLS를 켜되 누구나 읽기/쓰기/삭제 가능한 정책을 명시적으로 부여합니다.
-- (이 부분이 곧 "링크 유출 시 아무나 수정 가능"이라는 리스크입니다.)

alter table urgent_requests enable row level security;
alter table general_inquiries enable row level security;
alter table resolved_issues enable row level security;

create policy "urgent_public_select" on urgent_requests for select using (true);
create policy "urgent_public_insert" on urgent_requests for insert with check (true);
create policy "urgent_public_delete" on urgent_requests for delete using (true);

create policy "general_public_select" on general_inquiries for select using (true);
create policy "general_public_insert" on general_inquiries for insert with check (true);

create policy "resolved_public_select" on resolved_issues for select using (true);
create policy "resolved_public_insert" on resolved_issues for insert with check (true);

-- 해결 완료 건 사진 첨부용 Storage 버킷은 SQL이 아니라
-- Supabase 대시보드 > Storage 에서 "resolved-photos" 이름으로 Public 버킷을 직접 생성하세요.
