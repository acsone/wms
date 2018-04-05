--
-- PostgreSQL database dump
--

--
-- Name: db2_pdetcdfo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE db2_pdetcdfo (
    id integer NOT NULL,
    dcfctr character varying,
    dcfsui integer,
    dcfuti integer,
    dcfnli double precision,
    dcfsuc character varying,
    dcfssu character varying,
    dcffou double precision,
    dcfcli double precision,
    dcfart character varying,
    dcflib character varying,
    dcfquc double precision,
    dcfqur double precision,
    dcfqul double precision,
    dcflss integer,
    dcflaa integer,
    dcflmm integer,
    dcfljj integer,
    dcfpac double precision,
    dcfprv double precision,
    dcfrem double precision,
    dcfres double precision,
    dcfunv double precision,
    dcfgro double precision,
    dcfsgr double precision,
    dcfcva double precision,
    dcfcan double precision,
    dcfsta double precision,
    dcfstb double precision,
    dcfstc double precision,
    dcfstf double precision,
    dcfpsp double precision,
    dcfnfa character varying,
    dcffss integer,
    dcffaa integer,
    dcffmm integer,
    dcffjj integer,
    dcfcss integer,
    dcfcaa integer,
    dcfcmm integer,
    dcfcjj integer,
    dcfmss integer,
    dcfmaa integer,
    dcfmmm integer,
    dcfmjj integer,
    dcfre character varying,
    order_id integer
);


--
-- Name: db2_pdetcdfo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE db2_pdetcdfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: db2_pdetcdfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE db2_pdetcdfo_id_seq OWNED BY db2_pdetcdfo.id;


--
-- Name: db2_pdetcdfo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pdetcdfo ALTER COLUMN id SET DEFAULT nextval('db2_pdetcdfo_id_seq'::regclass);

--
-- Name: db2_pdetcdfo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('db2_pdetcdfo_id_seq', 1, false);


--
-- Name: db2_pdetcdfo db2_pdetcdfo_dcfsui_dcffou_dcfsuc_dcfnli_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pdetcdfo
    ADD CONSTRAINT db2_pdetcdfo_dcfsui_dcffou_dcfsuc_dcfnli_key UNIQUE (dcfsui, dcffou, dcfsuc, dcfnli);


--
-- Name: db2_pdetcdfo db2_pdetcdfo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pdetcdfo
    ADD CONSTRAINT db2_pdetcdfo_pkey PRIMARY KEY (id);


--
-- Name: db2_pdetcdfo db2_pdetcdfo_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY db2_pdetcdfo
    ADD CONSTRAINT db2_pdetcdfo_order_id_fkey FOREIGN KEY (order_id) REFERENCES db2_pentcdfo(id);


--
-- PostgreSQL database dump complete
--

