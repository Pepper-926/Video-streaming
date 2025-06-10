--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: toggle_like_dislike(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.toggle_like_dislike() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- Buscar si ya existe una reacción igual
  IF EXISTS (
    SELECT 1 FROM likes_dislikes_videos
    WHERE id_usuario = NEW.id_usuario AND id_video = NEW.id_video
  ) THEN
    -- Solo cambiar si el valor es diferente
    IF EXISTS (
      SELECT 1 FROM likes_dislikes_videos
      WHERE id_usuario = NEW.id_usuario AND id_video = NEW.id_video
      AND tipo_reaccion <> NEW.tipo_reaccion
    ) THEN
      UPDATE likes_dislikes_videos
      SET tipo_reaccion = NEW.tipo_reaccion,
          fecha_reaccion = CURRENT_TIMESTAMP
      WHERE id_usuario = NEW.id_usuario AND id_video = NEW.id_video;
    END IF;

    -- Cancelar la inserción
    RETURN NULL;
  ELSE
    -- Permitir inserción si no existe
    RETURN NEW;
  END IF;
END;
$$;


ALTER FUNCTION public.toggle_like_dislike() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: canales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.canales (
    id_canal integer NOT NULL,
    nombre_canal character varying(30) NOT NULL,
    id_usuario_id integer NOT NULL
);


ALTER TABLE public.canales OWNER TO postgres;

--
-- Name: canales_id_canal_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.canales ALTER COLUMN id_canal ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.canales_id_canal_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: comentarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comentarios (
    id_comentario integer NOT NULL,
    texto text NOT NULL,
    revisado boolean DEFAULT false NOT NULL,
    fecha_comentado timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id_video integer NOT NULL,
    id_usuario integer NOT NULL,
    id_respuesta integer
);


ALTER TABLE public.comentarios OWNER TO postgres;

--
-- Name: comentarios_id_comentario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.comentarios ALTER COLUMN id_comentario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.comentarios_id_comentario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: etiquetas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.etiquetas (
    id_etiqueta integer NOT NULL,
    categoria character varying(15) NOT NULL,
    descripcion character varying(50) NOT NULL
);


ALTER TABLE public.etiquetas OWNER TO postgres;

--
-- Name: etiquetas_id_etiqueta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.etiquetas ALTER COLUMN id_etiqueta ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.etiquetas_id_etiqueta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: historial; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historial (
    id integer NOT NULL,
    id_usuario integer NOT NULL,
    id_video integer NOT NULL,
    fecha_visto timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    eliminado boolean DEFAULT false NOT NULL
);


ALTER TABLE public.historial OWNER TO postgres;

--
-- Name: historial_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historial_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historial_id_seq OWNER TO postgres;

--
-- Name: historial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historial_id_seq OWNED BY public.historial.id;


--
-- Name: likes_dislikes_videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.likes_dislikes_videos (
    id_usuario integer NOT NULL,
    id_video integer NOT NULL,
    tipo_reaccion boolean NOT NULL,
    fecha_reaccion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id integer NOT NULL
);


ALTER TABLE public.likes_dislikes_videos OWNER TO postgres;

--
-- Name: likes_dislikes_videos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.likes_dislikes_videos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.likes_dislikes_videos_id_seq OWNER TO postgres;

--
-- Name: likes_dislikes_videos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.likes_dislikes_videos_id_seq OWNED BY public.likes_dislikes_videos.id;


--
-- Name: passwordresettoken; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passwordresettoken (
    id integer NOT NULL,
    id_usuario integer NOT NULL,
    token character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_used boolean DEFAULT false
);


ALTER TABLE public.passwordresettoken OWNER TO postgres;

--
-- Name: passwordresettoken_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.passwordresettoken_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.passwordresettoken_id_seq OWNER TO postgres;

--
-- Name: passwordresettoken_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.passwordresettoken_id_seq OWNED BY public.passwordresettoken.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id_rol integer NOT NULL,
    rol character varying(10) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.roles ALTER COLUMN id_rol ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.roles_id_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: seguidores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seguidores (
    id_usuario integer NOT NULL,
    seguidor integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.seguidores OWNER TO postgres;

--
-- Name: seguidores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.seguidores ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.seguidores_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    nombre character varying(16) NOT NULL,
    a_pat character varying(16),
    a_mat character varying(16),
    nacimiento date NOT NULL,
    correo character varying(50) NOT NULL,
    contra character varying(64) NOT NULL,
    foto_perfil character varying(64),
    id_rol integer NOT NULL
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.usuarios ALTER COLUMN id_usuario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.usuarios_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos (
    id_video integer NOT NULL,
    link character varying(128) NOT NULL,
    calificacion numeric(2,1),
    titulo character varying(30) NOT NULL,
    descripcion text,
    estado boolean DEFAULT false NOT NULL,
    revisado boolean DEFAULT false NOT NULL,
    publico boolean DEFAULT false NOT NULL,
    fecha_publicado timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    miniatura character varying(64),
    id_canal integer NOT NULL,
    conversion_completa boolean DEFAULT false,
    token_acceso_privado character varying(64),
    CONSTRAINT videos_calificacion_check CHECK (((calificacion >= (0)::numeric) AND (calificacion <= (5)::numeric)))
);


ALTER TABLE public.videos OWNER TO postgres;

--
-- Name: videos_etiquetas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos_etiquetas (
    id_video integer NOT NULL,
    id_etiqueta integer NOT NULL
);


ALTER TABLE public.videos_etiquetas OWNER TO postgres;

--
-- Name: videos_id_video_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.videos ALTER COLUMN id_video ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.videos_id_video_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: vista_canal_de_video; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_canal_de_video AS
 SELECT v.id_video,
    v.publico,
    c.nombre_canal,
    u.foto_perfil
   FROM ((public.videos v
     JOIN public.canales c ON ((v.id_canal = c.id_canal)))
     JOIN public.usuarios u ON ((c.id_usuario_id = u.id_usuario)));


ALTER VIEW public.vista_canal_de_video OWNER TO postgres;

--
-- Name: vw_videos_con_etiquetas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_videos_con_etiquetas AS
 SELECT row_number() OVER () AS id,
    v.id_video,
    v.publico,
    e.categoria
   FROM ((public.videos v
     JOIN public.videos_etiquetas ve ON ((v.id_video = ve.id_video)))
     JOIN public.etiquetas e ON ((ve.id_etiqueta = e.id_etiqueta)));


ALTER VIEW public.vw_videos_con_etiquetas OWNER TO postgres;

--
-- Name: vwdetalle_video; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vwdetalle_video AS
SELECT
    NULL::integer AS id_video,
    NULL::character varying(128) AS link,
    NULL::numeric(2,1) AS calificacion,
    NULL::character varying(30) AS titulo,
    NULL::boolean AS publico,
    NULL::character varying(64) AS token_acceso_privado,
    NULL::text AS descripcion,
    NULL::timestamp without time zone AS fecha_publicado,
    NULL::character varying(64) AS miniatura,
    NULL::boolean AS revisado,
    NULL::character varying(30) AS nombre_canal,
    NULL::character varying(64) AS foto_perfil,
    NULL::bigint AS seguidores,
    NULL::bigint AS me_gusta,
    NULL::bigint AS no_me_gusta,
    NULL::bigint AS reproducciones;


ALTER VIEW public.vwdetalle_video OWNER TO postgres;

--
-- Name: historial id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial ALTER COLUMN id SET DEFAULT nextval('public.historial_id_seq'::regclass);


--
-- Name: likes_dislikes_videos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.likes_dislikes_videos ALTER COLUMN id SET DEFAULT nextval('public.likes_dislikes_videos_id_seq'::regclass);


--
-- Name: passwordresettoken id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordresettoken ALTER COLUMN id SET DEFAULT nextval('public.passwordresettoken_id_seq'::regclass);


--
-- Data for Name: canales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.canales (id_canal, nombre_canal, id_usuario_id) FROM stdin;
3	CanalDaniel	3
4	MundoDeMonica	4
5	LuisExploraCode	5
6	ivan	6
9	reflex	10
10	hash	11
11	cisco	12
12	Prueba	13
14	aaaa	15
15	Pepper_9262	16
18	Pepper_926	19
19	Tenoch	20
23	Natal.IA	24
24	zuby	25
26	TechNews	27
27	Prueba produccion	28
29	OVERTMV	30
30	Jario	31
31	Tecnoch 	32
\.


--
-- Data for Name: comentarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comentarios (id_comentario, texto, revisado, fecha_comentado, id_video, id_usuario, id_respuesta) FROM stdin;
12	a	f	2025-05-07 05:01:39.703594	71	19	\N
16	Hola gfa, como andamos	f	2025-05-07 19:41:21.935496	71	19	\N
31	aaaa	f	2025-05-09 01:36:42.69896	71	19	\N
32	aa	f	2025-05-09 01:43:32.958641	71	19	16
37	Hola mundo	f	2025-05-11 01:06:11.51545	80	19	\N
38	Hello World	f	2025-05-11 01:06:25.35984	80	19	37
39	aaa	f	2025-05-12 02:27:08.878039	78	19	\N
40	Esta es una prueba	f	2025-05-12 02:27:18.692158	78	19	\N
41	aa	f	2025-05-12 02:31:15.865613	78	19	\N
42	Ayudaaaaaaaaa	f	2025-05-12 02:34:44.221497	78	19	\N
45	Fabuloso	f	2025-05-12 15:55:00.159034	84	19	\N
51	Increible	f	2025-05-13 01:29:59.523835	87	19	\N
52	Hola mundo	f	2025-05-13 17:20:50.85808	76	19	\N
53	Comentario solo visible para el admin	f	2025-05-13 17:52:21.717483	99	19	\N
54	Comentario solo visible para el admin	f	2025-05-13 18:35:49.102244	102	19	\N
55	Este tambien	f	2025-05-13 18:35:57.802869	102	19	54
17	aaa	t	2025-05-07 20:32:33.70349	73	19	\N
18	lo se	t	2025-05-07 20:32:44.791291	73	19	17
19	Hola mama	t	2025-05-07 20:43:21.750827	73	19	\N
20	aaa	t	2025-05-07 20:55:02.883809	73	19	\N
43	Increible video	t	2025-05-12 04:23:11.595563	73	24	\N
56	Increible video!!!	f	2025-05-13 18:46:01.41034	92	24	\N
57	Me gusto mucho	f	2025-05-13 18:46:36.282211	73	24	\N
61	Que pro	f	2025-05-20 19:53:43.103759	107	19	\N
62	Que malo	f	2025-05-20 19:53:49.192992	107	19	61
\.


--
-- Data for Name: etiquetas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.etiquetas (id_etiqueta, categoria, descripcion) FROM stdin;
1	Programación	Temas relacionados con escribir código
2	IA	Inteligencia artificial y aprendizaje automático
3	Ciberseguridad	Seguridad informática y hacking ético
4	Web	Desarrollo de sitios y aplicaciones web
5	Bases de Datos	Diseño y uso de sistemas de bases de datos
6	Redes	Conceptos de redes y telecomunicaciones
7	Sistemas	Sistemas operativos y administración
8	Frontend	Interfaz de usuario y tecnologías visuales
9	Backend	Lógica del servidor y APIs
10	DevOps	Integración y despliegue continuo
11	Mobile	Desarrollo de apps móviles
12	Cloud	Servicios y arquitecturas en la nube
\.


--
-- Data for Name: historial; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.historial (id, id_usuario, id_video, fecha_visto, eliminado) FROM stdin;
344	19	76	2025-05-13 03:46:59.18622	f
347	19	98	2025-05-13 14:55:41.206318	f
350	19	99	2025-05-13 17:46:52.160739	f
353	19	78	2025-05-13 18:26:21.553852	f
356	24	73	2025-05-13 18:46:22.003382	f
362	19	102	2025-05-13 21:17:57.579423	f
365	19	102	2025-05-14 02:18:35.56786	f
215	19	76	2025-05-09 01:34:33.67116	f
218	19	71	2025-05-09 01:43:03.548279	f
366	19	82	2025-05-14 02:24:51.599918	f
369	19	84	2025-05-18 03:01:08.154258	f
372	19	71	2025-05-20 16:16:24.053803	f
375	19	102	2025-05-20 18:39:19.36092	f
376	19	107	2025-05-20 19:52:09.260336	f
263	19	78	2025-05-10 22:30:13.477113	f
266	19	71	2025-05-10 22:33:24.941564	f
269	19	73	2025-05-10 22:47:31.196497	f
275	19	80	2025-05-11 01:01:32.450219	f
279	19	80	2025-05-11 20:39:20.68774	f
285	19	80	2025-05-11 21:35:55.298095	f
293	19	78	2025-05-12 02:31:09.534644	f
296	19	82	2025-05-12 02:52:01.550706	f
299	19	83	2025-05-12 03:11:38.29915	f
302	19	76	2025-05-12 04:20:37.677794	f
305	24	80	2025-05-12 04:24:28.007349	f
308	19	84	2025-05-12 05:55:38.242232	f
311	19	80	2025-05-12 13:00:51.23602	f
325	19	87	2025-05-12 16:53:06.460763	f
328	19	76	2025-05-12 16:58:25.819845	f
329	19	87	2025-05-12 16:58:41.115571	f
332	19	78	2025-05-12 22:56:54.091462	f
334	19	80	2025-05-13 00:23:33.329713	f
335	19	80	2025-05-13 00:23:38.885606	f
337	19	87	2025-05-13 01:29:44.518159	f
338	19	87	2025-05-13 01:32:44.794482	f
342	19	78	2025-05-13 03:30:54.034586	f
345	19	92	2025-05-13 03:50:17.265334	f
348	19	78	2025-05-13 15:13:29.072931	f
351	19	99	2025-05-13 17:52:09.331043	f
354	19	102	2025-05-13 18:35:38.138777	f
357	19	78	2025-05-13 19:34:30.751745	f
360	19	102	2025-05-13 21:17:08.588283	f
363	19	102	2025-05-13 21:18:53.426489	f
367	19	87	2025-05-15 17:59:32.111187	f
216	19	76	2025-05-09 01:34:42.756379	f
219	19	71	2025-05-09 01:43:17.422226	f
370	19	98	2025-05-18 20:47:11.917325	f
373	24	78	2025-05-20 18:31:28.18646	f
377	19	98	2025-05-20 19:53:59.933411	f
249	19	73	2025-05-09 20:07:08.693243	f
264	19	71	2025-05-10 22:30:24.530249	f
267	19	71	2025-05-10 22:41:01.245835	f
280	19	80	2025-05-11 20:40:34.813379	f
286	19	80	2025-05-11 21:36:22.905059	f
291	19	78	2025-05-12 02:27:03.080896	f
294	19	78	2025-05-12 02:34:29.886352	f
297	19	82	2025-05-12 02:52:49.464978	f
300	19	73	2025-05-12 04:15:58.295679	f
303	24	73	2025-05-12 04:22:59.497332	f
306	24	73	2025-05-12 05:14:22.086619	f
309	19	78	2025-05-12 12:58:06.449688	f
314	19	84	2025-05-12 15:54:43.359469	f
322	19	78	2025-05-12 16:44:28.562214	f
2	19	71	2025-05-04 18:04:43.282259	f
3	19	71	2025-05-04 18:13:51.424204	f
4	19	71	2025-05-05 18:31:55.063566	f
5	19	71	2025-05-05 18:40:07.153667	f
6	19	71	2025-05-05 18:41:31.656868	f
7	19	71	2025-05-05 18:44:10.274912	f
8	19	71	2025-05-05 18:44:39.069845	f
9	19	71	2025-05-05 18:44:41.962945	f
10	19	71	2025-05-05 18:57:35.196604	f
15	19	71	2025-05-05 19:08:52.16375	f
16	19	71	2025-05-05 19:10:10.895354	f
17	19	71	2025-05-05 19:10:26.649256	f
18	19	71	2025-05-05 19:10:32.074016	f
19	19	71	2025-05-05 19:10:48.246177	f
20	19	71	2025-05-05 19:11:11.644792	f
21	19	71	2025-05-05 19:11:42.660411	f
22	19	71	2025-05-05 19:12:04.419322	f
23	19	71	2025-05-06 12:15:19.042369	f
25	19	71	2025-05-06 12:16:02.760004	f
26	19	71	2025-05-06 12:31:24.412825	f
27	19	71	2025-05-06 12:33:00.038906	f
28	19	71	2025-05-06 18:48:00.106055	f
30	19	71	2025-05-06 18:49:53.770131	f
32	19	71	2025-05-06 22:14:00.174685	f
33	19	71	2025-05-06 22:39:14.624138	f
34	19	71	2025-05-06 22:39:48.045679	f
35	19	71	2025-05-06 22:41:25.82805	f
36	19	71	2025-05-06 22:42:43.86683	f
37	19	71	2025-05-06 22:43:23.194808	f
38	19	71	2025-05-06 22:43:33.525848	f
39	20	71	2025-05-06 22:46:19.386367	f
40	20	71	2025-05-06 22:47:29.048682	f
41	20	71	2025-05-06 22:48:40.166393	f
42	20	71	2025-05-06 22:50:02.14676	f
43	20	71	2025-05-06 22:50:22.356745	f
44	20	71	2025-05-06 22:51:24.616847	f
45	19	71	2025-05-06 22:58:41.937546	f
46	19	71	2025-05-06 22:59:08.577882	f
47	19	71	2025-05-06 23:00:45.927702	f
48	19	71	2025-05-06 23:01:18.664675	f
49	19	71	2025-05-06 23:01:36.991555	f
50	19	71	2025-05-06 23:01:47.522279	f
51	19	71	2025-05-06 23:01:54.130826	f
52	19	71	2025-05-06 23:03:15.424482	f
53	19	71	2025-05-06 23:04:19.197643	f
54	19	71	2025-05-06 23:08:56.94639	f
55	19	71	2025-05-06 23:11:17.568013	f
65	19	71	2025-05-06 23:58:53.21599	f
70	19	71	2025-05-07 13:16:25.040297	f
72	19	71	2025-05-07 13:16:53.787436	f
73	19	71	2025-05-07 13:41:00.080275	f
74	19	71	2025-05-07 14:08:51.940007	f
76	19	73	2025-05-07 14:10:44.949247	f
77	19	73	2025-05-07 14:32:26.873029	f
78	19	73	2025-05-07 14:43:13.781469	f
79	19	73	2025-05-07 14:44:34.218789	f
80	19	73	2025-05-07 14:50:26.251452	f
81	19	73	2025-05-07 14:50:53.000857	f
82	19	73	2025-05-07 14:51:02.287148	f
83	19	73	2025-05-07 14:54:03.721086	f
84	19	73	2025-05-07 14:54:23.229716	f
85	19	73	2025-05-07 14:54:38.754338	f
86	19	71	2025-05-07 14:56:06.075286	f
324	19	87	2025-05-12 16:52:59.89761	f
343	19	71	2025-05-13 03:43:37.314574	f
349	19	76	2025-05-13 17:20:34.461686	f
352	19	99	2025-05-13 17:53:55.623911	f
355	24	92	2025-05-13 18:45:51.46224	f
98	19	71	2025-05-07 19:24:53.68655	f
99	19	71	2025-05-07 19:29:51.129265	f
100	19	71	2025-05-07 19:32:05.487316	f
101	19	71	2025-05-07 19:37:06.23154	f
102	19	71	2025-05-07 19:39:45.946988	f
103	19	71	2025-05-07 19:40:51.780527	f
104	19	71	2025-05-07 19:40:57.278107	f
105	19	71	2025-05-07 19:41:17.48416	f
106	19	71	2025-05-07 19:41:51.776815	f
107	19	71	2025-05-07 19:42:09.71253	f
108	19	71	2025-05-07 19:42:46.957855	f
109	19	71	2025-05-07 19:42:57.310361	f
110	19	71	2025-05-07 19:43:10.419797	f
111	19	71	2025-05-07 19:45:13.342336	f
112	19	71	2025-05-07 19:45:33.366652	f
361	19	102	2025-05-13 21:17:37.01837	f
114	19	71	2025-05-08 07:28:00.268694	f
115	19	71	2025-05-08 07:28:31.254634	f
116	19	71	2025-05-08 07:33:17.397524	f
364	24	102	2025-05-13 21:45:24.510696	f
368	19	106	2025-05-15 18:17:21.341586	f
371	19	87	2025-05-19 23:13:14.57825	f
374	19	78	2025-05-20 18:32:11.734381	f
129	19	71	2025-05-08 08:50:31.294799	f
135	19	71	2025-05-08 10:45:07.913123	f
136	19	71	2025-05-08 10:55:50.067282	f
137	19	71	2025-05-08 10:56:13.15209	f
138	19	71	2025-05-08 10:56:21.134995	f
139	19	71	2025-05-08 10:56:44.457554	f
166	19	71	2025-05-08 18:18:22.37862	f
167	19	71	2025-05-08 18:23:24.130394	f
169	19	73	2025-05-08 18:28:44.651326	f
171	19	73	2025-05-08 18:28:49.105009	f
172	19	71	2025-05-08 18:28:50.095174	f
173	19	71	2025-05-08 18:32:44.947265	f
174	19	71	2025-05-08 18:32:47.388845	f
175	19	71	2025-05-08 18:34:35.648082	f
176	19	71	2025-05-08 18:36:28.083227	f
177	19	71	2025-05-08 18:36:30.097826	f
178	19	71	2025-05-08 18:36:40.511395	f
214	19	76	2025-05-09 01:32:14.082536	f
217	19	71	2025-05-09 01:35:01.187178	f
220	19	71	2025-05-09 01:43:54.991541	f
235	19	73	2025-05-09 04:25:55.498906	f
250	19	76	2025-05-09 20:17:42.85649	f
262	19	78	2025-05-10 22:29:01.009722	f
265	19	78	2025-05-10 22:30:30.119588	f
268	19	71	2025-05-10 22:41:11.456929	f
271	19	73	2025-05-11 00:49:22.672776	f
278	19	73	2025-05-11 20:39:19.190875	f
281	19	71	2025-05-11 20:42:07.807244	f
284	19	71	2025-05-11 21:35:52.889298	f
289	19	73	2025-05-12 02:19:04.216764	f
292	19	78	2025-05-12 02:29:18.027098	f
295	19	78	2025-05-12 02:44:04.808973	f
298	19	83	2025-05-12 03:03:48.083477	f
301	19	80	2025-05-12 04:16:45.738785	f
304	24	83	2025-05-12 04:23:26.196875	f
307	24	76	2025-05-12 05:14:33.357996	f
310	19	78	2025-05-12 12:58:08.197621	f
\.


--
-- Data for Name: likes_dislikes_videos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.likes_dislikes_videos (id_usuario, id_video, tipo_reaccion, fecha_reaccion, id) FROM stdin;
19	76	t	\N	240
19	102	t	\N	246
24	102	f	\N	249
19	84	t	\N	251
19	71	f	\N	252
24	78	f	\N	253
19	107	t	\N	255
19	80	t	\N	199
19	73	t	\N	207
19	83	t	\N	212
24	73	t	\N	213
24	80	t	\N	214
19	87	t	\N	235
\.


--
-- Data for Name: passwordresettoken; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passwordresettoken (id, id_usuario, token, created_at, is_used) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id_rol, rol) FROM stdin;
1	admin
2	usuario
\.


--
-- Data for Name: seguidores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.seguidores (id_usuario, seguidor, id) FROM stdin;
19	24	29
24	19	31
31	19	34
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id_usuario, nombre, a_pat, a_mat, nacimiento, correo, contra, foto_perfil, id_rol) FROM stdin;
3	Daniel	Álvarez	Mata	2001-03-25	daniel.alvarez@example.com	as98df76as8d	perfiles/fotos_de_perfil/avatar-defecto.svg	2
4	Mónica	Hernández	López	1999-07-01	monica.hl@example.com	9asd8f76a9sd	perfiles/fotos_de_perfil/avatar-defecto.svg	2
5	Luis	Torres	Martínez	2000-01-17	luis.torres@example.com	asdf789a7sd6	perfiles/fotos_de_perfil/avatar-defecto.svg	2
6	ivan	rodriguez	mendez	2004-03-08	ivanmendez@example.com	Ivan123$	perfiles/fotos_de_perfil/avatar-defecto.svg	2
7	ana	dom	rut	2004-05-13	ana.rut@example.com	Ana1234$	perfiles/fotos_de_perfil/avatar-defecto.svg	2
9	Gabriel	García	Cortés	2006-09-11	a@s	Pepper_926	perfiles/fotos_de_perfil/avatar-defecto.svg	2
10	ivan	rodriguez	mendez	2004-06-29	gaelguzman@example.com	Gael123$	perfiles/fotos_de_perfil/avatar-defecto.svg	2
11	Anette	Ruíz	Saucedo	2004-06-22	anetterusau@gmail.com	d125a74743aa34fbe6369e65e0d910dce0d76ee0a7336a43878be3f84b5a9452	perfiles/fotos_de_perfil/avatar-defecto.svg	2
12	pedro	velazquez	romo	2003-11-18	pedritosola@gmail.com	e662f169989cca6cff29ecf17989f4c8b22e06ec8a6952b4dcbb65f6dfd5ec02	perfiles/fotos_de_perfil/avatar-defecto.svg	2
13	Misuki	Lopez	Ortiz	2004-06-23	misuki@gmail.com	17346e54bf5c3eea1375ec451d4da94a947d35770b674bd22d44dc98fbfe7976	perfiles/fotos_de_perfil/avatar-defecto.svg	2
15	Angel	García	Cortés	2007-01-09	aaaaa@gmail.com	aaaa	perfiles/fotos_de_perfil/avatar-defecto.svg	2
16	Gabriel	García	Cortés	2004-06-15	prueba123@gmail.com	0d9d09e157f7c29a43c02e57f081915d6fe2f10da1710672086f8ad73bb95cb2	perfiles/fotos_de_perfil/avatar-defecto.svg	2
20	Gabriel	García	Cortés	2001-06-06	t@m	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	perfiles/fotos_de_perfil/avatar-defecto.svg	2
19	Gabriel	García	Cortés	2009-03-05	gaboland1405@gmail.com	853cf33f88bec1a44586d4c18a8c539a34f4997928af2f6f2ea0b6bb2b6f38a4	perfiles/fotos_de_perfil/foto_perfil19.svg	1
24	Manuel	Maria	Ponce	1997-11-13	manuel@gmail.com	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	perfiles/fotos_de_perfil/foto_perfil24.jpeg	2
25	jose 	nunez	mitchel	2005-01-19	josemanuel.n@hotmail.com	0adc7daa27b3f19591094e4985636dfda86ae66b62df56345a1f79cad8a9b82a	perfiles/fotos_de_perfil/avatar-defecto.svg	2
27	Dummy	user	\N	2001-07-17	dummy@gmail.com	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	perfiles/fotos_de_perfil/avatar-defecto.svg	2
28	Dumm2	a	\N	1988-11-12	dummy2@a	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	perfiles/fotos_de_perfil/avatar-defecto.svg	2
30	Tenoch	Moreno	Velarde	2004-02-24	tenochmoreno24@gmail.com	ba022c3880f02d5d142d232954ebe23684209a0c314e6868094bf0c9ebc1204a	perfiles/fotos_de_perfil/avatar-defecto.svg	2
31	jairo	\N	\N	2003-07-16	jairos@gmail.com	d8753ab2bd74c6bdad3f960795aed6a2b7cdbf0f05c8274fed33e067380ba670	perfiles/fotos_de_perfil/foto_perfil31.jpg	2
32	Tenoch 	Moreno	Velarde	2005-02-24	tenoch.moreno@edu.uag.mx	1a18eef50c0f631ccc1b98b287b90caa8e89ff93c5d4e008c81a4a56483a73e2	perfiles/fotos_de_perfil/avatar-defecto.svg	2
\.


