"""
parse csv and save to db
"""
import logging
import pandas as pd
from models import CountBySchool
from database import session_factory

logger = logging.getLogger(__name__)


DEFAULT_FILE_PATH = "~/Desktop/admissions.xlsx"

YEARS = [2023, 2022, 2021]
CAMPUSES = ["ucb", "ucla", "uci", "ucd"]

SHEET_HEADER_TO_TABLE_COLUMNS = {
    "Calculation1": "na",
    "County/State/ Territory": "na",
    "School": "school",
    "City": "city",
    "Count": "count_type"
}


def read_file_to_list(file_path: str, sheet_name: str | int | None = 0) -> list[dict]:
    raw_df = pd.read_excel(
        io=file_path,
        sheet_name=sheet_name,
        header=0
    )
    raw_df.fillna(0, inplace=True)
    # pd.set_option('display.max_columns', None)
    # print(f'****** raw_df\n{raw_df}')
    records = raw_df.to_dict("records")
    # print(f'***** {records=}')
    return records


def save_file_to_db(file_path: str = DEFAULT_FILE_PATH) -> dict:
    results = {}
    with session_factory() as session:
        for yr in YEARS:
            for camp in CAMPUSES:
                sheet_name = f"{yr} {camp}"
                records = read_file_to_list(file_path=file_path, sheet_name=sheet_name)
                saved = 0
                for rec in records:
                    races = [_ for _ in rec.keys() if SHEET_HEADER_TO_TABLE_COLUMNS.get(_) is None]
                    for race in races:
                        try:
                            new_obj = CountBySchool(
                                year=yr,
                                campus=camp,
                                race=race,
                                count_type=rec.get("Count"),
                                count=rec.get(race, 0),
                                city=rec.get("City"),
                                school=rec.get("School")
                            )
                            session.add(new_obj)
                            session.commit()
                            saved += 1
                        except Exception as e:
                            logger.error(e)
                            session.rollback()

                results[sheet_name] = {"count": len(records), "saved": saved}

    return results


