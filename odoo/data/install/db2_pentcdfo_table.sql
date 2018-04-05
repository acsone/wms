--
-- PostgreSQL database dump
--

--
-- Name: db2_pentcdfo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE db2_pentcdfo (
    id integer NOT NULL,
    ecfctr character varying,
    ecfsui integer,
    ecfuti integer,
    ecftyc integer,
    ecfsuc character varying,
    ecfssu character varying,
    ecfdss integer,
    ecfdaa integer,
    ecfdmm integer,
    ecfdjj integer,
    ecfdiv double precision,
    ecffou double precision,
    ecfrin character varying,
    ecfrcl character varying,
    ecflss integer,
    ecflaa integer,
    ecflmm integer,
    ecfljj integer,
    ecfmdl integer,
    ecfrem double precision,
    ecfrms double precision,
    ecfdev double precision,
    ecftau double precision,
    ecfdel integer,
    ecfnal integer,
    ecfqua double precision,
    ecfed1 double precision,
    ecfcom double precision,
    ecfedc double precision,
    ecfncd double precision,
    ecfjes double precision,
    ecftes double precision,
    ecfnof character varying,
    ecffss integer,
    ecffaa integer,
    ecffmm integer,
    ecffjj integer,
    ecfcss integer,
    ecfcaa integer,
    ecfcmm integer,
    ecfcjj integer,
    ecfmss integer,
    ecfmaa integer,
    ecfmmm integer,
    ecfmjj integer,
    ecfpss integer,
    ecfpaa integer,
    ecfpmm integer,
    ecfpjj integer,
    ecfana character varying,
    ecfdnl double precision,
    ecfmto double precision,
    ecfsts double precision,
    ecfres character varying
);


--
-- Name: db2_pentcdfo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE db2_pentcdfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: db2_pentcdfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE db2_pentcdfo_id_seq OWNED BY db2_pentcdfo.id;


--
-- Name: db2_pentcdfo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pentcdfo ALTER COLUMN id SET DEFAULT nextval('db2_pentcdfo_id_seq'::regclass);


--
-- Name: db2_pentcdfo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('db2_pentcdfo_id_seq', 1, false);


--
-- Name: db2_pentcdfo db2_pentcdfo_ecfsui_ecffou_ecfsuc_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pentcdfo
    ADD CONSTRAINT db2_pentcdfo_ecfsui_ecffou_ecfsuc_key UNIQUE (ecfsui, ecffou, ecfsuc);


--
-- Name: db2_pentcdfo db2_pentcdfo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pentcdfo
    ADD CONSTRAINT db2_pentcdfo_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

