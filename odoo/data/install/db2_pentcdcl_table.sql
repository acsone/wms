--
-- PostgreSQL database dump
--

--
-- Name: db2_pentcdcl; Type: TABLE; Schema: public
--

CREATE TABLE db2_pentcdcl (
    id integer NOT NULL,
    eccctr character varying,
    eccsui integer,
    eccuti integer,
    eccrep integer,
    eccres integer,
    ecctyc integer,
    eccsuc character varying,
    eccssu character varying,
    eccdss integer,
    eccdaa integer,
    eccdmm integer,
    eccdjj integer,
    eccrgn double precision,
    eccrgf double precision,
    eccdiv double precision,
    ecccli double precision,
    eccclf double precision,
    eccrin character varying,
    eccrcl character varying,
    ecclss integer,
    ecclaa integer,
    ecclmm integer,
    eccljj integer,
    eccmdl integer,
    eccrem double precision,
    eccrms double precision,
    eccdev double precision,
    ecctau double precision,
    eccsec integer,
    ecctou integer,
    eccdel integer,
    eccnal integer,
    eccqua double precision,
    eccqte double precision,
    ecced1 double precision,
    ecced2 double precision,
    ecced3 double precision,
    ecccom double precision,
    eccedc double precision,
    eccnfa double precision,
    eccnne double precision,
    eccncd double precision,
    eccjes double precision,
    ecctes double precision,
    eccexo double precision,
    eccnof character varying,
    eccfss integer,
    eccfaa integer,
    eccfmm integer,
    eccfjj integer,
    ecccss integer,
    ecccaa integer,
    ecccmm integer,
    ecccjj integer,
    eccmss integer,
    eccmaa integer,
    eccmmm integer,
    eccmjj integer,
    eccpss integer,
    eccpaa integer,
    eccpmm integer,
    eccpjj integer,
    eccana character varying,
    eccdnl double precision,
    eccmto double precision,
    eccncr double precision,
    eccsts double precision,
    eccre character varying,
    ecccex double precision
);


--
-- Name: db2_pentcdcl_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE db2_pentcdcl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: db2_pentcdcl id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY db2_pentcdcl ALTER COLUMN id SET DEFAULT nextval('db2_pentcdcl_id_seq'::regclass);


--
-- Name: db2_pentcdcl_id_seq; Type: SEQUENCE SET; Schema: public
--

SELECT pg_catalog.setval('db2_pentcdcl_id_seq', 1, false);


--
-- Name: db2_pentcdcl db2_pentcdcl_eccsui_ecccli_eccsuc_key; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY db2_pentcdcl
    ADD CONSTRAINT db2_pentcdcl_eccsui_ecccli_eccsuc_key UNIQUE (eccsui, ecccli, eccsuc);


--
-- Name: db2_pentcdcl db2_pentcdcl_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY db2_pentcdcl
    ADD CONSTRAINT db2_pentcdcl_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

