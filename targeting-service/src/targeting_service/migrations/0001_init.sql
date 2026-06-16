-- depends:
-- Initial schema for Targeting Service

CREATE TABLE IF NOT EXISTS recipient (
    id            uuid PRIMARY KEY,
    telegram_id   VARCHAR(255) NOT NULL UNIQUE,
    name          VARCHAR(255),
    type          VARCHAR(255) NOT NULL,
    is_admin      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by    VARCHAR(255),
    updated_by    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS distribution (
    id            uuid PRIMARY KEY,
    bmk_id        VARCHAR(255) NOT NULL UNIQUE,
    name          VARCHAR(255),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by    VARCHAR(255),
    updated_by    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS distribution_recipient (
    distribution_id uuid NOT NULL REFERENCES distribution(id) ON DELETE CASCADE,
    recipient_id    uuid NOT NULL REFERENCES recipient(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      VARCHAR(255),
    updated_by      VARCHAR(255),
    PRIMARY KEY (distribution_id, recipient_id)
);

CREATE INDEX IF NOT EXISTS idx_recipient_telegram_id ON recipient (telegram_id);
CREATE INDEX IF NOT EXISTS idx_distribution_bmk_id ON distribution (bmk_id);