--
-- Data for Name: videos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.videos (id_video, link, calificacion, titulo, descripcion, estado, revisado, publico, fecha_publicado, miniatura, id_canal, conversion_completa, token_acceso_privado) FROM stdin;
102	videos/video102/index.m3u8	\N	Probamos la nueva IA!!!!	El fin de ChatGPT?	t	t	t	2025-05-14 00:34:22.950523	videos/video102/miniatura.jpg	23	t	\N
92	videos/video92/index.m3u8	\N	Prueba produccion	aaa	t	t	t	2025-05-13 09:49:55.801874	videos/video92/miniatura.jpg	18	t	\N
104	videos/video104/index.m3u8	\N	Prueba 2	Admin	t	t	t	2025-05-14 01:11:22.125858	videos/video104/miniatura.jpg	18	t	\N
78	videos/video78/index.m3u8	\N	JS essentials 1	Curso introductorio	t	t	t	2025-05-12 10:21:41.505368	videos/video78/miniatura.jpg	18	t	\N
80	videos/video80/index.m3u8	\N	Prueba en MAC	Prueba hecha en MAC	t	t	t	2025-05-12 06:59:29.849904	videos/video80/miniatura.jpg	18	t	\N
73	videos/video73/index.m3u8	\N	Prueba css subida	aaa	t	t	t	2025-05-09 14:09:51.803494	videos/video73/miniatura.jpg	18	t	\N
76	videos/video76/index.m3u8	\N	Prueba para la hora de subida	PRobando la hora	t	t	t	2025-05-10 19:31:16.449917	videos/video76/miniatura.jpg	18	t	\N
106	videos/video106/index.m3u8	\N	Proyecto HealthCAT	Gabo me pidio que lo subiera aqui y me estuvo enfadando, asi que no tuve opcion y lo subi	t	t	t	2025-05-16 00:04:30.459892	videos/video106/miniatura.jpg	29	t	\N
98	videos/video98/index.m3u8	\N	IA		t	t	t	2025-05-13 20:54:51.769571	videos/video98/miniatura.jpg	18	t	\N
107	videos/video107/index.m3u8	\N	video precenta	gg	t	t	t	2025-05-21 01:47:43.369493	videos/video107/miniatura.jpg	30	t	\N
83	videos/video83/index.m3u8	\N	Prueba	Prueba hecha en un celular	t	t	t	2025-05-12 21:02:52.682242	videos/video83/miniatura.jpg	18	t	\N
71	videos/video71/index.m3u8	\N	Botsito captado en camara	Manco botsito	t	t	t	2025-05-05 20:23:18.313395	videos/video71/miniatura.jpg	18	t	\N
84	videos/video84/index.m3u8	\N	Que es un CDN?	Hoy veremos que es cloudfront, el cdn de AWS	t	t	t	2025-05-12 17:50:49.874865	videos/video84/miniatura.jpg	23	t	\N
108	videos/video108/index.m3u8	\N	hola	no se	t	f	t	2025-05-20 19:52:05.277347	videos/video108/miniatura.jpg	31	t	\N
93	videos/video93/index.m3u8	\N	Prueba 2 produccion		t	t	t	2025-05-13 09:52:46.412152	videos/video93/miniatura.jpg	18	t	\N
82	videos/video82/index.m3u8	\N	Prueba de produccion	aaaa	t	t	t	2025-05-12 20:50:15.683325	videos/video82/miniatura.jpg	18	t	\N
87	videos/video87/index.m3u8	\N	VIdeo de Ingenieria		t	t	t	2025-05-13 04:50:05.305589	videos/video87/miniatura.jpg	18	t	\N
99	videos/video99/index.m3u8	\N	Redes II: VLANs		t	t	t	2025-05-13 23:45:44.090506	videos/video99/miniatura.jpg	18	t	\N
\.


