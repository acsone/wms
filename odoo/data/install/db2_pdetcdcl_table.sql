--
-- PostgreSQL database dump
--

--
-- Name: db2_pdetcdcl; Type: TABLE; Schema: public
--

CREATE TABLE db2_pdetcdcl (
    id integer NOT NULL,
    dccctr character varying,
    dccsui integer,
    dccuti integer,
    dccnli double precision,
    dccsuc character varying,
    dccssu character varying,
    dccncl double precision,
    dcccli double precision,
    dccart character varying,
    dcclib character varying,
    dccquc double precision,
    dccqur double precision,
    dccqul double precision,
    dccexc double precision,
    dccaut double precision,
    dccbss integer,
    dccbaa integer,
    dccbse integer,
    dcclss integer,
    dcclaa integer,
    dcclmm integer,
    dccljj integer,
    dccpac double precision,
    dccprv double precision,
    dccpvd double precision,
    dccpvn double precision,
    dccpve double precision,
    dcctva double precision,
    dccrem double precision,
    dccres double precision,
    dccunv double precision,
    dccgro double precision,
    dccsgr double precision,
    dcccvv double precision,
    dcccan double precision,
    dcccgr double precision,
    dccsta double precision,
    dccstb double precision,
    dccstc double precision,
    dccstd double precision,
    dccste double precision,
    dccstf double precision,
    dccpsp double precision,
    dccnfa character varying,
    dccfss integer,
    dccfaa integer,
    dccfmm integer,
    dccfjj integer,
    dcccss integer,
    dcccaa integer,
    dcccmm integer,
    dcccjj integer,
    dccmss integer,
    dccmaa integer,
    dccmmm integer,
    dccmjj integer,
    dcclll integer,
    dcclop character varying,
    dccarc character varying,
    dccre character varying,
    order_id integer
);


--
-- Name: db2_pdetcdcl_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE db2_pdetcdcl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: db2_pdetcdcl id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY db2_pdetcdcl ALTER COLUMN id SET DEFAULT nextval('db2_pdetcdcl_id_seq'::regclass);


--
-- Name: db2_pdetcdcl_id_seq; Type: SEQUENCE SET; Schema: public
--

SELECT pg_catalog.setval('db2_pdetcdcl_id_seq', 1, false);


--
-- Name: db2_pdetcdcl db2_pdetcdcl_dccsui_dccncl_dccsuc_dccnli_key; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY db2_pdetcdcl
    ADD CONSTRAINT db2_pdetcdcl_dccsui_dccncl_dccsuc_dccnli_key UNIQUE (dccsui, dccncl, dccsuc, dccnli);


--
-- Name: db2_pdetcdcl db2_pdetcdcl_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY db2_pdetcdcl
    ADD CONSTRAINT db2_pdetcdcl_pkey PRIMARY KEY (id);


--
-- Name: db2_pdetcdcl db2_pdetcdcl_order_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY db2_pdetcdcl
    ADD CONSTRAINT db2_pdetcdcl_order_id_fkey FOREIGN KEY (order_id) REFERENCES db2_pentcdcl(id);


--
-- PostgreSQL database dump complete
--

