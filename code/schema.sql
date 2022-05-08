create table if not exists working_proxies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ip           integer,
    port         INTEGER,
    proxie_type    INTEGER
);

create table if not exists die_proxies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ip           int
);