--
-- Data for Name: videos_etiquetas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.videos_etiquetas (id_video, id_etiqueta) FROM stdin;
76	11
76	12
78	8
78	9
78	10
71	11
71	12
73	12
80	11
80	12
82	10
82	11
82	12
83	7
83	9
83	10
84	12
87	11
87	12
92	12
93	10
93	11
98	12
99	6
102	12
104	11
104	12
106	4
107	9
\.


--
-- Name: canales_id_canal_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.canales_id_canal_seq', 31, true);


--
-- Name: comentarios_id_comentario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comentarios_id_comentario_seq', 62, true);


--
-- Name: etiquetas_id_etiqueta_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.etiquetas_id_etiqueta_seq', 12, true);


--
-- Name: historial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.historial_id_seq', 377, true);


--
-- Name: likes_dislikes_videos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.likes_dislikes_videos_id_seq', 255, true);


--
-- Name: passwordresettoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.passwordresettoken_id_seq', 1, false);


--
-- Name: roles_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_rol_seq', 2, true);


--
-- Name: seguidores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seguidores_id_seq', 34, true);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_usuario_seq', 32, true);


--
-- Name: videos_id_video_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.videos_id_video_seq', 109, true);


--
-- Name: canales canales_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canales
    ADD CONSTRAINT canales_nombre_key UNIQUE (nombre_canal);


