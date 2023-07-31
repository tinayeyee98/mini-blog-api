"""Export MongoDB collections with Rention Policy.

The script will load .env file for runtime settings.
It will prepare query strings and then invokes mongodump command for the actual data backup.

IMPORTANT: The script only uses the db uri env var when connecting and working with the database i.e. db name is implicit.
"""

import dataclasses
import shlex
import subprocess
from datetime import date, datetime, time, timedelta
from os import environ
from pathlib import Path
from typing import List, NamedTuple, Optional

import bson.json_util  # type: ignore
import pymongo  # type: ignore
import pytz
import structlog
from bson import ObjectId  # type: ignore
from dotenv import load_dotenv
from pymongo.database import Database  # type: ignore
from pytz.tzfile import DstTzInfo
from rfc3339 import rfc3339  # type: ignore

# get env vars from .env file
load_dotenv()

# configure logging
# structlog.configure()
log = structlog.get_logger()


### settings ###

# defaults
DB_URI = "mongodb://localhost:27017/apms_status_db"
DB_RETENTION_DAYS = 1
DB_ARCHIVE_DAYS = 180
DB_BACKUP_DIR = "."


class Settings(NamedTuple):
    db_uri: str
    db_retention_days: int
    db_archive_days: int
    db_backup_dir: Path


def get_settings() -> Settings:
    settings = Settings(
        db_uri=environ.get("APMS_STATUS_DB_URI", DB_URI),
        db_retention_days=int(environ.get("DB_RETENTION_DAYS", DB_RETENTION_DAYS)),
        db_archive_days=int(environ.get("DB_ARCHIVE_DAYS", DB_ARCHIVE_DAYS)),
        db_backup_dir=Path(environ.get("DB_BACKUP_DIR", DB_BACKUP_DIR)),
    )
    return settings


### tz functions ###


def local_timezone() -> DstTzInfo:
    """Local timezone name.

    tay@vivobook:~/src$ ls -l /etc/localtime
    lrwxrwxrwx 1 root root 31 Mar 30 12:58 /etc/localtime -> /usr/share/zoneinfo/Asia/Yangon
    """
    localtime = Path("/etc/localtime")
    zone_info = localtime.resolve()
    zone_name = "/".join(zone_info.parts[-2:])
    return pytz.timezone(zone_name)


def retention_timestamp(
    retention_days: int = 1, tz: DstTzInfo = local_timezone(), utc: bool = True
):
    """Retention period = today + retention_days"""
    today = datetime.combine(date.today(), time.min)
    today_local = tz.localize(today)
    retention_local = today_local - timedelta(days=retention_days)
    if utc:
        return retention_local.astimezone(tz=pytz.utc)
    return retention_local


### db functions ###


@dataclasses.dataclass
class ProcessResult:
    out: Optional[bytes]
    err: Optional[bytes]
    returncode: int


def get_db(db_uri: str) -> Database:
    client = pymongo.MongoClient(db_uri)
    db = client.get_default_database()
    return db


def dump_db(
    db_uri: str, db_name: str, db_collection: str, query_filter: str, output_dir: str
) -> ProcessResult:
    mongodump_cmd = "mongodump --uri={db_uri} --db={db_name} --collection={db_collection} --query={query_filter} --out={output_dir} --gzip"
    cmd = mongodump_cmd.format(
        db_uri=shlex.quote(db_uri),
        db_name=db_name,
        db_collection=db_collection,
        query_filter=shlex.quote(query_filter),
        output_dir=shlex.quote(output_dir),
    )
    cmd_args: List[str] = shlex.split(cmd)
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    p.wait()
    r = ProcessResult(out=out, err=err, returncode=p.returncode)
    return r


def restore_db(db_uri: str, data_namespace: str, intput_dir: str):
    mongorestore_cmd = (
        "mongorestore --uri={db_uri} --nsInclude='{data_namespace}' --gzip {input_dir}"
    )
    cmd = mongorestore_cmd.format(
        db_uri=shlex.quote(db_uri),
        data_namespace=shlex.quote(data_namespace),
        input_dir=shlex.quote(intput_dir),
    )
    cmd_args: List[str] = shlex.split(cmd)
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    p.wait()
    r = ProcessResult(out=out, err=err, returncode=p.returncode)
    return r


## utility functions ##


class BackupMetadata(NamedTuple):
    start: datetime
    end: datetime
    description: str
    output_dir: Path


class BackupTask(NamedTuple):
    backup_start: datetime
    backup_end: datetime
    backup_task: str
    output_dir: Path


