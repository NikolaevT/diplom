-- depends: 0001_init

CREATE TABLE IF NOT EXISTS tag (
    id            uuid PRIMARY KEY,
    name          VARCHAR(255) NOT NULL UNIQUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL,
    created_by    VARCHAR(255),
    updated_by    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS distribution_tag (
    distribution_id uuid NOT NULL REFERENCES distribution(id) ON DELETE CASCADE,
    tag_id          uuid NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL,
    created_by      VARCHAR(255),
    updated_by      VARCHAR(255),
    PRIMARY KEY (distribution_id, tag_id)
);

CREATE TABLE IF NOT EXISTS recipient_tag (
    recipient_id uuid NOT NULL REFERENCES recipient(id) ON DELETE CASCADE,
    tag_id       uuid NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL,
    created_by   VARCHAR(255),
    updated_by   VARCHAR(255),
    PRIMARY KEY (recipient_id, tag_id)
);

ALTER TABLE distribution RENAME COLUMN bmk_id TO bmc_distribution_id; 
DROP TABLE IF EXISTS distribution_recipient;