--
-- Name: canales canales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canales
    ADD CONSTRAINT canales_pkey PRIMARY KEY (id_canal);


--
-- Name: comentarios comentarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT comentarios_pkey PRIMARY KEY (id_comentario);


--
-- Name: etiquetas etiquetas_categoria_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.etiquetas
    ADD CONSTRAINT etiquetas_categoria_key UNIQUE (categoria);


--
-- Name: etiquetas etiquetas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.etiquetas
    ADD CONSTRAINT etiquetas_pkey PRIMARY KEY (id_etiqueta);


--
-- Name: historial historial_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial
    ADD CONSTRAINT historial_pkey PRIMARY KEY (id);


--
-- Name: historial historial_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial
    ADD CONSTRAINT historial_unique UNIQUE (id_usuario, id_video, fecha_visto);


--
-- Name: likes_dislikes_videos likes_dislikes_videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.likes_dislikes_videos
    ADD CONSTRAINT likes_dislikes_videos_pkey PRIMARY KEY (id);


--
-- Name: passwordresettoken passwordresettoken_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordresettoken
    ADD CONSTRAINT passwordresettoken_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_rol);


--
-- Name: roles roles_rol_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_rol_key UNIQUE (rol);


--
-- Name: seguidores seguidores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguidores
    ADD CONSTRAINT seguidores_pkey PRIMARY KEY (id);


