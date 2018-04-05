--
-- PostgreSQL database dump
--

--
-- Name: db2_mvtlot; Type: TABLE; Schema: public
--

CREATE TABLE db2_mvtlot (
    id integer NOT NULL,
    mltart character varying,
    mltlot character varying,
    mltnum double precision,
    mltsuc character varying,
    mltssu character varying,
    mltctr character varying,
    mltsui double precision,
    mltnli double precision,
    mltlig double precision,
    mltnne double precision,
    mltnfa double precision,
    mltnff character varying,
    mltdss double precision,
    mltdaa double precision,
    mltdmm double precision,
    mltdjj double precision,
    mltquc double precision,
    mltcnr character varying,
    mltlll double precision
);


--
-- Name: db2_mvtlot_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE db2_mvtlot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: db2_mvtlot_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE db2_mvtlot_id_seq OWNED BY db2_mvtlot.id;


--
-- Name: db2_mvtlot id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY db2_mvtlot ALTER COLUMN id SET DEFAULT nextval('db2_mvtlot_id_seq'::regclass);

--
-- Name: db2_mvtlot_id_seq; Type: SEQUENCE SET; Schema: public
--

SELECT pg_catalog.setval('db2_mvtlot_id_seq', 1, false);


--
-- Name: db2_mvtlot db2_mvtlot_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY db2_mvtlot
    ADD CONSTRAINT db2_mvtlot_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

