-- Run this entire file once in Supabase Dashboard > SQL Editor.
create table if not exists public.user_productivity_state (
  user_id uuid primary key references auth.users(id) on delete cascade,
  daily_date date not null,
  daily_data jsonb not null default '{}'::jsonb,
  micro_config jsonb not null default '[]'::jsonb,
  timezone text not null default 'UTC',
  updated_at timestamptz not null default now()
);

alter table public.user_productivity_state enable row level security;

drop policy if exists "Users can read their own productivity state"
  on public.user_productivity_state;
create policy "Users can read their own productivity state"
  on public.user_productivity_state
  for select
  to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users can create their own productivity state"
  on public.user_productivity_state;
create policy "Users can create their own productivity state"
  on public.user_productivity_state
  for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users can update their own productivity state"
  on public.user_productivity_state;
create policy "Users can update their own productivity state"
  on public.user_productivity_state
  for update
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users can delete their own productivity state"
  on public.user_productivity_state;
create policy "Users can delete their own productivity state"
  on public.user_productivity_state
  for delete
  to authenticated
  using ((select auth.uid()) = user_id);

revoke all on table public.user_productivity_state from anon;
grant select, insert, update, delete on table public.user_productivity_state to authenticated;