--
-- Name: seguidores unique_usuario_seguidor; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguidores
    ADD CONSTRAINT unique_usuario_seguidor UNIQUE (id_usuario, seguidor);


--
-- Name: likes_dislikes_videos unique_usuario_video; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.likes_dislikes_videos
    ADD CONSTRAINT unique_usuario_video UNIQUE (id_usuario, id_video);


--
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- Name: videos_etiquetas videos_etiquetas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos_etiquetas
    ADD CONSTRAINT videos_etiquetas_pkey PRIMARY KEY (id_video, id_etiqueta);


--
-- Name: videos videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_pkey PRIMARY KEY (id_video);


--
-- Name: videos videos_token_acceso_privado_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_token_acceso_privado_key UNIQUE (token_acceso_privado);


--
-- Name: idx_comentarios_respuesta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_comentarios_respuesta ON public.comentarios USING btree (id_respuesta);


--
-- Name: idx_comentarios_revisado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_comentarios_revisado ON public.comentarios USING btree (revisado);


--
-- Name: idx_comentarios_video; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_comentarios_video ON public.comentarios USING btree (id_video);


--
-- Name: vwdetalle_video _RETURN; Type: RULE; Schema: public; Owner: postgres
--

CREATE OR REPLACE VIEW public.vwdetalle_video AS
 SELECT v.id_video,
    v.link,
    v.calificacion,
    v.titulo,
    v.publico,
    v.token_acceso_privado,
    v.descripcion,
    v.fecha_publicado,
    v.miniatura,
    v.revisado,
    c.nombre_canal,
    u.foto_perfil,
    count(DISTINCT s.seguidor) AS seguidores,
    count(DISTINCT
        CASE
            WHEN (l.tipo_reaccion = true) THEN l.id_usuario
            ELSE NULL::integer
        END) AS me_gusta,
    count(DISTINCT
        CASE
            WHEN (l.tipo_reaccion = false) THEN l.id_usuario
            ELSE NULL::integer
        END) AS no_me_gusta,
    count(h.id_usuario) AS reproducciones
   FROM (((((public.videos v
     LEFT JOIN public.historial h ON ((v.id_video = h.id_video)))
     LEFT JOIN public.likes_dislikes_videos l ON ((v.id_video = l.id_video)))
     JOIN public.canales c ON ((v.id_canal = c.id_canal)))
     JOIN public.usuarios u ON ((c.id_usuario_id = u.id_usuario)))
     LEFT JOIN public.seguidores s ON ((s.id_usuario = u.id_usuario)))
  GROUP BY v.id_video, v.link, v.calificacion, v.titulo, v.descripcion, v.fecha_publicado, v.miniatura, v.revisado, c.nombre_canal, u.foto_perfil;


