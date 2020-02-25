--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE beiweuser;
ALTER ROLE beiweuser WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'md5fd36226e6614aebafbf128a7be060350';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;
CREATE ROLE ubuntu;
ALTER ROLE ubuntu WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS;
CREATE ROLE xuancong;
ALTER ROLE xuancong WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;






\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4
-- Dumped by pg_dump version 11.4

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
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4
-- Dumped by pg_dump version 11.4

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
-- Name: beiweproject; Type: DATABASE; Schema: -; Owner: ubuntu
--

CREATE DATABASE beiweproject WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE beiweproject OWNER TO ubuntu;

\connect beiweproject

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

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: database_chunkregistry; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_chunkregistry (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    is_chunkable boolean NOT NULL,
    chunk_path character varying(256) NOT NULL,
    chunk_hash character varying(25) NOT NULL,
    data_type character varying(32) NOT NULL,
    time_bin timestamp with time zone NOT NULL,
    participant_id integer NOT NULL,
    study_id integer NOT NULL,
    survey_id integer,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_chunkregistry OWNER TO beiweuser;

--
-- Name: database_chunkregistry_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_chunkregistry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_chunkregistry_id_seq OWNER TO beiweuser;

--
-- Name: database_chunkregistry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_chunkregistry_id_seq OWNED BY public.database_chunkregistry.id;


--
-- Name: database_decryptionkeyerror; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_decryptionkeyerror (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    file_path character varying(256) NOT NULL,
    contents text NOT NULL,
    participant_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_decryptionkeyerror OWNER TO beiweuser;

--
-- Name: database_decryptionkeyerror_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_decryptionkeyerror_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_decryptionkeyerror_id_seq OWNER TO beiweuser;

--
-- Name: database_decryptionkeyerror_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_decryptionkeyerror_id_seq OWNED BY public.database_decryptionkeyerror.id;


--
-- Name: database_devicesettings; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_devicesettings (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    accelerometer boolean NOT NULL,
    gps boolean NOT NULL,
    calls boolean NOT NULL,
    texts boolean NOT NULL,
    wifi boolean NOT NULL,
    bluetooth boolean NOT NULL,
    power_state boolean NOT NULL,
    proximity boolean NOT NULL,
    gyro boolean NOT NULL,
    magnetometer boolean NOT NULL,
    steps boolean NOT NULL,
    devicemotion boolean NOT NULL,
    reachability boolean NOT NULL,
    allow_upload_over_cellular_data boolean NOT NULL,
    accelerometer_off_duration_seconds integer NOT NULL,
    accelerometer_on_duration_seconds integer NOT NULL,
    bluetooth_on_duration_seconds integer NOT NULL,
    bluetooth_total_duration_seconds integer NOT NULL,
    bluetooth_global_offset_seconds integer NOT NULL,
    check_for_new_surveys_frequency_seconds integer NOT NULL,
    create_new_data_files_frequency_seconds integer NOT NULL,
    gps_off_duration_seconds integer NOT NULL,
    gps_on_duration_seconds integer NOT NULL,
    seconds_before_auto_logout integer NOT NULL,
    upload_data_files_frequency_seconds integer NOT NULL,
    voice_recording_max_time_length_seconds integer NOT NULL,
    wifi_log_frequency_seconds integer NOT NULL,
    gyro_off_duration_seconds integer NOT NULL,
    gyro_on_duration_seconds integer NOT NULL,
    magnetometer_off_duration_seconds integer NOT NULL,
    magnetometer_on_duration_seconds integer NOT NULL,
    steps_off_duration_seconds integer NOT NULL,
    steps_on_duration_seconds integer NOT NULL,
    devicemotion_off_duration_seconds integer NOT NULL,
    devicemotion_on_duration_seconds integer NOT NULL,
    about_page_text text NOT NULL,
    call_clinician_button_text text NOT NULL,
    consent_form_text text,
    survey_submit_success_toast_text text NOT NULL,
    consent_sections text NOT NULL,
    study_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    ambientlight boolean DEFAULT false,
    ambientlight_interval_seconds integer DEFAULT 60,
    taps boolean DEFAULT false,
    accessibility boolean DEFAULT false,
    usage boolean DEFAULT false,
    usage_update_interval_seconds integer DEFAULT 1800,
    use_anonymized_hashing boolean DEFAULT false,
    phone_number_length integer DEFAULT 8,
    primary_care text,
    use_gps_fuzzing boolean DEFAULT false,
    write_buffer_size integer DEFAULT 0,
    CONSTRAINT database_devicesettings_accelerometer_off_duration_second_check CHECK ((accelerometer_off_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_accelerometer_on_duration_seconds_check CHECK ((accelerometer_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_bluetooth_global_offset_seconds_check CHECK ((bluetooth_global_offset_seconds >= 0)),
    CONSTRAINT database_devicesettings_bluetooth_on_duration_seconds_check CHECK ((bluetooth_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_bluetooth_total_duration_seconds_check CHECK ((bluetooth_total_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_check_for_new_surveys_frequency_s_check CHECK ((check_for_new_surveys_frequency_seconds >= 0)),
    CONSTRAINT database_devicesettings_create_new_data_files_frequency_s_check CHECK ((create_new_data_files_frequency_seconds >= 0)),
    CONSTRAINT database_devicesettings_devicemotion_off_duration_seconds_check CHECK ((devicemotion_off_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_devicemotion_on_duration_seconds_check CHECK ((devicemotion_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_gps_off_duration_seconds_check CHECK ((gps_off_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_gps_on_duration_seconds_check CHECK ((gps_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_gyro_off_duration_seconds_check CHECK ((gyro_off_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_gyro_on_duration_seconds_check CHECK ((gyro_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_magnetometer_off_duration_seconds_check CHECK ((magnetometer_off_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_magnetometer_on_duration_seconds_check CHECK ((magnetometer_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_steps_off_duration_seconds_check CHECK ((steps_off_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_steps_on_duration_seconds_check CHECK ((steps_on_duration_seconds >= 0)),
    CONSTRAINT database_devicesettings_seconds_before_auto_logout_check CHECK ((seconds_before_auto_logout >= 0)),
    CONSTRAINT database_devicesettings_upload_data_files_frequency_secon_check CHECK ((upload_data_files_frequency_seconds >= 0)),
    CONSTRAINT database_devicesettings_voice_recording_max_time_length_s_check CHECK ((voice_recording_max_time_length_seconds >= 0)),
    CONSTRAINT database_devicesettings_wifi_log_frequency_seconds_check CHECK ((wifi_log_frequency_seconds >= 0))
);


ALTER TABLE public.database_devicesettings OWNER TO beiweuser;

--
-- Name: database_devicesettings_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_devicesettings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_devicesettings_id_seq OWNER TO beiweuser;

--
-- Name: database_devicesettings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_devicesettings_id_seq OWNED BY public.database_devicesettings.id;


--
-- Name: database_encryptionerrormetadata; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_encryptionerrormetadata (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    file_name character varying(256) NOT NULL,
    total_lines integer NOT NULL,
    number_errors integer NOT NULL,
    errors_lines text NOT NULL,
    error_types text NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    CONSTRAINT database_encryptionerrormetadata_number_errors_check CHECK ((number_errors >= 0)),
    CONSTRAINT database_encryptionerrormetadata_total_lines_check CHECK ((total_lines >= 0))
);


ALTER TABLE public.database_encryptionerrormetadata OWNER TO beiweuser;

--
-- Name: database_encryptionerrormetadata_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_encryptionerrormetadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_encryptionerrormetadata_id_seq OWNER TO beiweuser;

--
-- Name: database_encryptionerrormetadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_encryptionerrormetadata_id_seq OWNED BY public.database_encryptionerrormetadata.id;


--
-- Name: database_fileprocesslock; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_fileprocesslock (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    lock_time timestamp with time zone,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_fileprocesslock OWNER TO beiweuser;

--
-- Name: database_fileprocesslock_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_fileprocesslock_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_fileprocesslock_id_seq OWNER TO beiweuser;

--
-- Name: database_fileprocesslock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_fileprocesslock_id_seq OWNED BY public.database_fileprocesslock.id;


--
-- Name: database_filetoprocess; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_filetoprocess (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    s3_file_path character varying(256) NOT NULL,
    participant_id integer NOT NULL,
    study_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_filetoprocess OWNER TO beiweuser;

--
-- Name: database_filetoprocess_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_filetoprocess_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_filetoprocess_id_seq OWNER TO beiweuser;

--
-- Name: database_filetoprocess_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_filetoprocess_id_seq OWNED BY public.database_filetoprocess.id;


--
-- Name: database_lineencryptionerror; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_lineencryptionerror (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    type character varying(32) NOT NULL,
    line text NOT NULL,
    base64_decryption_key character varying(256) NOT NULL,
    prev_line text NOT NULL,
    next_line text NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_lineencryptionerror OWNER TO beiweuser;

--
-- Name: database_lineencryptionerror_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_lineencryptionerror_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_lineencryptionerror_id_seq OWNER TO beiweuser;

--
-- Name: database_lineencryptionerror_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_lineencryptionerror_id_seq OWNED BY public.database_lineencryptionerror.id;


--
-- Name: database_participant; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_participant (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    password character varying(44) NOT NULL,
    salt character varying(24) NOT NULL,
    patient_id character varying(8) NOT NULL,
    device_id character varying(256) NOT NULL,
    os_type character varying(16) NOT NULL,
    study_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    os_desc character varying(64)
);


ALTER TABLE public.database_participant OWNER TO beiweuser;

--
-- Name: database_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_participant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_participant_id_seq OWNER TO beiweuser;

--
-- Name: database_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_participant_id_seq OWNED BY public.database_participant.id;


--
-- Name: database_pipelineupload; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_pipelineupload (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    object_id character varying(24) NOT NULL,
    file_name text NOT NULL,
    s3_path text NOT NULL,
    file_hash character varying(128) NOT NULL,
    study_id integer NOT NULL
);


ALTER TABLE public.database_pipelineupload OWNER TO beiweuser;

--
-- Name: database_pipelineupload_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_pipelineupload_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_pipelineupload_id_seq OWNER TO beiweuser;

--
-- Name: database_pipelineupload_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_pipelineupload_id_seq OWNED BY public.database_pipelineupload.id;


--
-- Name: database_pipelineuploadtags; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_pipelineuploadtags (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    tag text NOT NULL,
    pipeline_upload_id integer NOT NULL
);


ALTER TABLE public.database_pipelineuploadtags OWNER TO beiweuser;

--
-- Name: database_pipelineuploadtags_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_pipelineuploadtags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_pipelineuploadtags_id_seq OWNER TO beiweuser;

--
-- Name: database_pipelineuploadtags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_pipelineuploadtags_id_seq OWNED BY public.database_pipelineuploadtags.id;


--
-- Name: database_researcher; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_researcher (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    password character varying(44) NOT NULL,
    salt character varying(24) NOT NULL,
    username character varying(32) NOT NULL,
    admin boolean NOT NULL,
    access_key_id character varying(64),
    access_key_secret character varying(44) NOT NULL,
    access_key_secret_salt character varying(24) NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_researcher OWNER TO beiweuser;

--
-- Name: database_researcher_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_researcher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_researcher_id_seq OWNER TO beiweuser;

--
-- Name: database_researcher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_researcher_id_seq OWNED BY public.database_researcher.id;


--
-- Name: database_researcher_studies; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_researcher_studies (
    id integer NOT NULL,
    researcher_id integer NOT NULL,
    study_id integer NOT NULL
);


ALTER TABLE public.database_researcher_studies OWNER TO beiweuser;

--
-- Name: database_researcher_studies_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_researcher_studies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_researcher_studies_id_seq OWNER TO beiweuser;

--
-- Name: database_researcher_studies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_researcher_studies_id_seq OWNED BY public.database_researcher_studies.id;


--
-- Name: database_study; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_study (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    name text NOT NULL,
    encryption_key character varying(32) NOT NULL,
    object_id character varying(24) NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    is_test boolean NOT NULL
);


ALTER TABLE public.database_study OWNER TO beiweuser;

--
-- Name: database_study_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_study_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_study_id_seq OWNER TO beiweuser;

--
-- Name: database_study_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_study_id_seq OWNED BY public.database_study.id;


--
-- Name: database_survey; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_survey (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    content text NOT NULL,
    survey_type character varying(16) NOT NULL,
    settings text NOT NULL,
    timings text NOT NULL,
    last_modified timestamp with time zone NOT NULL,
    object_id character varying(24) NOT NULL,
    study_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_survey OWNER TO beiweuser;

--
-- Name: database_survey_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_survey_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_survey_id_seq OWNER TO beiweuser;

--
-- Name: database_survey_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_survey_id_seq OWNED BY public.database_survey.id;


--
-- Name: database_surveyarchive; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_surveyarchive (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    content text NOT NULL,
    survey_type character varying(16) NOT NULL,
    settings text NOT NULL,
    timings text NOT NULL,
    archive_start timestamp with time zone NOT NULL,
    archive_end timestamp with time zone NOT NULL,
    study_id integer NOT NULL,
    survey_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.database_surveyarchive OWNER TO beiweuser;

--
-- Name: database_surveyarchive_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_surveyarchive_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_surveyarchive_id_seq OWNER TO beiweuser;

--
-- Name: database_surveyarchive_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_surveyarchive_id_seq OWNED BY public.database_surveyarchive.id;


--
-- Name: database_uploadtracking; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.database_uploadtracking (
    id integer NOT NULL,
    deleted boolean NOT NULL,
    file_path character varying(256) NOT NULL,
    file_size integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    participant_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    CONSTRAINT database_uploadtracking_file_size_check CHECK ((file_size >= 0))
);


ALTER TABLE public.database_uploadtracking OWNER TO beiweuser;

--
-- Name: database_uploadtracking_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.database_uploadtracking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_uploadtracking_id_seq OWNER TO beiweuser;

--
-- Name: database_uploadtracking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.database_uploadtracking_id_seq OWNED BY public.database_uploadtracking.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: beiweuser
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO beiweuser;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: beiweuser
--

CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO beiweuser;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: beiweuser
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: database_chunkregistry id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_chunkregistry ALTER COLUMN id SET DEFAULT nextval('public.database_chunkregistry_id_seq'::regclass);


--
-- Name: database_decryptionkeyerror id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_decryptionkeyerror ALTER COLUMN id SET DEFAULT nextval('public.database_decryptionkeyerror_id_seq'::regclass);


--
-- Name: database_devicesettings id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_devicesettings ALTER COLUMN id SET DEFAULT nextval('public.database_devicesettings_id_seq'::regclass);


--
-- Name: database_encryptionerrormetadata id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_encryptionerrormetadata ALTER COLUMN id SET DEFAULT nextval('public.database_encryptionerrormetadata_id_seq'::regclass);


--
-- Name: database_fileprocesslock id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_fileprocesslock ALTER COLUMN id SET DEFAULT nextval('public.database_fileprocesslock_id_seq'::regclass);


--
-- Name: database_filetoprocess id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_filetoprocess ALTER COLUMN id SET DEFAULT nextval('public.database_filetoprocess_id_seq'::regclass);


--
-- Name: database_lineencryptionerror id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_lineencryptionerror ALTER COLUMN id SET DEFAULT nextval('public.database_lineencryptionerror_id_seq'::regclass);


--
-- Name: database_participant id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_participant ALTER COLUMN id SET DEFAULT nextval('public.database_participant_id_seq'::regclass);


--
-- Name: database_pipelineupload id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineupload ALTER COLUMN id SET DEFAULT nextval('public.database_pipelineupload_id_seq'::regclass);


--
-- Name: database_pipelineuploadtags id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineuploadtags ALTER COLUMN id SET DEFAULT nextval('public.database_pipelineuploadtags_id_seq'::regclass);


--
-- Name: database_researcher id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher ALTER COLUMN id SET DEFAULT nextval('public.database_researcher_id_seq'::regclass);


--
-- Name: database_researcher_studies id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher_studies ALTER COLUMN id SET DEFAULT nextval('public.database_researcher_studies_id_seq'::regclass);


--
-- Name: database_study id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_study ALTER COLUMN id SET DEFAULT nextval('public.database_study_id_seq'::regclass);


--
-- Name: database_survey id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_survey ALTER COLUMN id SET DEFAULT nextval('public.database_survey_id_seq'::regclass);


--
-- Name: database_surveyarchive id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_surveyarchive ALTER COLUMN id SET DEFAULT nextval('public.database_surveyarchive_id_seq'::regclass);


--
-- Name: database_uploadtracking id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_uploadtracking ALTER COLUMN id SET DEFAULT nextval('public.database_uploadtracking_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Data for Name: database_chunkregistry; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_chunkregistry (id, deleted, is_chunkable, chunk_path, chunk_hash, data_type, time_bin, participant_id, study_id, survey_id, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_decryptionkeyerror; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_decryptionkeyerror (id, deleted, file_path, contents, participant_id, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_devicesettings; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_devicesettings (id, deleted, accelerometer, gps, calls, texts, wifi, bluetooth, power_state, proximity, gyro, magnetometer, steps, devicemotion, reachability, allow_upload_over_cellular_data, accelerometer_off_duration_seconds, accelerometer_on_duration_seconds, bluetooth_on_duration_seconds, bluetooth_total_duration_seconds, bluetooth_global_offset_seconds, check_for_new_surveys_frequency_seconds, create_new_data_files_frequency_seconds, gps_off_duration_seconds, gps_on_duration_seconds, seconds_before_auto_logout, upload_data_files_frequency_seconds, voice_recording_max_time_length_seconds, wifi_log_frequency_seconds, gyro_off_duration_seconds, gyro_on_duration_seconds, magnetometer_off_duration_seconds, magnetometer_on_duration_seconds, steps_off_duration_seconds, steps_on_duration_seconds, devicemotion_off_duration_seconds, devicemotion_on_duration_seconds, about_page_text, call_clinician_button_text, consent_form_text, survey_submit_success_toast_text, consent_sections, study_id, created_on, last_updated, ambientlight, ambientlight_interval_seconds, taps, accessibility, usage, usage_update_interval_seconds, use_anonymized_hashing, phone_number_length, primary_care, use_gps_fuzzing, write_buffer_size) FROM stdin;
\.


--
-- Data for Name: database_encryptionerrormetadata; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_encryptionerrormetadata (id, deleted, file_name, total_lines, number_errors, errors_lines, error_types, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_fileprocesslock; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_fileprocesslock (id, deleted, lock_time, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_filetoprocess; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_filetoprocess (id, deleted, s3_file_path, participant_id, study_id, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_lineencryptionerror; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_lineencryptionerror (id, deleted, type, line, base64_decryption_key, prev_line, next_line, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_participant; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_participant (id, deleted, password, salt, patient_id, device_id, os_type, study_id, created_on, last_updated, os_desc) FROM stdin;
\.


--
-- Data for Name: database_pipelineupload; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_pipelineupload (id, deleted, created_on, last_updated, object_id, file_name, s3_path, file_hash, study_id) FROM stdin;
\.


--
-- Data for Name: database_pipelineuploadtags; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_pipelineuploadtags (id, deleted, created_on, last_updated, tag, pipeline_upload_id) FROM stdin;
\.


--
-- Data for Name: database_researcher; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_researcher (id, deleted, password, salt, username, admin, access_key_id, access_key_secret, access_key_secret_salt, created_on, last_updated) FROM stdin;
1	f	3GTRHIxOIAu3PEpEWU9bzmcnUdaJXH0hc4uAhb6b9oo=	owtGu2zrpsUfuRMKYg2fuQ==	default_admin	t	7WygtO6TsauK68POQ+feoYbHW2bmbte/LW3zBkg+7s4gmUlbRBQ0R8fUYOY1SdFn	A9rbE33Gp6186_hpdg8uN9x8xb8uhC9RTl05WOlP6tk=	d7NFb4yzPHWhBovlnWAYaw==	2018-04-18 06:39:46.899276+08	2018-04-18 06:39:46.899297+08
2	f	M3Adu5VJxvWQcslITNu7IkGO2qWJtLnJUFdVYx867Gg=	e-LsJn96qKjkDbr_bSUJ-Q==	admin	t	O38g6n8DDKNQEAyo7tDNfqHeJis4bGd7+3bfGjOur+q+7tq4+TcMoAIx0PyS5QT0	9xrBozUxywT95bQMaqcXLw-cJRjcKXBlE7d0-r33OVE=	0oaSi2a0iiW8dtFbPEflqA==	2018-04-18 06:39:47.271762+08	2019-04-16 14:42:41.11583+08
3	f	i6_h4yysMfD9CzxLbE4PBg0ig3ll6b2jPG1b0dq-NjA=	n5UyH3TnkbtXRoTzKzgZ-A==	moht	f	YwLlSgeaJnjnaQ93JjDg8URPp2cnMhL9JkfvJ14Z6Not/fQAiPEVEX49Vowc3sFX	Pvg0XK5wyjcVHoQjCc0EZWlQNvJ3f5OQnSanHY-vdWc=	PQ02MNRWXrsgaZ3sti7coQ==	2019-04-18 10:56:44.566906+08	2019-04-18 10:56:44.573314+08
4	f	Akfq3r_H1UUqRHxvnzLQefn7OPXklGpWWqd1qZ7UDXs=	9bkni_1i0x90qTvBMlqEpw==	testadmin	f	2TfErADgm25qm/hSt8k4XUNLsfK6VDArZ4rE+y1qwgNKcJLrR/lmCvwCLTHSlsvd	KCzbwNEzSlN19D_LXZuA2KMtKVhG-JkqLtNyKXXg_S0=	_E2EkXI4kYXgCZjHWxcRug==	2019-06-11 16:18:57.136294+08	2019-06-11 16:18:57.160291+08
\.


--
-- Data for Name: database_researcher_studies; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_researcher_studies (id, researcher_id, study_id) FROM stdin;
\.


--
-- Data for Name: database_study; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_study (id, deleted, name, encryption_key, object_id, created_on, last_updated, is_test) FROM stdin;
1	f	test01	12345678901234567890123456789012	1JxL3ITDi77X2414qZ5fLYla	2019-04-16 14:44:40.936034+08	2019-04-16 14:44:40.936064+08	t
2	f	test02	12345678901234567890123456789012	WsALPJQJp11m8qxQl23Huufh	2019-06-11 16:21:25.869912+08	2019-06-11 16:21:25.869936+08	t
\.


--
-- Data for Name: database_survey; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_survey (id, deleted, content, survey_type, settings, timings, last_modified, object_id, study_id, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_surveyarchive; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_surveyarchive (id, deleted, content, survey_type, settings, timings, archive_start, archive_end, study_id, survey_id, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: database_uploadtracking; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.database_uploadtracking (id, deleted, file_path, file_size, "timestamp", participant_id, created_on, last_updated) FROM stdin;
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: beiweuser
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
\.


--
-- Name: database_chunkregistry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_chunkregistry_id_seq', 1, false);


--
-- Name: database_decryptionkeyerror_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_decryptionkeyerror_id_seq', 1, false);


--
-- Name: database_devicesettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_devicesettings_id_seq', 2, true);


--
-- Name: database_encryptionerrormetadata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_encryptionerrormetadata_id_seq', 6, true);


--
-- Name: database_fileprocesslock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_fileprocesslock_id_seq', 182, true);


--
-- Name: database_filetoprocess_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_filetoprocess_id_seq', 28332, true);


--
-- Name: database_lineencryptionerror_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_lineencryptionerror_id_seq', 1, false);


--
-- Name: database_participant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_participant_id_seq', 13, true);


--
-- Name: database_pipelineupload_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_pipelineupload_id_seq', 1, false);


--
-- Name: database_pipelineuploadtags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_pipelineuploadtags_id_seq', 1, false);


--
-- Name: database_researcher_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_researcher_id_seq', 4, true);


--
-- Name: database_researcher_studies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_researcher_studies_id_seq', 3, true);


--
-- Name: database_study_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_study_id_seq', 2, true);


--
-- Name: database_survey_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_survey_id_seq', 1, false);


--
-- Name: database_surveyarchive_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_surveyarchive_id_seq', 1, false);


--
-- Name: database_uploadtracking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.database_uploadtracking_id_seq', 28089, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: beiweuser
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 7, true);


--
-- Name: database_chunkregistry database_chunkregistry_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_chunkregistry
    ADD CONSTRAINT database_chunkregistry_pkey PRIMARY KEY (id);


--
-- Name: database_decryptionkeyerror database_decryptionkeyerror_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_decryptionkeyerror
    ADD CONSTRAINT database_decryptionkeyerror_pkey PRIMARY KEY (id);


--
-- Name: database_devicesettings database_devicesettings_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_devicesettings
    ADD CONSTRAINT database_devicesettings_pkey PRIMARY KEY (id);


--
-- Name: database_devicesettings database_devicesettings_study_id_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_devicesettings
    ADD CONSTRAINT database_devicesettings_study_id_key UNIQUE (study_id);


--
-- Name: database_encryptionerrormetadata database_encryptionerrormetadata_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_encryptionerrormetadata
    ADD CONSTRAINT database_encryptionerrormetadata_pkey PRIMARY KEY (id);


--
-- Name: database_fileprocesslock database_fileprocesslock_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_fileprocesslock
    ADD CONSTRAINT database_fileprocesslock_pkey PRIMARY KEY (id);


--
-- Name: database_filetoprocess database_filetoprocess_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_filetoprocess
    ADD CONSTRAINT database_filetoprocess_pkey PRIMARY KEY (id);


--
-- Name: database_lineencryptionerror database_lineencryptionerror_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_lineencryptionerror
    ADD CONSTRAINT database_lineencryptionerror_pkey PRIMARY KEY (id);


--
-- Name: database_participant database_participant_patient_id_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_participant
    ADD CONSTRAINT database_participant_patient_id_key UNIQUE (patient_id);


--
-- Name: database_participant database_participant_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_participant
    ADD CONSTRAINT database_participant_pkey PRIMARY KEY (id);


--
-- Name: database_pipelineupload database_pipelineupload_object_id_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineupload
    ADD CONSTRAINT database_pipelineupload_object_id_key UNIQUE (object_id);


--
-- Name: database_pipelineupload database_pipelineupload_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineupload
    ADD CONSTRAINT database_pipelineupload_pkey PRIMARY KEY (id);


--
-- Name: database_pipelineuploadtags database_pipelineuploadtags_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineuploadtags
    ADD CONSTRAINT database_pipelineuploadtags_pkey PRIMARY KEY (id);


--
-- Name: database_researcher database_researcher_access_key_id_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher
    ADD CONSTRAINT database_researcher_access_key_id_key UNIQUE (access_key_id);


--
-- Name: database_researcher database_researcher_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher
    ADD CONSTRAINT database_researcher_pkey PRIMARY KEY (id);


--
-- Name: database_researcher_studies database_researcher_stud_researcher_id_study_id_8b2bd313_uniq; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher_studies
    ADD CONSTRAINT database_researcher_stud_researcher_id_study_id_8b2bd313_uniq UNIQUE (researcher_id, study_id);


--
-- Name: database_researcher_studies database_researcher_studies_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher_studies
    ADD CONSTRAINT database_researcher_studies_pkey PRIMARY KEY (id);


--
-- Name: database_researcher database_researcher_username_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher
    ADD CONSTRAINT database_researcher_username_key UNIQUE (username);


--
-- Name: database_study database_study_name_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_study
    ADD CONSTRAINT database_study_name_key UNIQUE (name);


--
-- Name: database_study database_study_object_id_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_study
    ADD CONSTRAINT database_study_object_id_key UNIQUE (object_id);


--
-- Name: database_study database_study_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_study
    ADD CONSTRAINT database_study_pkey PRIMARY KEY (id);


--
-- Name: database_survey database_survey_object_id_key; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_survey
    ADD CONSTRAINT database_survey_object_id_key UNIQUE (object_id);


--
-- Name: database_survey database_survey_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_survey
    ADD CONSTRAINT database_survey_pkey PRIMARY KEY (id);


--
-- Name: database_surveyarchive database_surveyarchive_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_surveyarchive
    ADD CONSTRAINT database_surveyarchive_pkey PRIMARY KEY (id);


--
-- Name: database_uploadtracking database_uploadtracking_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_uploadtracking
    ADD CONSTRAINT database_uploadtracking_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: database_chunkregistry_participant_id_86ed17cf; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_chunkregistry_participant_id_86ed17cf ON public.database_chunkregistry USING btree (participant_id);


--
-- Name: database_chunkregistry_study_id_02c441c3; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_chunkregistry_study_id_02c441c3 ON public.database_chunkregistry USING btree (study_id);


--
-- Name: database_chunkregistry_survey_id_6d3ed776; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_chunkregistry_survey_id_6d3ed776 ON public.database_chunkregistry USING btree (survey_id);


--
-- Name: database_decryptionkeyerror_participant_id_820ee4b8; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_decryptionkeyerror_participant_id_820ee4b8 ON public.database_decryptionkeyerror USING btree (participant_id);


--
-- Name: database_filetoprocess_participant_id_58eb91cf; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_filetoprocess_participant_id_58eb91cf ON public.database_filetoprocess USING btree (participant_id);


--
-- Name: database_filetoprocess_study_id_bde5df71; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_filetoprocess_study_id_bde5df71 ON public.database_filetoprocess USING btree (study_id);


--
-- Name: database_participant_patient_id_6acaeab5_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_participant_patient_id_6acaeab5_like ON public.database_participant USING btree (patient_id varchar_pattern_ops);


--
-- Name: database_participant_study_id_8a79528b; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_participant_study_id_8a79528b ON public.database_participant USING btree (study_id);


--
-- Name: database_pipelineupload_object_id_c49fb769_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_pipelineupload_object_id_c49fb769_like ON public.database_pipelineupload USING btree (object_id varchar_pattern_ops);


--
-- Name: database_pipelineupload_study_id_03446ed9; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_pipelineupload_study_id_03446ed9 ON public.database_pipelineupload USING btree (study_id);


--
-- Name: database_pipelineuploadtags_pipeline_upload_id_930237e0; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_pipelineuploadtags_pipeline_upload_id_930237e0 ON public.database_pipelineuploadtags USING btree (pipeline_upload_id);


--
-- Name: database_researcher_access_key_id_85b1e779_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_researcher_access_key_id_85b1e779_like ON public.database_researcher USING btree (access_key_id varchar_pattern_ops);


--
-- Name: database_researcher_studies_researcher_id_d50f7b28; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_researcher_studies_researcher_id_d50f7b28 ON public.database_researcher_studies USING btree (researcher_id);


--
-- Name: database_researcher_studies_study_id_c9b031c0; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_researcher_studies_study_id_c9b031c0 ON public.database_researcher_studies USING btree (study_id);


--
-- Name: database_researcher_username_b31dab38_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_researcher_username_b31dab38_like ON public.database_researcher USING btree (username varchar_pattern_ops);


--
-- Name: database_study_name_155b14db_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_study_name_155b14db_like ON public.database_study USING btree (name text_pattern_ops);


--
-- Name: database_study_object_id_be2f81fa_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_study_object_id_be2f81fa_like ON public.database_study USING btree (object_id varchar_pattern_ops);


--
-- Name: database_survey_object_id_ad7ce4cb_like; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_survey_object_id_ad7ce4cb_like ON public.database_survey USING btree (object_id varchar_pattern_ops);


--
-- Name: database_survey_study_id_bc7ed043; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_survey_study_id_bc7ed043 ON public.database_survey USING btree (study_id);


--
-- Name: database_surveyarchive_study_id_960cf592; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_surveyarchive_study_id_960cf592 ON public.database_surveyarchive USING btree (study_id);


--
-- Name: database_surveyarchive_survey_id_9b38709e; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_surveyarchive_survey_id_9b38709e ON public.database_surveyarchive USING btree (survey_id);


--
-- Name: database_uploadtracking_participant_id_f6783799; Type: INDEX; Schema: public; Owner: beiweuser
--

CREATE INDEX database_uploadtracking_participant_id_f6783799 ON public.database_uploadtracking USING btree (participant_id);


--
-- Name: database_chunkregistry database_chunkregist_participant_id_86ed17cf_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_chunkregistry
    ADD CONSTRAINT database_chunkregist_participant_id_86ed17cf_fk_database_ FOREIGN KEY (participant_id) REFERENCES public.database_participant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_chunkregistry database_chunkregistry_study_id_02c441c3_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_chunkregistry
    ADD CONSTRAINT database_chunkregistry_study_id_02c441c3_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_chunkregistry database_chunkregistry_survey_id_6d3ed776_fk_database_survey_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_chunkregistry
    ADD CONSTRAINT database_chunkregistry_survey_id_6d3ed776_fk_database_survey_id FOREIGN KEY (survey_id) REFERENCES public.database_survey(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_decryptionkeyerror database_decryptionk_participant_id_820ee4b8_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_decryptionkeyerror
    ADD CONSTRAINT database_decryptionk_participant_id_820ee4b8_fk_database_ FOREIGN KEY (participant_id) REFERENCES public.database_participant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_devicesettings database_devicesettings_study_id_5967a5af_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_devicesettings
    ADD CONSTRAINT database_devicesettings_study_id_5967a5af_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_filetoprocess database_filetoproce_participant_id_58eb91cf_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_filetoprocess
    ADD CONSTRAINT database_filetoproce_participant_id_58eb91cf_fk_database_ FOREIGN KEY (participant_id) REFERENCES public.database_participant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_filetoprocess database_filetoprocess_study_id_bde5df71_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_filetoprocess
    ADD CONSTRAINT database_filetoprocess_study_id_bde5df71_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_participant database_participant_study_id_8a79528b_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_participant
    ADD CONSTRAINT database_participant_study_id_8a79528b_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_pipelineuploadtags database_pipelineupl_pipeline_upload_id_930237e0_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineuploadtags
    ADD CONSTRAINT database_pipelineupl_pipeline_upload_id_930237e0_fk_database_ FOREIGN KEY (pipeline_upload_id) REFERENCES public.database_pipelineupload(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_pipelineupload database_pipelineupload_study_id_03446ed9_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_pipelineupload
    ADD CONSTRAINT database_pipelineupload_study_id_03446ed9_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_researcher_studies database_researcher__researcher_id_d50f7b28_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher_studies
    ADD CONSTRAINT database_researcher__researcher_id_d50f7b28_fk_database_ FOREIGN KEY (researcher_id) REFERENCES public.database_researcher(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_researcher_studies database_researcher__study_id_c9b031c0_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_researcher_studies
    ADD CONSTRAINT database_researcher__study_id_c9b031c0_fk_database_ FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_survey database_survey_study_id_bc7ed043_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_survey
    ADD CONSTRAINT database_survey_study_id_bc7ed043_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_surveyarchive database_surveyarchive_study_id_960cf592_fk_database_study_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_surveyarchive
    ADD CONSTRAINT database_surveyarchive_study_id_960cf592_fk_database_study_id FOREIGN KEY (study_id) REFERENCES public.database_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_surveyarchive database_surveyarchive_survey_id_9b38709e_fk_database_survey_id; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_surveyarchive
    ADD CONSTRAINT database_surveyarchive_survey_id_9b38709e_fk_database_survey_id FOREIGN KEY (survey_id) REFERENCES public.database_survey(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: database_uploadtracking database_uploadtrack_participant_id_f6783799_fk_database_; Type: FK CONSTRAINT; Schema: public; Owner: beiweuser
--

ALTER TABLE ONLY public.database_uploadtracking
    ADD CONSTRAINT database_uploadtrack_participant_id_f6783799_fk_database_ FOREIGN KEY (participant_id) REFERENCES public.database_participant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: DATABASE beiweproject; Type: ACL; Schema: -; Owner: ubuntu
--

GRANT ALL ON DATABASE beiweproject TO beiweuser;


--
-- PostgreSQL database dump complete
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4
-- Dumped by pg_dump version 11.4

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
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4
-- Dumped by pg_dump version 11.4

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
-- Name: ubuntu; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE ubuntu WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE ubuntu OWNER TO postgres;

\connect ubuntu

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
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

