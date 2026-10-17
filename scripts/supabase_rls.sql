-- ============================================================================
--  Shoreline City — Protección de tablas en Supabase
-- ============================================================================
--  Supabase expone el esquema "public" en su Data API. Sin RLS, cualquiera con
--  la llave pública (anon) podría leer las tablas sin pasar por el login.
--
--  Este script activa RLS en todas las tablas SIN crear políticas, de modo que
--  la Data API no devuelve nada. La aplicación no se ve afectada: se conecta
--  con el usuario "postgres", dueño de las tablas, que no está sujeto a RLS.
--
--  Ejecutar en Supabase > SQL Editor después del primer despliegue (cuando la
--  app ya creó las tablas) y de nuevo si se agregan tablas.
-- ============================================================================
do $$
declare t record;
begin
  for t in select tablename from pg_tables where schemaname = 'public' loop
    execute format('alter table public.%I enable row level security', t.tablename);
  end loop;
end $$;

-- Verificación: todas las filas deben mostrar rowsecurity = true.
select tablename, rowsecurity from pg_tables where schemaname = 'public' order by 1;