def generate_retention_tasks(
    start_time: datetime, num_days: int = 0, backup_dir: Path = Path(".")
):
    start = start_time
    backup = "retention-{backup_date}"

    for i in range(num_days + 1):
        end = start + timedelta(hours=24)
        dir = backup_dir.joinpath(
            Path(backup.format(backup_date=start.strftime("%Y%m%d")))
        )
        r = BackupTask(
            backup_start=start,
            backup_end=end,
            backup_task=f"retention-{i}",
            output_dir=dir,
        )
        yield r
        start = end


def generate_archive_tasks(
    start_time: datetime, num_days: int = 0, backup_dir: Path = Path(".")
):
    end = start_time
    backup = "archive-{archive_date}"

    for i in range(num_days):
        start = end - timedelta(hours=24)
        dir = backup_dir.joinpath(
            Path(backup.format(archive_date=start.strftime("%Y%m%d")))
        )
        a = BackupTask(
            backup_start=start,
            backup_end=end,
            backup_task=f"archive-{i}",
            output_dir=dir,
        )
        yield a
        end = start


settings: Settings = get_settings()


def main():
    tz: DstTzInfo = local_timezone()
    now: datetime = datetime.now(tz=tz)
    dir_format = "mongodump-{backup_timestamp}"
    backup_dir = settings.db_backup_dir / dir_format.format(
        backup_timestamp=now.strftime("%Y%m%d_%H%M%S")
    )

    db: Database = get_db(settings.db_uri)
    collection_names = db.list_collection_names()

    log.msg(
        "db connection established",
        name=db.name,
        collections=",".join(collection_names),
    )

    retention_cutoff: datetime = retention_timestamp(settings.db_retention_days, tz)
    log.msg(
        "starting db backup",
        retention_start=rfc3339(retention_cutoff),
        retention_days=settings.db_retention_days,
        backup_dir=str(backup_dir),
    )

    retention_backup = generate_retention_tasks(
        retention_cutoff, settings.db_retention_days, backup_dir
    )

    archive_backup = generate_archive_tasks(
        retention_cutoff, settings.db_archive_days, backup_dir
    )

    for r in retention_backup:
        subtask_id = 0
        for cn in collection_names:
            oid_range = {
                "_id": {
                    "$gte": ObjectId.from_datetime(r.backup_start),
                    "$lt": ObjectId.from_datetime(r.backup_end),
                }
            }
            p = dump_db(
                settings.db_uri,
                db.name,
                cn,
                bson.json_util.dumps(oid_range),
                str(r.output_dir.absolute()),
            )
            if p.returncode == 0:
                msg = "retention backup successful"
            else:
                msg = "retention backup failed"

            log.msg(
                msg,
                backup_start=rfc3339(r.backup_start),
                backup_end=rfc3339(r.backup_end),
                backup_task=f"{r.backup_task}-{subtask_id}",
                collection=cn,
                output_dir=str(r.output_dir.absolute()),
            )

    for a in archive_backup:
        subtask_id = 0
        for cn in collection_names:
            oid_range = {
                "_id": {
                    "$gte": ObjectId.from_datetime(a.backup_start),
                    "$lt": ObjectId.from_datetime(a.backup_end),
                }
            }
            p = dump_db(
                settings.db_uri,
                db.name,
                cn,
                bson.json_util.dumps(oid_range),
                str(a.output_dir.absolute()),
            )
            if p.returncode == 0:
                msg = "archive backup successful"
            else:
                msg = "archive backup failed"
            log.msg(
                msg,
                backup_start=rfc3339(a.backup_start),
                backup_end=rfc3339(a.backup_end),
                backup_task=f"{a.backup_task}-{subtask_id}",
                collection=cn,
                output_dir=str(a.output_dir.absolute()),
            )

    for cn in collection_names:
        db.drop_collection(cn)
        log.msg("dropped collection", db_name=db.name, collection_name=cn)

    retention_backup = generate_retention_tasks(
        retention_cutoff, settings.db_retention_days, backup_dir
    )

    for r in retention_backup:
        data_namespace = f"{db.name}.*"
        input_dir = r.output_dir.joinpath(Path(db.name))
        p = restore_db(settings.db_uri, data_namespace, str(input_dir.absolute()))
        if p.returncode == 0:
            msg = "backup restoration successful"
        else:
            msg = "backup restoration failed"
        log.msg(
            msg,
            data_namespace=data_namespace,
            restore_start=rfc3339(r.backup_start),
            restore_end=rfc3339(r.backup_end),
            restore_task=r.backup_task,
            backup_dir=str(input_dir.absolute()),
        )


if __name__ == "__main__":
    main()
