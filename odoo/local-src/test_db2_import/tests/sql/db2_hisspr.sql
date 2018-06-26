--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.5
-- Dumped by pg_dump version 9.6.3

--
-- Name: db2_hisspr; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE db2_hisspr (
    id integer NOT NULL,
    hpssuc character varying,
    hpsctr character varying,
    hpssui double precision,
    hpsnli double precision,
    hpssli double precision,
    hpsnfo double precision,
    hpsnfa character varying,
    hpsdat double precision,
    hpscpb character varying,
    hpsccd character varying,
    hpsccl character varying,
    hpssid character varying,
    hpssda double precision,
    hpssco character varying,
    hpssts character varying
);


--
-- Name: db2_hisspr_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE db2_hisspr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: db2_hisspr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE db2_hisspr_id_seq OWNED BY db2_hisspr.id;


--
-- Name: db2_hisspr id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_hisspr ALTER COLUMN id SET DEFAULT nextval('db2_hisspr_id_seq'::regclass);


--
-- Data for Name: db2_hisspr; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO db2_hisspr VALUES (1, '1', '101', 109686, 240, 1, 68250, '72127864', 20180607, '102', 'L', 'Q', 'CIOLLMA', 20180620, 'note de crédit reçue n° 090023', 'C');
INSERT INTO db2_hisspr VALUES (2, '1', '101', 109686, 300, 1, 68250, '72127864', 20180607, '104', 'L', 'Q', 'CIOLLMA', 20180620, 'note de crédit reçue n° 090024', 'C');


--
-- Name: db2_hisspr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('db2_hisspr_id_seq', 2, true);


--
-- Name: db2_hisspr db2_hisspr_hpssui_hpsnli_hpscpb_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_hisspr
    ADD CONSTRAINT db2_hisspr_hpssui_hpsnli_hpscpb_key UNIQUE (hpssui, hpsnli, hpscpb);


--
-- Name: db2_hisspr db2_hisspr_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_hisspr
    ADD CONSTRAINT db2_hisspr_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