--
-- Name: canales fk_canales_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canales
    ADD CONSTRAINT fk_canales_usuario FOREIGN KEY (id_usuario_id) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: comentarios fk_comentarios_respuesta; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT fk_comentarios_respuesta FOREIGN KEY (id_respuesta) REFERENCES public.comentarios(id_comentario) ON DELETE CASCADE;


--
-- Name: comentarios fk_comentarios_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT fk_comentarios_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: comentarios fk_comentarios_video; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT fk_comentarios_video FOREIGN KEY (id_video) REFERENCES public.videos(id_video) ON DELETE CASCADE;


--
-- Name: historial fk_historial_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial
    ADD CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: historial fk_historial_video; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial
    ADD CONSTRAINT fk_historial_video FOREIGN KEY (id_video) REFERENCES public.videos(id_video) ON DELETE CASCADE;


--
-- Name: likes_dislikes_videos fk_likes_dislikes_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.likes_dislikes_videos
    ADD CONSTRAINT fk_likes_dislikes_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: likes_dislikes_videos fk_likes_dislikes_video; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.likes_dislikes_videos
    ADD CONSTRAINT fk_likes_dislikes_video FOREIGN KEY (id_video) REFERENCES public.videos(id_video) ON DELETE CASCADE;


--
-- Name: seguidores fk_seguidor_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguidores
    ADD CONSTRAINT fk_seguidor_usuario FOREIGN KEY (seguidor) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: passwordresettoken fk_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordresettoken
    ADD CONSTRAINT fk_user FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: seguidores fk_usuario_seguidor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguidores
    ADD CONSTRAINT fk_usuario_seguidor FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: usuarios fk_usuarios_rol; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT fk_usuarios_rol FOREIGN KEY (id_rol) REFERENCES public.roles(id_rol) ON DELETE CASCADE;


