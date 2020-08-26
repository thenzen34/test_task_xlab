set search_path to '...';

select r.date, r.result, r.cnt, r.total_duration, p.name, s.name from (
select date, server_id, project_id, result, count(*) as cnt, sum(duration) as total_duration from recognizing_results

where date >= '2020-01-01' and date < '2021-01-01'

group by date, server_id, project_id, result
) as r

left join project as p on p.id = r.project_id
left join server as s on s.id = r.server_id