--
-- Name: videos fk_videos_canal; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT fk_videos_canal FOREIGN KEY (id_canal) REFERENCES public.canales(id_canal) ON DELETE CASCADE;


--
-- Name: videos_etiquetas fk_videos_etiquetas_etiqueta; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos_etiquetas
    ADD CONSTRAINT fk_videos_etiquetas_etiqueta FOREIGN KEY (id_etiqueta) REFERENCES public.etiquetas(id_etiqueta) ON DELETE CASCADE;


--
-- Name: videos_etiquetas fk_videos_etiquetas_video; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos_etiquetas
    ADD CONSTRAINT fk_videos_etiquetas_video FOREIGN KEY (id_video) REFERENCES public.videos(id_video) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT CREATE ON SCHEMA public TO anette;
GRANT CREATE ON SCHEMA public TO backend;


--
-- Name: FUNCTION toggle_like_dislike(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.toggle_like_dislike() TO anette;
GRANT ALL ON FUNCTION public.toggle_like_dislike() TO backend;


--
-- Name: TABLE canales; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.canales TO anette;
GRANT ALL ON TABLE public.canales TO backend;


--
-- Name: SEQUENCE canales_id_canal_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.canales_id_canal_seq TO anette;
GRANT ALL ON SEQUENCE public.canales_id_canal_seq TO backend;


--
-- Name: TABLE comentarios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.comentarios TO anette;
GRANT ALL ON TABLE public.comentarios TO backend;


--
-- Name: SEQUENCE comentarios_id_comentario_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.comentarios_id_comentario_seq TO anette;
GRANT ALL ON SEQUENCE public.comentarios_id_comentario_seq TO backend;


--
-- Name: TABLE etiquetas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.etiquetas TO anette;
GRANT ALL ON TABLE public.etiquetas TO backend;


--
-- Name: SEQUENCE etiquetas_id_etiqueta_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.etiquetas_id_etiqueta_seq TO anette;
GRANT ALL ON SEQUENCE public.etiquetas_id_etiqueta_seq TO backend;


--
-- Name: TABLE historial; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.historial TO anette;
GRANT ALL ON TABLE public.historial TO backend;


--
-- Name: SEQUENCE historial_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.historial_id_seq TO anette;
GRANT ALL ON SEQUENCE public.historial_id_seq TO backend;


--
-- Name: TABLE likes_dislikes_videos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.likes_dislikes_videos TO anette;
GRANT ALL ON TABLE public.likes_dislikes_videos TO backend;


--
-- Name: SEQUENCE likes_dislikes_videos_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.likes_dislikes_videos_id_seq TO anette;
GRANT ALL ON SEQUENCE public.likes_dislikes_videos_id_seq TO backend;


--
-- Name: TABLE passwordresettoken; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.passwordresettoken TO anette;
GRANT ALL ON TABLE public.passwordresettoken TO backend;


--
-- Name: SEQUENCE passwordresettoken_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.passwordresettoken_id_seq TO anette;
GRANT ALL ON SEQUENCE public.passwordresettoken_id_seq TO backend;


--
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.roles TO anette;
GRANT ALL ON TABLE public.roles TO backend;


--
-- Name: SEQUENCE roles_id_rol_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.roles_id_rol_seq TO anette;
GRANT ALL ON SEQUENCE public.roles_id_rol_seq TO backend;


--
-- Name: TABLE seguidores; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.seguidores TO anette;
GRANT ALL ON TABLE public.seguidores TO backend;


--
-- Name: SEQUENCE seguidores_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.seguidores_id_seq TO anette;
GRANT ALL ON SEQUENCE public.seguidores_id_seq TO backend;


--
-- Name: TABLE usuarios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.usuarios TO anette;
GRANT ALL ON TABLE public.usuarios TO backend;


--
-- Name: SEQUENCE usuarios_id_usuario_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.usuarios_id_usuario_seq TO anette;
GRANT ALL ON SEQUENCE public.usuarios_id_usuario_seq TO backend;


--
-- Name: TABLE videos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.videos TO anette;
GRANT ALL ON TABLE public.videos TO backend;


--
-- Name: TABLE videos_etiquetas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.videos_etiquetas TO anette;
GRANT ALL ON TABLE public.videos_etiquetas TO backend;


--
-- Name: SEQUENCE videos_id_video_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.videos_id_video_seq TO anette;
GRANT ALL ON SEQUENCE public.videos_id_video_seq TO backend;


--
-- Name: TABLE vista_canal_de_video; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_canal_de_video TO anette;
GRANT ALL ON TABLE public.vista_canal_de_video TO backend;


--
-- Name: TABLE vw_videos_con_etiquetas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_videos_con_etiquetas TO anette;
GRANT ALL ON TABLE public.vw_videos_con_etiquetas TO backend;


--
-- Name: TABLE vwdetalle_video; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vwdetalle_video TO anette;
GRANT ALL ON TABLE public.vwdetalle_video TO backend;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO anette;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO backend;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO anette;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO backend;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO anette;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO backend;


--
-- PostgreSQL database dump complete
--

